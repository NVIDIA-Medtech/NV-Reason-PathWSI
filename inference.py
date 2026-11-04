# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: OpenMDW-1.1
"""Standalone NV-Reason-PathWSI inference on one pathology image (transformers backend).

Works with both packaged models:
  nvidia/NV-Reason-PathWSI-4B    (~9 GB, 1x GPU >= 24 GB)
  nvidia/NV-Reason-PathWSI-4B    (~51 GB, 1x 80 GB GPU or
                                                 multi-GPU with --device-map auto)

Examples:
  python inference.py --model nvidia/NV-Reason-PathWSI-4B \
      --image examples/sample_1.jpg \
      --prompt "Describe the histopathological features visible in this image."

  # Thinking mode (used by the reasoning benchmarks):
  python inference.py --model nvidia/NV-Reason-PathWSI-4B \
      --image examples/sample_1.jpg --prompt "..." --think
"""

import argparse
from pathlib import Path

import torch
from transformers import AutoModelForImageTextToText, AutoProcessor


DEFAULT_MODEL = "nvidia/NV-Reason-PathWSI-4B"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default="nvidia/NV-Reason-PathWSI-4B",
        help=f"Local model directory or Hugging Face model ID (default: {mid})",
    )
    parser.add_argument("--image", required=True, help="Path to a pathology image")
    parser.add_argument(
        "--prompt",
        default="Describe the histopathological features visible in this image.",
    )
    parser.add_argument(
        "--think",
        action="store_true",
        help="Enable thinking mode (default off; the reported benchmark numbers "
        "for MCQ-style tasks were measured with thinking off and greedy decoding)",
    )
    parser.add_argument("--max-new-tokens", type=int, default=2048)
    parser.add_argument(
        "--device-map",
        default=None,
        help="Optional device_map for from_pretrained (e.g. 'auto' to shard the "
        "27B model across several GPUs)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not Path(args.model).is_dir():
        raise SystemExit(f"model directory not found: {args.model}")
    if not Path(args.image).is_file():
        raise SystemExit(f"image not found: {args.image}")

    model = AutoModelForImageTextToText.from_pretrained(
        args.model,
        dtype=torch.bfloat16,
        device_map=args.device_map,
    ).eval()
    if args.device_map is None:
        model = model.to("cuda")
    processor = AutoProcessor.from_pretrained(args.model)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": args.image},
                {"type": "text", "text": args.prompt},
            ],
        }
    ]
    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=args.think,
    )
    inputs = processor(
        text=text,
        images=[args.image],
        return_tensors="pt",
    ).to(model.device)

    with torch.inference_mode():
        generated = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            use_cache=True,
        )

    new_tokens = generated[:, inputs.input_ids.shape[1]:]
    print(
        processor.batch_decode(
            new_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
    )


if __name__ == "__main__":
    main()

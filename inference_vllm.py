# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: OpenMDW-1.1
"""Batched NV-Reason-PathWSI inference with vLLM — matches the benchmark methodology.

This is the engine used to produce the reported benchmark numbers
(vLLM 0.19.0, greedy decoding, max_model_len 16384). Use it to
cross-verify scores on an independent machine.

Input: a JSONL file where each line is {"image": "<path>", "prompt": "<text>"}
        (extra fields are copied through to the output).
Output: the same records plus {"response": "<generated text>"}.

Example:
  python inference_vllm.py \
      --model nvidia/NV-Reason-PathWSI \
      --input queries.jsonl --output responses.jsonl
"""

import argparse
import base64
import io
import json
from pathlib import Path

from PIL import Image
from vllm import LLM, SamplingParams


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="nvidia/NV-Reason-PathWSI", help="Model directory or HF model ID")
    parser.add_argument(
        "--input", required=True, help="JSONL with {'image', 'prompt'} records"
    )
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument(
        "--max-model-len", type=int, default=16384,
        help="Context length used for the reported benchmark runs (default 16384)",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=8192,
        help="Max generated tokens; the thinking-mode evals used 8192 (default)",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.0,
        help="Greedy (0.0) matches the reported numbers",
    )
    parser.add_argument(
        "--think", action="store_true",
        help="Enable thinking mode. Default off, matching the reported "
        "MCQ/PathMMU/PathVQA/PathPrivate runs. PathMMU thinking-mode reruns "
        "used this flag with --max-tokens 8192.",
    )
    parser.add_argument(
        "--gpu-memory-utilization", type=float, default=0.90
    )
    return parser.parse_args()


def image_data_url(path: str) -> str:
    """Encode a local image as a data URL (vLLM's chat expects image_url parts)."""
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    args = parse_args()

    records = []
    with open(args.input, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    if not records:
        raise SystemExit(f"no records found in {args.input}")

    missing = [
        i for i, r in enumerate(records)
        if not Path(r["image"]).is_file()
    ]
    if missing:
        raise SystemExit(
            f"{len(missing)} records point at missing images "
            f"(first bad index {missing[0]}: {records[missing[0]]['image']})"
        )

    llm = LLM(
        model=args.model,
        max_model_len=args.max_model_len,
        gpu_memory_utilization=args.gpu_memory_utilization,
        enforce_eager=True,  # matches the eval runs (container without compiler cache)
    )
    sampling = SamplingParams(
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    messages = [
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url(r["image"])},
                    },
                    {"type": "text", "text": r["prompt"]},
                ],
            }
        ]
        for r in records
    ]
    outputs = llm.chat(
        messages,
        sampling_params=sampling,
        chat_template_kwargs={"enable_thinking": args.think},
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for record, output in zip(records, outputs):
            record = dict(record)
            record["response"] = output.outputs[0].text
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"wrote {len(records)} responses to {out_path}")


if __name__ == "__main__":
    main()

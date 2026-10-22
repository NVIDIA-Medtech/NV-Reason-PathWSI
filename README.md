# NV-Reason-PathWSI

[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-yellow)](https://huggingface.co/nvidia/NV-Reason-PathWSI)
[![GitHub](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/NVIDIA-Medtech/NV-Reason-PathWSI)
[![arXiv](https://img.shields.io/badge/arXiv-XXXX.XXXXX-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/XXXX.XXXXX)
[![License](https://img.shields.io/badge/License-OpenMDW--1.1-f5de53)](LICENSE)

NV-Reason-PathWSI is a generative vision-language model for whole-slide
pathology image (WSI) interpretation. It combines a Qwen3.5-4B language model
with a gigapixel whole-slide vision tower and supports abnormality and lesion
classification, structured report generation, visual question answering, and
interactive reasoning from digitized histopathology slides.

This repository provides inference, supervised fine-tuning (SFT), and Group
Relative Policy Optimization (GRPO) examples for the
[NV-Reason-PathWSI model](https://huggingface.co/nvidia/NV-Reason-PathWSI). The
complete model package—including weights, custom model and processor code,
configuration, tokenizer, and preprocessing metadata—is maintained on Hugging
Face and is intentionally not duplicated here.

> NV-Reason-PathWSI is for research and development only. It is not a medical
> device and must not be used as a substitute for professional clinical
> judgment, diagnosis, or treatment decisions. Model outputs can be incorrect
> and should be reviewed by qualified medical professionals.

## Contents

- [`inference.py`](inference.py): one-slide command-line inference
- [`train/vlm_sft_train.py`](train/vlm_sft_train.py): SFT example
- [`train/vlm_grpo_train.py`](train/vlm_grpo_train.py): GRPO entrypoint
- [`train/vlm_grpo_trainer.py`](train/vlm_grpo_trainer.py): WSI adaptation of the TRL GRPO trainer
- [`train/vlm_rewards.py`](train/vlm_rewards.py): lesion-type-aware verifiable rewards
- [`datalists/`](datalists): sample training records; corresponding whole-slide images are not included
- [`examples/`](examples): example whole-slide images stored with Git LFS
- [`configs/`](configs): example SFT and GRPO configurations
- [`THIRD-PARTY-NOTICES`](THIRD-PARTY-NOTICES): PyPI dependencies and the third-party package licenses

## Model source

All examples load `nvidia/NV-Reason-PathWSI` with
`AutoModelForImageTextToText` and `AutoProcessor`. Because the model defines a
custom whole-slide architecture and WSI processor, `trust_remote_code=True` is
required. On first use, Transformers downloads the model package from Hugging
Face and stores it in the local Hugging Face cache.

The command-line inference example accepts `--model` when a local model copy or
a different Hugging Face repository is needed. The training configurations use
`model_name_or_path: nvidia/NV-Reason-PathWSI` by default.

## Model overview

- Language backbone: [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)
- WSI vision encoder: pathology foundation-model vision tower
- Input: hematoxylin-and-eosin-stained whole-slide images in standard scanner
  formats (`.svs`, `.tif`/`.tiff`, `.ndpi`, `.mrxs`, `.vsi`, `.scn`, `.bif`)
- Preprocessing: tissue detection, magnification-aware tile extraction, and
  stain-aware normalization handled by the custom processor
- Patch grid: non-overlapping tiles selected from detected tissue regions
- Visual interface: projected tile visual tokens are passed to the language
  model without spatial merging
- Position encoding: tile row and column positions are represented with 2D
  MRoPE

Whole-slide images are routed through the custom `wsi=` processor argument and
the whole-slide vision tower.

![NV-Reason-PathWSI overview](assets/nv_reason_pathwsi_overview.png)

## Installation

Python 3.11 and a CUDA-capable PyTorch installation are recommended. A fresh
environment can be created with [`uv`](https://docs.astral.sh/uv/):

```bash
uv venv --seed --python 3.11 nvreasonpathwsi
source nvreasonpathwsi/bin/activate
```

For inference:

```bash
uv pip install -r requirements.txt
```

For training:

```bash
uv pip install -r requirements-train.txt
uv pip install flash-attn==2.8.3 --no-build-isolation
```

The training code and configs are pinned to Transformers 5.6.2, TRL 1.2.0,
and Accelerate 1.13.0 because the custom GRPO trainer follows those TRL
internals.

## Quick start: inference

The input slide must be a valid whole-slide image readable by
[OpenSlide](https://openslide.org/). Provide the requested tissue or organ
context when applicable.

The examples below use `examples/example_1.svs`.

### Download the example slides

The whole-slide images in [`examples/`](examples) are stored with Git LFS.
Install [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage),
then run these commands from the repository root to download the actual slides:

```bash
git lfs install
git lfs pull --include="examples/*"
```

### Command-line examples

Use these prompts to generate a structured report for the slide:

```bash
# Structured pathology report
python inference.py examples/example_1.svs \
  --prompt "write a structured pathology report"

# Diagnostic reasoning
python inference.py examples/example_1.svs \
  --prompt "full slide reasoning analysis"

# Finding-specific question
python inference.py examples/example_1.svs \
  --prompt "Are tumor cells present in this slide? Answer only Yes or No."
```

A structured report is generated by default when `--prompt` is omitted.
Thinking is enabled by default. For a concise response without thinking:

```bash
python inference.py examples/example_1.svs \
  --prompt "Is mitotic activity increased? Answer only Yes or No." \
  --disable-thinking
```

Each CLI command loads the model and starts a new conversation. For several
questions or follow-up dialogue, reuse the model in Python as shown below.

### Reuse the model in Python

Load the model and processor once. `generate_response()` returns the generated
text; when a `history` list is supplied, it also appends the user and assistant
turns to that list.

```python
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor

model_id = "nvidia/NV-Reason-PathWSI"
slide_path = "examples/example_1.svs"

model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    trust_remote_code=True,
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
).eval().to("cuda")
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)


def generate_response(
    slide_path,
    prompt_text,
    enable_thinking=True,
    max_new_tokens=2048,
    history=None,
):
    """Generate a reply and append both turns to history when provided."""
    if history is None:
        history = []
    content = [{"type": "text", "text": prompt_text}]
    if not history:
        content.insert(0, {"type": "image"})
    history.append({"role": "user", "content": content})

    prompt = processor.apply_chat_template(
        history,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=enable_thinking,
    )
    inputs = processor(
        text=prompt,
        wsi=[slide_path],
        return_tensors="pt",
    ).to(model.device)

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            use_cache=True,
        )

    new_tokens = output_ids[:, inputs.input_ids.shape[1]:]
    response = processor.batch_decode(
        new_tokens,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]
    history.append(
        {"role": "assistant", "content": [{"type": "text", "text": response}]}
    )
    return response
```

These independent requests reuse the loaded model without sharing conversation
history:

```python
# Structured report
print(generate_response(slide_path, "write a structured pathology report"))

# Full reasoning
print(generate_response(slide_path, "full slide reasoning analysis"))
```

### Follow-up questions

Pass the same history list to retain earlier questions and answers:

```python
history = []
print(generate_response(slide_path, "write a structured pathology report", history=history))
print(generate_response(slide_path, "Which tumor grade best matches the morphology?", history=history))
print(generate_response(slide_path, "What is the most likely differential diagnosis?", history=history))
print(generate_response(slide_path, "which associated features support it?", history=history))
```

Keep the same slide path throughout a conversation. Start with a new empty
history list for a different slide. The image marker is included only in the
first user turn, while the same whole-slide image is supplied on every call.

To continue an existing conversation, supply alternating `user` and `assistant`
messages in the same format. The assistant replies below are shortened
examples; replace them with the actual previous replies for your slide:

```python
history = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "write a structured pathology report"},
        ],
    },
    {
        "role": "assistant",
        "content": [{"type": "text", "text": "Tumor: Invasive ductal carcinoma with moderate pleomorphism."}],
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "What is the inferred tumor grade?"}],
    },
    {
        "role": "assistant",
        "content": [{"type": "text", "text": "Histologic grade 2 of 3 by Nottingham criteria."}],
    },
]

print(generate_response(
    slide_path,
    "which associated features support it?",
    history=history,
))
```

Here, `history` ends with the previous assistant reply. The function adds the
new user question, generates a response, and appends that response to
`history`. The image marker identifies where the slide belongs in the
conversation; the slide itself is still passed separately through
`wsi=[slide_path]`.

## Inspect the model input tiles

The same preprocessing used for inference can be inspected without running the
model:

```python
import numpy as np
from PIL import Image
from transformers import AutoProcessor

processor = AutoProcessor.from_pretrained(
    "nvidia/NV-Reason-PathWSI",
    trust_remote_code=True,
)
tiles = processor.image_processor_wsi.load_slide(
    "examples/example_1.svs",
)
for i, tile in enumerate(tiles[:16]):
    Image.fromarray(tile.permute(1, 2, 0).detach().cpu().numpy()).save(f"tile_{i}.png")
```

If the default tissue detection or magnification selection is unsuitable for a
dataset, preprocess the slide in custom code and call the processor with the
precomputed tile tensor instead.

## Sample training data

The two manifests contain the same illustrative structured-report examples and
are provided for demonstration purposes only. `datalists/sft.jsonl` includes
the assistant responses; `datalists/grpo.jsonl` keeps the same prompts and
solutions without assistant responses (not needed for GRPO). Whole-slide
images are not included; download the matching slides from the source dataset
following its access instructions and dataset terms.

Each SFT row contains the conversation and repeats the slide path at the top
level so the same record is easy to adapt for GRPO:

```json
{
  "id": "case-001",
  "image": "dataset/case-001.svs",
  "solution": "Tumor present, High mitotic activity",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image", "image": "dataset/case-001.svs"},
        {"type": "text", "text": "Write a structured pathology report."}
      ]
    },
    {
      "role": "assistant",
      "content": [
        {"type": "text", "text": "<think>...</think>\n...\n<answer>Tumor present, High mitotic activity</answer>"}
      ]
    }
  ]
}
```

For GRPO, `messages` contains the user turn only. `solution` is the verified,
comma-separated finding set used by the reward. Allowed labels are defined in
[`train/vlm_labels.py`](train/vlm_labels.py). No-finding cases must use exactly
`No Pathology Finding`.

### Prepare the whole-slide images

Run the examples from this repository's root, with the training environment
from [Installation](#installation) activated. Training resolves relative image
paths against `--image_dir`; set it to the root for the paths in your JSONL
files.

Supply whole-slide images in standard scanner formats; the processor handles
tissue detection, tile extraction, and normalization.

For your own data, keep the same schema: SFT conversations must end with the
assistant response to learn from; GRPO examples contain the user prompt and
verified `solution` labels. The GRPO solution is used for scoring, not added to
the model's prompt.

## SFT example

The SFT collator computes loss only on the final assistant response, sends the
whole-slide image through `wsi=`, and preserves Qwen3.5's intended multi-turn
chat behavior. By default, the language model, WSI vision encoder, and
projector are trained end to end, starting from `nvidia/NV-Reason-PathWSI`.

On a single node with eight CUDA GPUs, launch a short eight-step run:

```bash
accelerate launch --config_file accelerate/zero2.yaml \
  train/vlm_sft_train.py \
  --config configs/sft_config.yaml \
  --dataset_path datalists/sft.jsonl \
  --image_dir /path/to/wsi-slides \
  --output_dir data/nv_reason_pathwsi_sft_example \
  --max_steps 8 \
  --logging_steps 1
```

The [SFT configuration](configs/sft_config.yaml) uses one example per GPU and
two gradient-accumulation steps: 16 examples per optimizer step across eight
GPUs. Watch the console for `loss`, `grad_norm`, and `learning_rate`. Loss
should remain finite, but it need not decrease at every step. This short run
checks the training pipeline; it is not enough to establish model quality.
Metrics are also saved in the output directory, including `trainer_state.json`
and `train_results.json`. W&B is not required (`report_to: none`).

Use `--freeze_llm`, `--freeze_visual`, or `--freeze_merger` for controlled
adaptation experiments.

## GRPO example

GRPO samples multiple responses to a prompt and learns from their relative
rewards instead of a reference assistant response. This example uses structured
reports ending with one `<answer>...</answer>` finding-label block and combines
three rewards:

```text
2.0 * abnormality-set F1
+ 0.5 * lesion-type-specific report-structure score
+ 1.0 * soft completion-length penalty
```

By default, GRPO starts independently from `nvidia/NV-Reason-PathWSI` and
trains the language model, WSI vision encoder, and projector end to end. On the
same eight-GPU setup, run six steps, which includes the configured five warmup
steps and one step after warmup:

```bash
accelerate launch --config_file accelerate/zero2.yaml \
  train/vlm_grpo_train.py \
  --config configs/grpo_config.yaml \
  --dataset_path datalists/grpo.jsonl \
  --image_dir /path/to/wsi-slides \
  --output_dir data/nv_reason_pathwsi_grpo_example \
  --max_steps 6
```

The [GRPO configuration](configs/grpo_config.yaml) generates 16 completions per
prompt. Keep the supplied eight-GPU batch and accumulation settings for this
example; changing them must preserve a generation batch divisible by
`num_generations`. Remove `--max_steps` to run the configured epochs.

Watch the total `reward`, individual reward metrics, and `reward_std` as well
as the loss. GRPO loss is not directly comparable to SFT loss. Groups whose
completions all receive the same reward provide no relative learning signal.
Generation makes each GRPO step slower than an SFT step, and a six-step run is
only a pipeline check. These rewards are specific to the structured-report
task; other QA tasks may need different rewards.

### Continue from an SFT checkpoint

To use the model saved by the SFT example instead of the release checkpoint,
change `--model_name_or_path` and use a separate output directory:

```bash
accelerate launch --config_file accelerate/zero2.yaml \
  train/vlm_grpo_train.py \
  --config configs/grpo_config.yaml \
  --model_name_or_path data/nv_reason_pathwsi_sft_example \
  --dataset_path datalists/grpo.jsonl \
  --image_dir /path/to/wsi-slides \
  --output_dir data/nv_reason_pathwsi_sft_grpo_example \
  --max_steps 6
```

The custom trainer currently uses standard Transformers generation rather
than vLLM because the WSI tensor and `wsi=` route require specialized
handling.

The supplied configurations are single-node training examples. Adapt them to
your own data and hardware.

## Use the trained model

Both training scripts save the final model and processor directly in
`--output_dir`. Load that directory with the same inference script:

```bash
python inference.py examples/example_1.svs \
  --model data/nv_reason_pathwsi_sft_example
```

Replace the slide path with one of your slides. To try a GRPO-trained model,
use its output directory for `--model`. The same `--prompt` options shown in
[Quick start: inference](#quick-start-inference) apply. In the Python
examples, set `model_id` to the output directory to load both the model and
processor, including for multi-turn inference.

Use a new output directory for each fresh experiment. If a `checkpoint-*`
subdirectory exists, rerunning the same training command automatically resumes
from the latest one, including optimizer and scheduler state. To continue an
interrupted run, keep its original configuration and output directory. Loading
the final model via `--model_name_or_path` into a new output directory starts a
new training run instead of restoring that training state.

## Acknowledgements

NV-Reason-PathWSI builds on
[Qwen3.5](https://huggingface.co/Qwen/Qwen3.5-4B),
[OpenSlide](https://openslide.org/),
[MONAI](https://monai.io/),
[Transformers](https://github.com/huggingface/transformers), and
[TRL](https://github.com/huggingface/trl). It extends the reasoning-centered
training strategy introduced in
[NV-Reason-CXR](https://github.com/NVIDIA-Medtech/NV-Reason-CXR) and
[NV-Reason-CT](https://github.com/NVIDIA-Medtech/NV-Reason-CT).

## License

This repository is released under the [OpenMDW-1.1 license](LICENSE), the same
license used by the
[Hugging Face model repository](https://huggingface.co/nvidia/NV-Reason-PathWSI).
Third-party package licenses are listed in
[THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES).

## Citation

```bibtex
@article{nvreasonpathwsi,
  title  = {NV-Reason-PathWSI: Whole-Slide Pathology Vision-Language Model},
  author = {NVIDIA},
  year   = {2026},
  journal = {arXiv preprint arXiv:XXXX.XXXXX}
}
```

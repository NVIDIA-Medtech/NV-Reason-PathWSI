# NV-Reason-PathWSI

[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-yellow)](https://huggingface.co/nvidia/NV-Reason-PathWSI)
[![GitHub](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/NVIDIA-Medtech/NV-Reason-PathWSI)
[![arXiv](https://img.shields.io/badge/arXiv-2510.04587-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2510.04587)
[![License](https://img.shields.io/badge/License-OpenMDW--1.1-f5de53)](LICENSE)

NV-Reason-PathWSI is a generative vision-language model for whole-slide
pathology image (WSI) interpretation. It supports abnormality and lesion
classification, structured report generation, visual question answering, and
interactive reasoning from digitized histopathology images.

This repository provides inference examples for the
[NV-Reason-PathWSI model](https://huggingface.co/nvidia/NV-Reason-PathWSI). The
complete model package — weights, configuration, tokenizer, and model card — is
maintained on Hugging Face and is intentionally not duplicated here.

> NV-Reason-PathWSI is for research and development only. It is not a medical
> device and must not be used as a substitute for professional clinical
> judgment, diagnosis, or treatment decisions. Model outputs can be incorrect
> and should be reviewed by qualified medical professionals.

## Contents

- [`inference.py`](inference.py): single-image command-line inference
  (transformers backend)
- [`inference_vllm.py`](inference_vllm.py): batched JSONL-to-JSONL inference
  (vLLM backend; reproduces the benchmark decoding configuration)
- [`examples/`](examples): example histopathology images stored with Git LFS
- [`THIRD-PARTY-NOTICES`](THIRD-PARTY-NOTICES): PyPI dependencies and the third-party package licenses

## Model source

All examples load `nvidia/NV-Reason-PathWSI` with
`AutoModelForImageTextToText` and `AutoProcessor`. The checkpoint is a
standard native multimodal architecture that works with stock Transformers and
vLLM — `trust_remote_code` is not required. On first use, Transformers
downloads the model package from Hugging Face and stores it in the local
Hugging Face cache.

The command-line inference example accepts `--model` when a local model copy or
a different Hugging Face repository is needed.

## Model overview

- Language backbone: [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) (native multimodal)
- Input: RGB histopathology patches and whole-slide image tiles (PNG/JPEG)
- Thinking mode: `enable_thinking` chat-template flag; direct answers by default
- GPU requirement: one ≥24 GB GPU for inference
- Number of model parameters: 4.54B (bf16)

## Installation

Python 3.11 and a CUDA-capable PyTorch installation are recommended. A fresh
environment can be created with [`uv`](https://docs.astral.sh/uv/):

```bash
uv venv --seed --python 3.11 nvreasonpathwsi
source nvreasonpathwsi/bin/activate

uv pip install -r requirements.txt
```

## Quick start: inference

### Download the example images

The images in [`examples/`](examples) are stored with Git LFS. Install
[Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage),
then run these commands from the repository root:

```bash
git lfs install
git lfs pull --include="examples/*"
```

### Command-line examples

```bash
# Open-ended description
python inference.py \
  --image examples/sample_1.png \
  --prompt "Describe the histopathological features visible in this image."

# Diagnostic reasoning (thinking mode)
python inference.py \
  --image examples/sample_1.png \
  --prompt "Reason step by step about the likely diagnosis." \
  --think

# Finding-specific question with a concise answer
python inference.py \
  --image examples/sample_1.png \
  --prompt "Are tumor cells present in this image? Answer only Yes or No."
```

Thinking is disabled by default; add `--think` to enable it.

### Batched inference

`inference_vllm.py` processes a JSONL file of
`{"image": "<path>", "prompt": "<text>"}` records and writes the same records
back with a `response` field:

```bash
python inference_vllm.py \
  --input examples/queries.jsonl \
  --output responses.jsonl
```

Defaults (greedy decoding, 16384 context, 8192 max tokens, thinking off)
match the benchmark evaluation configuration.

## Acknowledgements

NV-Reason-PathWSI builds on
[Qwen3.5](https://huggingface.co/Qwen/Qwen3.5-4B),
[Transformers](https://github.com/huggingface/transformers), and
[vLLM](https://github.com/vllm-project/vllm).

## License

This repository and the model package are released under the
[OpenMDW-1.1 license](LICENSE). Third-party package licenses are listed in
[THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES).

## Citation

```bibtex
@article{wang2026pathologycot,
  title   = {Pathology-CoT: Learning Visual Chain-of-Thought Agent from Expert
             Whole Slide Image Diagnosis Behavior},
  author  = {Wang, Sheng and Wu, Ruiming and Herndon, Charles and Liu, Yihang
             and Koga, Shunsuke and Shen, Jeanne and Huang, Zhi},
  year    = {2026},
  journal = {arXiv preprint arXiv:2510.04587}
}
```

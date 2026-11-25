# NV-Reason-PathWSI Model Card

## License/Terms of Use

Use of this model is governed by the [OpenMDW-1.1 License](LICENSE).

### Deployment Geography

Global

### Use Case

Pathologists, medical students, and medical researchers would be expected to use this model for histopathology slide report generation, question answering, and reviewable AI-generated reasoning analyses in research and educational settings.

**Important Medical AI Considerations:**
This model is designed for research and educational purposes only and should not be used for clinical diagnosis or treatment decisions. All outputs should be reviewed by qualified medical professionals. The model is intended to support medical education and research, not replace clinical judgment.

### Release Date

Huggingface 11/28/2026 via https://huggingface.co/nvidia/NV-Reason-PathWSI

## Reference(s)

[1] Wang S, Wu R, Herndon C, et al. "Pathology-CoT: Learning Visual Chain-of-Thought Agent from Expert Whole Slide Image Diagnosis Behavior." arXiv:2510.04587, 2025. https://arxiv.org/abs/2510.04587

[2] Sun Y, Zhang Y, Si Y, et al. "PathGen-1.6M: 1.6 Million Pathology Image-text Pairs Generation through Multi-agent Collaboration." arXiv:2407.00203, 2024. https://arxiv.org/abs/2407.00203

## Model Architecture

**Architecture Type:** Transformer (Vision-Language Model)<br>
**Network Architecture:** 2D vision encoder (ViT) coupled to a Qwen3.5-4B language model, with 2D positional encoding<br>
**Task:** Vision-Language (report generation, question answering, and reasoning)<br>
**Base Model:** [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)<br>
**Number of model parameters:** 4.54B total (4,539,265,536 parameters, bf16)

This model was developed by training end-to-end with Supervised Fine-Tuning (SFT) and Group Relative Policy Optimization (GRPO).

**Hugging Face integration:**
- `AutoModelForImageTextToText` + `AutoProcessor`, no remote code
- Chat template supports `enable_thinking`

## Input

**Input Type(s):** Image, Text<br>
**Input Format(s):** Whole-slide images (.svs, .tif/.tiff, .ndpi) or extracted histopathology tiles (.png, .jpg), Text prompts (string)<br>
**Input Parameters:** Image: Two-Dimensional (2D); Text: One-Dimensional (1D)<br>
**Other Properties Related to Input:** Accepts digitized histopathology slides (routine hematoxylin and eosin (H&E) and/or special stains). Whole-slide images are tiled into 2D image regions before encoding. Input image sizes are flexible, from 224 x 224 pixels up to 4K resolution. Text length limits follow the NV-Reason-CT configuration: generation is capped at 2,048 new tokens, with prompt length bounded by the Qwen3.5-4B context window. Accepts natural language prompts for medical queries, follow-up questions, and reasoning requests.

### Input Specifications

- **Medical Images:** Digitized whole-slide histopathology images and extracted image tiles (flexible input size from 224 x 224 pixels up to 4K resolution)
- **Text Prompts:** Natural language requests for pathology reports, answers to questions, or detailed reasoning analyses
- **Interactive Dialogue:** Support for follow-up questions and clarification requests

## Output

**Output Type(s):** Text<br>
**Output Format:** String<br>
**Output Parameters:** One-Dimensional (1D) natural language reports, answers, and reasoning analyses<br>
**Other Properties Related to Output:** Outputs contain structured reasoning showing step-by-step medical analysis, followed by a concise answer. This format enables transparency in the model's reasoning process and supports educational use cases. Reasoning output can be disabled for concise answers.

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.

## Software Integration

**Runtime Engine(s):**
* PyTorch
* Transformers

**Supported Hardware Microarchitecture Compatibility:**
* NVIDIA Ampere
* NVIDIA Hopper
* NVIDIA Lovelace

**Supported Operating System(s):**
* Linux

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.

## Model Version(s)

0.1 - Initial release version for pathology WSI reasoning and interpretation with structured thinking output

This model can be integrated into AI systems through the PyTorch and Transformers runtimes on NVIDIA GPU-accelerated systems. Integration requires additional use-case-specific testing and validation, following the V-model methodology described under Software Integration, before the model is deployed in any AI system.

## Training and Evaluation Datasets

### Dataset Overview

The model was trained on a curated dataset of structured question answering (QA) examples derived from whole-slide images, integrating public pathology datasets with paired reports, abnormality labels, and expert-authored reasoning.

**Total Size:** Hundreds of thousands of structured QA examples derived from tens of thousands of whole-slide images; less than a million images and less than a billion text tokens in total.

**Total Number of Datasets:** 32 (31 public TCGA datasets used for training and validation, plus 1 independent external test set used for testing).

**Partition Percentages:** Training and validation partitions are derived from the 31 TCGA datasets (the majority of the data); testing is performed on an independent external test set that is fully disjoint from all training and validation data.

**Time Period:** 2000-2025.

**Data Processing:** Whole-slide images are tiled into image regions; standardized pathology reports, abnormality-focused QA, multi-turn interactions, and pathologist-authored reasoning are converted into structured QA examples; de-identification is applied to all source data before use.

**Harmful Data Mitigation:** All TCGA source data is de-identified by the data provider; additional Protected Health Information (PHI) scrubbing and review are applied before use. Data is limited to de-identified histopathology images and accompanying medical text for research use. Users are responsible for ensuring that whole-slide images and associated patient data are properly de-identified and handled in accordance with applicable privacy requirements.

### Public Datasets

- **The Cancer Genome Atlas (TCGA):** 31 TCGA cancer-type datasets (identified by TCGA project codes), providing whole-slide histopathology images with paired pathology annotations. Link: https://portal.gdc.cancer.gov/projects/TCGA. Period of collection: 2000-2025. All TCGA source data is de-identified.

### Private Datasets

- **Independent external test set (clinical evaluation benchmark):** 579 whole-slide histopathology images with accompanying text, used for evaluation and testing only; fully disjoint from all TCGA training and validation data.
- **Providing parties:** external clinical collaborating institutions; not distributed by NVIDIA.
- **Number of data points / size per modality:** 579 whole-slide images (image modality) with paired natural-language text.
- **Nature of content:** de-identified patient histopathology data.
- **Unique identifiers/links:** not publicly available (held-out test collection).
- **Period of collection:** 2000-2025.

### Self-Sourced Synthetic Data

Report-grounded synthetic reasoning examples generated for supervised fine-tuning, derived from expert pathologist annotations of TCGA whole-slide images. Data points: included within the hundreds of thousands of structured QA training examples. Size per modality: synthetic text (reasoning chains and QA) paired with source histopathology image regions. Generation methods: expert-guided generation grounded in paired pathology reports, with review under expert guidance. AI models/systems used: internal data-generation pipelines guided by expert-authored reasoning.

## Training Dataset

**Data Modality:**
* Image
* Text

**Image Training Data Size:**
* Less than a Million Images

**Text Training Data Size:**
* Less than a Billion Tokens

**Data Collection Method by dataset:**
* Hybrid: Manually-Collected, Automatic/Sensors

**Labeling Method by dataset:**
* Hybrid: Manually-Labeled, Synthetic

**Properties:** Data count: hundreds of thousands of structured QA examples derived from tens of thousands of whole-slide images across the 31 TCGA datasets. Modalities: histopathology whole-slide images (image) and natural-language text (reports, question answering, and reasoning). Nature of content: de-identified public (TCGA) patient data with human-authored and synthetic annotations. Linguistic characteristics: English-language medical text. Time period: 2000-2025.

## Testing Dataset

**Data Modality:**
* Image
* Text

**Data Collection Method by dataset:**
* Hybrid: Manually-Collected, Automatic/Sensors

**Labeling Method by dataset:**
* Hybrid: Manually-Labeled, Synthetic

**Properties:** Data count: 579 whole-slide images (independent external test set), fully disjoint from the 31 TCGA training datasets. Modalities: histopathology whole-slide images (image) and natural-language text. Nature of content: held-out, de-identified patient data with human and synthetic annotations. Linguistic characteristics: English-language medical text. Time period: 2000-2025.

## Evaluation Dataset

**Data Modality:**
* Image
* Text

**Data Collection Method by dataset:**
* Hybrid: Manually-Collected, Automatic/Sensors

**Labeling Method by dataset:**
* Hybrid: Manually-Labeled, Synthetic

**Properties:** Data count: 579 whole-slide images from the independent external test set (clinical evaluation benchmark), fully disjoint from the 31 TCGA training datasets. Modalities: histopathology whole-slide images (image) and natural-language text. Nature of content: held-out, de-identified patient data with human and synthetic annotations. Linguistic characteristics: English-language medical text. Time period: 2000-2025.

## Inference

**Acceleration Engine:** PyTorch, Transformers<br>
**Test Hardware:**
* NVIDIA Hopper H100
* NVIDIA Lovelace L40S

## Ethical Considerations

NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

Please make sure you have proper rights and permissions for all input image and video content; if image or video includes people, personal health information, or intellectual property, the image or video generated will not blur or maintain proportions of image subjects included.

For more detailed information on ethical considerations for this model, please see the [Model Card++ Bias, Explainability, Safety & Security, and Privacy Subcards](MODEL_CARD_SUBCARDS.md).

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

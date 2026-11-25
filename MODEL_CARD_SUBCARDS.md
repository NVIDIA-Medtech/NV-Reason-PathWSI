# NV-Reason-PathWSI Model Card++ Subcards

## Bias

Field                                                                                                                                                             |  Response
:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------
Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing:  |  Not Applicable
Measures taken to mitigate against unwanted bias:                                                                                                                 |  Training data derives from 31 public TCGA cancer-type datasets, which aggregate multi-institutional, de-identified contributions across diverse tumor types; de-identification removes direct demographic attributes from the data. Model generalization is further characterized on an independent external test set (579 whole-slide images) that is fully disjoint from all training data. Known limitation: TCGA source populations are predominantly North American, and slide preparation, staining, and scanner protocols vary across sites, so performance may differ across subpopulations and sites.
Bias Metric (If Measured):                                                                                                                                        |  Not Applicable

## Explainability

Field                                                                                                       |  Response
:-----------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------
Intended Task/Domain:                                                                                        |  Pathology whole-slide image report generation, question answering, and multi-step reasoning (digital pathology / histopathology)
Model Type:                                                                                                  |  Vision-Language Model (Transformer; 2D ViT vision encoder coupled to a Qwen3.5-4B language model)
Intended Users:                                                                                              |  Pathologists, medical students, and medical researchers working with digitized histopathology slides in research and educational settings.
Output:                                                                                                      |  Natural-language text: structured reasoning showing step-by-step medical analysis, followed by a concise answer. Reasoning output can be disabled for concise answers.
Describe how the model works:                                                                                |  NV-Reason-PathWSI combines a 2D vision encoder (ViT) with a Qwen3.5-4B language model. Whole-slide images are tiled into 2D image regions; the encoder converts them into visual tokens whose 2D positions are passed to the language model without spatial downsampling, with 2D positional encoding preserving spatial relationships. The model was trained end-to-end using Supervised Fine-Tuning (SFT) and Group Relative Policy Optimization (GRPO) with verifiable rewards over pathology finding sets, using standardized reports, abnormality-focused QA, multi-turn interactions, and pathologist-authored reasoning.
Name the adversely impacted groups this has been tested to deliver comparable outcomes regardless of:        |  Not Applicable
Technical Limitations & Mitigation:                                                                          |  This model is not intended for clinical diagnosis or treatment decisions. All outputs should be reviewed by qualified medical professionals. Performance may degrade on out-of-distribution tissue types, stains, or scanner protocols not represented in training data; use-case-specific testing and validation are recommended before deployment in any downstream application.
Verified to have met prescribed NVIDIA quality standards:                                                    |  Yes
Performance Metrics:                                                                                         |  Slide-level abnormality detection (Area Under the Receiver Operating Characteristic curve (AUROC), sensitivity, specificity, F1-score (F1)) and pathology report generation quality, measured on the internal clinical evaluation benchmark (579 whole-slide images) and the independent external test set, both fully disjoint from training data.
Potential Known Risks:                                                                                       |  Generated reports and reasoning may contain errors or omissions, including hallucinated findings or incomplete coverage of rare entities. The reasoning text is generated by the model for transparency and human review. Outputs must not replace review by a qualified pathologist.
Licensing:                                                                                                   |  Use of this model is governed by the [OpenMDW-1.1 License](https://github.com/OpenMDW/OpenMDW/blob/main/1.1/LICENSE.OpenMDW-1.1). Third-party software and upstream model components remain subject to their own license terms.

## Safety

Field                                               |  Response
:---------------------------------------------------|:----------------------------------
Model Application Field(s):                         |  Healthcare
Describe the life critical impact (if present).     |  This model is not intended to be used as a standalone diagnostic device. Outputs must be reviewed by qualified medical professionals, and additional testing and evaluation is recommended prior to use in clinical settings and non-experimental downstream applications.
Use Case Restrictions:                              |  Use of this model is governed by the [OpenMDW-1.1 License](https://github.com/OpenMDW/OpenMDW/blob/main/1.1/LICENSE.OpenMDW-1.1). This model is intended for research and educational use in pathology report generation, question answering, and reasoning analysis, and is not intended for clinical diagnosis or treatment decisions. Third-party software and upstream model components remain subject to their own license terms.
Model and dataset restrictions:                     |  The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to.

## Privacy

The datasets used to train NV-Reason-PathWSI included personal data. NVIDIA collected and used this data in compliance with applicable data protection and privacy laws. NVIDIA uses a combination of filters, data minimization techniques, and other guardrails to help prevent personal data from being recited by our models. In addition, we employ automated tools and data processing techniques during pre-training or training to identify and filter certain categories of personal data. The datasets used to train this model were reviewed before release. Please review NVIDIA’s Privacy Policy (https://www.nvidia.com/en-us/about-nvidia/privacy-policy/) for more information.

Generated by the NVIDIA Model Card Generator Toolkit.

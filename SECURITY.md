# Security Policy: NV-Reason-PathWSI-4B

NVIDIA is dedicated to the security and trust of our software products and
services, including all source code repositories managed through our
organization.

If you need to report a security issue, please use the appropriate contact
points outlined below. **Please do not report security vulnerabilities through
GitHub issues or pull requests.**

## Reporting a Vulnerability

If you discover a potential security vulnerability, please **do not open a
public issue.**

* **Web (preferred):** [NVIDIA Vulnerability Disclosure Program](https://www.nvidia.com/en-us/security/)
* **E-Mail:** [psirt@nvidia.com](mailto:psirt@nvidia.com)
  - We encourage you to use the following PGP key for secure email
    communication: [NVIDIA public PGP Key](https://www.nvidia.com/en-us/security/pgp-key)
* **GitHub:** Use this repository's **Security** tab > **Report a
  vulnerability** to submit a report directly.

Please include the following information:

- Product/project name and version or branch (this repository and, if
  applicable, the Hugging Face model revision)
- Type of vulnerability
- Step-by-step reproduction instructions
- Proof-of-concept code (if available)
- Impact assessment

**Detailed reports help NVIDIA evaluate and address issues faster.**

NVIDIA's Product Security Incident Response Team (PSIRT) will acknowledge
receipt, validate severity, develop fixes, and publish security bulletins as
appropriate.

## Security Architecture & Context

NV-Reason-PathWSI is a research vision-language model family for pathology image
interpretation. This repository provides **command-line inference** scripts
only; model weights are published as standard Hugging Face model packages
(`Qwen3_5ForConditionalGeneration`) and are not duplicated here. The
checkpoints load with stock Transformers/vLLM — **no `trust_remote_code` and
no remote code execution is involved**.

This software operates at the **CLI script** level. It is not a network
service. Its primary security responsibility is to keep operator-supplied
histopathology images, prompts, and generated reports under the operator's
control.

**Repository Exposure Classification:** Public.
Basis: origin remote is GitHub and the project is an open-source research
release; this document is written for public consumption.

**Service Exposure Classification:** External / Regulated (medium confidence).
Basis: externally distributed research model materials, a medical-imaging
workload that operators may run on sensitive patient-derived data, and an
explicit research-only (not a medical device) constraint. This repository
has no network listener.

Key boundaries and interfaces:

- **Operator-supplied inputs:** local image paths, free-text prompts, JSONL
  query files, and the model identifier or local model directory.
- **Model weights:** downloaded from the official NVIDIA Hugging Face
  repositories or supplied as a local directory the operator controls.
- **No in-repo authentication or API surface:** there are no HTTP or RPC
  endpoints and no application-level auth.
- **Outputs:** generated text goes to standard output or a local JSONL file.

NV-Reason-PathWSI is for research and development only. It is not a medical device
and must not be used as a substitute for professional clinical judgment.

### Threat Model

1. **Exposure of patient-derived images and generated reports:** the tools
   read operator image files and emit text reports. Shared storage or
   overly broad output locations can disclose sensitive health data.
2. **Unexpected local file access from query manifests:** JSONL inputs
   contain filesystem paths to images. A malicious or mistaken manifest can
   cause the loader to read files the process is allowed to open but that
   were not intended as inputs.
3. **Model provenance:** loading weights from an unverified source or
   substituted local directory can change model behavior. Use the official
   Hub repositories or an operator-reviewed local copy.
4. **Unsafe clinical or production use:** model outputs can be incorrect.
   Using this software as a diagnostic service, or feeding outputs into
   clinical systems without qualified review, is outside the research
   design and can cause patient-safety harm even when the code behaves as
   implemented.

### Critical Security Assumptions

- This repository does **not** authenticate callers, encrypt data at rest,
  or terminate TLS. Access control is assumed to come from the host OS and
  the Hugging Face Hub.
- Image files and query manifests are assumed to be supplied by a trusted
  operator who is authorized to use that data. Example images in this
  repository come from public benchmark datasets and contain no patient
  identifiers.
- There is no network service in this repository. The software is assumed
  to run as a local CLI on machines the operator controls.
- Clinical safety, regulatory clearance, and policy for sensitive health
  data (including logging and retention of reports) are assumed to be
  handled **outside** this software. Research-only use is a condition of
  intended operation.

## Scope

**In scope:** vulnerabilities in this repository's inference scripts and
example assets that allow unexpected code execution, unauthorized access to
operator data, or integrity loss of inference artifacts.

**Out of scope:**

- Model quality, hallucinated findings, or clinical accuracy (unless they
  result from a security bug such as poisoned inputs or substituted weights)
- Issues solely in third-party libraries (PyTorch, Transformers, vLLM,
  Pillow) except where this repo misuses them
- Hugging Face Hub, cluster, or OS vulnerabilities
- Public GitHub issues used as a disclosure channel

## Deployment Assumptions

Operators run inference on a GPU machine they control, install the published
Python dependencies, and point the model path at a verified local tree or
the official NVIDIA Hub repository.

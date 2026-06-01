# Security Policy

IST is a dual-use research tool for semantics-preserving code transformation.
It can support defensive research such as robustness evaluation, clone-detection
benchmarking, dataset augmentation, and backdoor or poisoning analysis. It must
not be used to deploy malware, hide malicious behavior, evade security review,
or attack systems without authorization.

## Supported scope

Security reports are in scope when they affect:

- Transformation logic that unexpectedly changes program behavior.
- Parser or dataset handling issues that can corrupt experiments.
- Unsafe defaults that make misuse easier.
- Supply-chain or dependency issues in the IST maintenance workflow.

## Reporting a concern

If GitHub private vulnerability reporting is available for this repository,
please use it. Otherwise, open a minimal public issue that describes the affected
component and asks for maintainer follow-up without posting exploit details.

Please include:

- A short description of the concern.
- The affected language, transformation ID, or script.
- A minimal reproduction when it is safe to share.
- Whether the issue affects research validity, code execution, or data handling.

## Maintainer response

The maintainer will triage reports, reproduce the issue, and decide whether the
fix belongs in transformation logic, documentation, tests, or release notes.
Security-sensitive fixes should include regression coverage when practical.

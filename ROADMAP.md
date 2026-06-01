# IST Roadmap

IST aims to make code-equivalence transformation infrastructure reusable for
ML4Code, software engineering, and code-security research.

## Current maintenance priorities

- Keep the core CLI and Python API runnable on clean environments.
- Add smoke tests for representative C and Java transformations.
- Improve documentation for transformation IDs, expected inputs, and examples.
- Make dataset-processing workflows reproducible with small public samples.
- Add clear contribution and security guidance for research users.

## Near-term engineering work

- Expand smoke tests into regression tests for high-risk transformation groups.
- Add CI coverage for parser builds and syntax-preservation checks.
- Improve error messages for unsupported or partially implemented style IDs.
- Add examples for HumanEval-X, CodeXGLUE-style JSONL, and clone-detection data.
- Separate generated outputs from source files more consistently.

## Research-facing goals

- Support controlled adversarial robustness evaluation for code models.
- Support reproducible backdoor and poisoning analysis in defensive settings.
- Improve data augmentation workflows for clone detection and code generation.
- Add more language coverage where tree-sitter grammars are stable.
- Document transformation validity limits so users can cite IST responsibly.

## Maintainer automation goals

- Use Codex/API assistance for issue triage, PR review, test generation, and
  release preparation.
- Require smoke tests before accepting transformation changes.
- Keep benchmark samples small enough for contributors to run locally.
- Track transformation failures as actionable issues with minimal reproducers.

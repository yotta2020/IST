# Contributing to IST

IST welcomes contributions that make semantics-preserving code transformations
more reliable, better documented, and easier to reuse in research workflows.

## Good first contributions

- Add or improve smoke tests for an existing transformation.
- Document a transformation rule in `Conversion_type.md`.
- Add a minimal code example under `test_code/`.
- Improve CLI usability in `BatchSample_Generator.py`.
- Report a transformation that breaks syntax or changes behavior.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python scripts/smoke_test.py
```

The smoke test builds the local tree-sitter grammars if needed and checks that
basic C and Java transformations still parse successfully.

## Adding a transformation rule

1. Add the implementation in `transform/transform_<category>.py`.
2. Register the matcher, converter, and counter in `transform/config.py`.
3. Add the style ID and metadata in `transfer.py`.
4. Document the rule in `Conversion_type.md`.
5. Add a focused input example and update `scripts/smoke_test.py` when possible.

Every rule should preserve syntax. If a rule is intended for adversarial or
security research, document the intended evaluation setting clearly.

## Pull request checklist

- The change has a clear research or maintenance purpose.
- `python scripts/smoke_test.py` passes locally.
- New generated files, datasets, logs, and build outputs are not committed.
- The PR description explains the affected language and style IDs.
- Security-sensitive behavior is framed for defensive, reproducible research.

## Reporting issues

Please include:

- Language (`c`, `java`, `python`, or `c_sharp`)
- Style ID
- Minimal input code
- Expected behavior
- Actual transformed output or error message

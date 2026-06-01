#!/usr/bin/env python3
"""Minimal smoke tests for IST parser setup and core transformations."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from transfer import IST



def assert_transform(lang: str, code_path: str, style: str) -> None:
    ist = IST(lang)
    code = (ROOT / code_path).read_text(encoding="utf-8")

    if not ist.check_syntax(code):
        raise AssertionError(f"{code_path} does not parse as {lang}")
    if not ist.is_supported_style(style):
        raise AssertionError(f"Style {style} is not supported for {lang}")

    new_code, success = ist.transfer(styles=[style], code=code)
    if not success or new_code == code:
        raise AssertionError(f"Style {style} did not transform {code_path}")
    if not ist.check_syntax(new_code):
        raise AssertionError(f"Style {style} produced invalid {lang} syntax")

    tokens = ist.tokenize(new_code)
    if not tokens:
        raise AssertionError(f"Tokenization returned no tokens for {code_path}")


def main() -> None:
    assert_transform("c", "test_code/test.c", "11.2")
    assert_transform("java", "test_code/test.java", "3.1")
    print("IST smoke tests passed.")


if __name__ == "__main__":
    main()

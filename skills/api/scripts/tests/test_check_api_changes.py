#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "check_api_changes.py"
SPEC = importlib.util.spec_from_file_location("check_api_changes", SCRIPT)
assert SPEC and SPEC.loader
check_api_changes = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_api_changes
SPEC.loader.exec_module(check_api_changes)


class CheckApiChangesTests(unittest.TestCase):
    def test_yes_no_answers(self) -> None:
        with patch("builtins.input", return_value="n"):
            self.assertFalse(check_api_changes.ask_yes_no(""))

        with patch("builtins.input", return_value="yes"):
            self.assertTrue(check_api_changes.ask_yes_no(""))

    def test_eof_is_an_error(self) -> None:
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(check_api_changes.NonInteractiveInputError):
                check_api_changes.ask_yes_no("")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "check_local_coverage.py"
SPEC = importlib.util.spec_from_file_location("check_local_coverage", SCRIPT)
assert SPEC and SPEC.loader
coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coverage)


class LocalCoverageParserTests(unittest.TestCase):
    def _extract(self, source: str) -> set[tuple[str, str]]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "routes.rs").write_text(source, encoding="utf-8")
            return coverage.extract_operations(root)

    def test_reordered_fields_ignore_misleading_description_text(self) -> None:
        operations = self._extract(
            '''
#[utoipa::path(
    path = "/api/reordered",
    description = "the prose says post, and get, but is not a method",
    responses((status = 200, description = "ok")),
    get,
)]
async fn reordered() {}
'''
        )

        self.assertEqual(operations, {("GET", "/api/reordered")})

    def test_same_file_const_path_and_commented_macro(self) -> None:
        operations = self._extract(
            '''
const EXAMPLE_PATH: &str = "/api/constant";

#[utoipa::path(
    post,
    path = EXAMPLE_PATH,
    responses((status = 200, description = "ok")),
)]
async fn constant_path() {}

// #[utoipa::path(
// //     post,
// //     path = "/api/commented",
// // )]
'''
        )

        self.assertEqual(operations, {("POST", "/api/constant")})


if __name__ == "__main__":
    unittest.main()

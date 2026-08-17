#!/usr/bin/env python3
"""Compare live service-af-fe route declarations with endpoint-inventory.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


METHOD_RE = re.compile(r"\b(post|get|put|delete|patch)\s*,")
PATH_RE = re.compile(r'path\s*=\s*"(/api/[^"]+)"')
INVENTORY_RE = re.compile(
    r"^- `(GET|POST|PUT|DELETE|PATCH) (/api/[^`]+)`", re.MULTILINE
)


def extract_operations(source_root: Path) -> set[tuple[str, str]]:
    operations: set[tuple[str, str]] = set()

    for source_path in source_root.rglob("*.rs"):
        collecting = False
        macro_lines: list[str] = []

        for line in source_path.read_text(encoding="utf-8").splitlines():
            # Commented-out historical handlers are not live operations.
            if line.lstrip().startswith("//"):
                continue

            if "#[utoipa::path" in line:
                collecting = True
                macro_lines = [line]
                continue

            if not collecting:
                continue

            macro_lines.append(line)
            macro = " ".join(macro_lines)
            method = METHOD_RE.search(macro)
            route = PATH_RE.search(macro)
            if method and route:
                operations.add((method.group(1).upper(), route.group(1)))
                collecting = False
                macro_lines = []

    return operations


def extract_inventory(inventory_path: Path) -> set[tuple[str, str]]:
    inventory = inventory_path.read_text(encoding="utf-8")
    return {(method, path) for method, path in INVENTORY_RE.findall(inventory)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check endpoint-inventory.md against live Rust route declarations."
    )
    parser.add_argument(
        "--service-root",
        required=True,
        type=Path,
        help="Path to the service-af-fe checkout.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "endpoint-inventory.md",
        help="Path to the generated endpoint inventory.",
    )
    args = parser.parse_args()

    source_root = args.service_root / "src"
    if not source_root.is_dir():
        print(f"Missing service source directory: {source_root}", file=sys.stderr)
        return 2
    if not args.inventory.is_file():
        print(f"Missing endpoint inventory: {args.inventory}", file=sys.stderr)
        return 2

    source_operations = extract_operations(source_root)
    inventory_operations = extract_inventory(args.inventory)
    missing = sorted(source_operations - inventory_operations)
    extra = sorted(inventory_operations - source_operations)

    print(f"Source operations: {len(source_operations)}")
    print(f"Inventory operations: {len(inventory_operations)}")
    print(f"Source unique paths: {len({path for _, path in source_operations})}")
    print(f"Inventory unique paths: {len({path for _, path in inventory_operations})}")

    if missing:
        print("Missing from inventory:")
        for operation in missing:
            print(f"  {operation[0]} {operation[1]}")
    if extra:
        print("Extra in inventory:")
        for operation in extra:
            print(f"  {operation[0]} {operation[1]}")

    if missing or extra:
        return 1

    print("Coverage check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

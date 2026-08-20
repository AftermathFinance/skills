#!/usr/bin/env python3
"""Compare service/OpenAPI route declarations with endpoint-inventory.md.

This is source/OpenAPI declaration coverage, not runtime-route coverage. It does
not verify Actix registration, reverse-proxy routing, deployment availability,
or response behavior. Use deployment-aware smoke tests for those checks.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


METHOD_RE = re.compile(r"(?m)^[ \t]*(post|get|put|delete|patch)[ \t]*,")
PATH_LITERAL_RE = re.compile(r'\bpath\s*=\s*"(/api/[^"]+)"')
PATH_EXPR_RE = re.compile(r"\bpath\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\b")
CONST_RE = re.compile(
    r'\b(?:pub(?:\([^)]*\))?[ \t]+)?const[ \t]+'
    r'([A-Za-z_][A-Za-z0-9_]*)[ \t]*:[ \t]*&str[ \t]*=[ \t]*"(/api/[^"]+)"'
)
INVENTORY_RE = re.compile(
    r"^- `(GET|POST|PUT|DELETE|PATCH) (/api/[^`]+)`", re.MULTILINE
)


def extract_operations(source_root: Path) -> set[tuple[str, str]]:
    operations: set[tuple[str, str]] = set()

    for source_path in source_root.rglob("*.rs"):
        source = source_path.read_text(encoding="utf-8")
        constants = {name: path for name, path in CONST_RE.findall(source)}
        collecting = False
        macro_lines: list[str] = []
        macro_depth = 0

        for line in source.splitlines():
            # Commented-out historical handlers are not live operations.
            if line.lstrip().startswith("//"):
                continue

            if "#[utoipa::path" in line:
                collecting = True
                macro_lines = [line]
                macro_depth = _paren_delta(line)
                continue

            if not collecting:
                continue

            macro_lines.append(line)
            macro_depth += _paren_delta(line)
            if macro_depth <= 0:
                macro = "\n".join(macro_lines)
                method = METHOD_RE.search(macro)
                route_match = PATH_LITERAL_RE.search(macro)
                if route_match:
                    route = route_match.group(1)
                else:
                    route_expr = PATH_EXPR_RE.search(macro)
                    route = constants.get(route_expr.group(1)) if route_expr else None
                if method and route:
                    operations.add((method.group(1).upper(), route))
                collecting = False
                macro_lines = []
                macro_depth = 0

    return operations


def _paren_delta(line: str) -> int:
    """Count parentheses outside ordinary Rust string literals."""

    delta = 0
    in_string = False
    escaped = False
    for char in line:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            delta += 1
        elif char == ")":
            delta -= 1
    return delta


def extract_inventory(inventory_path: Path) -> set[tuple[str, str]]:
    inventory = inventory_path.read_text(encoding="utf-8")
    return {(method, path) for method, path in INVENTORY_RE.findall(inventory)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check endpoint-inventory.md against service source/OpenAPI "
            "route declarations; this does not check deployed runtime routes."
        )
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

    print(f"Source/OpenAPI declaration operations: {len(source_operations)}")
    print(f"Inventory operations: {len(inventory_operations)}")
    print(
        "Source/OpenAPI declaration unique paths: "
        f"{len({path for _, path in source_operations})}"
    )
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

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen


SPEC_URL = "https://aftermath.finance/api/openapi/spec.json"


@dataclass
class SkillMetadata:
    last_validated: datetime
    raw_date: str


def parse_last_validated(skill_md_path: Path) -> SkillMetadata:
    content = skill_md_path.read_text(encoding="utf-8")
    match = re.search(r"Last validated:\s*`(\d{4}-\d{2}-\d{2})`", content)
    if not match:
        raise ValueError("Could not find `Last validated: `YYYY-MM-DD`` in SKILL.md")

    raw_date = match.group(1)
    dt = datetime.strptime(raw_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return SkillMetadata(last_validated=dt, raw_date=raw_date)


def age_hours(reference: datetime, now: datetime) -> float:
    return (now - reference).total_seconds() / 3600.0


def load_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def fetch_spec_hash(url: str) -> str:
    with urlopen(url) as response:
        body = response.read()
    return hashlib.sha256(body).hexdigest()


def ask_yes_no(prompt: str) -> bool:
    ans = input(prompt).strip().lower()
    return ans in {"y", "yes"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Checks public OpenAPI spec for changes after a 24h validation window."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore 24h window and prompt immediately.",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    skill_md = skill_dir / "SKILL.md"
    state_path = skill_dir / ".api-spec-state.json"

    try:
        meta = parse_last_validated(skill_md)
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc)
    elapsed_hours = age_hours(meta.last_validated, now)

    if elapsed_hours < 24 and not args.force:
        remaining = max(0.0, 24 - elapsed_hours)
        print(
            f"Skip: only {elapsed_hours:.1f}h since Last validated ({meta.raw_date}). "
            f"Next check in ~{remaining:.1f}h."
        )
        return 0

    should_query = ask_yes_no(
        "More than 24h since Last validated. "
        f"Query {SPEC_URL} for API changes now? [y/N]: "
    )
    if not should_query:
        print("No query executed. State unchanged.")
        return 0

    previous_state = load_state(state_path)
    previous_hash = previous_state.get("last_spec_sha256")

    try:
        current_hash = fetch_spec_hash(SPEC_URL)
    except Exception as exc:  # pragma: no cover
        print(f"Failed to fetch spec: {exc}", file=sys.stderr)
        return 1

    changed = bool(previous_hash) and previous_hash != current_hash

    if previous_hash is None:
        print("Baseline created: no previous hash found.")
    elif changed:
        print("Change detected: OpenAPI spec hash differs from previous check.")
    else:
        print("No change detected: OpenAPI spec hash matches previous check.")

    new_state = {
        "spec_url": SPEC_URL,
        "last_checked_at": now.isoformat(),
        "last_spec_sha256": current_hash,
        "last_validated_in_skill": meta.raw_date,
    }
    state_path.write_text(json.dumps(new_state, indent=2) + "\n", encoding="utf-8")
    print(f"Saved state to {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

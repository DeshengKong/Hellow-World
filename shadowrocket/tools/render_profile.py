#!/usr/bin/env python3
"""Render both update entry points from one template and an immutable rules commit."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "@RULES_COMMIT@"


def render(commit):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Use a full immutable Git commit SHA")
    template = (ROOT / "profile.template.conf").read_text()
    if TOKEN not in template:
        raise ValueError("Missing snapshot token")
    payload = template.replace(TOKEN, commit).encode("utf-8")
    for name in ("we-neuro-shadowrocket.conf", "we-neuro-shadowrocket-home.conf"):
        (ROOT / name).write_bytes(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules-commit", default=None)
    args = parser.parse_args()
    commit = args.rules_commit or json.loads((ROOT / "release.json").read_text())["rules_commit"]
    render(commit)

#!/usr/bin/env python3
"""Rebuild reviewed DOMAIN-SET snapshots from hash-locked upstream inputs.

No branch-tip fetches, implicit source updates, embedded credentials, or network
access are needed when --source-cache contains the verified input files.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SETS = {
    "STUN": [0],
    "MainlandFinance": list(range(2, 15)),
    "ProtonMail": [16],
    "YouTube": [17],
    "Google": [18],
    "GitHub": [20],
    "Netflix": [21],
    "Disney": [22],
    "Max": [23],
    "Spotify": [24],
    "Telegram": [25],
    "PayPal": [26],
    "Twitter": [27],
    "Facebook": [28],
    "Amazon": [29],
    "TikTok": [30],
    "Games": list(range(31, 37)),
    "Apple": [37, 38],
    "Microsoft": [39],
    "BiliBili": [40],
    "ChinaApps": list(range(41, 48)),
    "LAN": [48],
    "China": [49, 50],
    "Global": [51],
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def active_lines(data: bytes):
    for line in data.decode("utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith(("#", ";", "//")):
            yield line


def load_source(source, cache):
    path = cache / source["cache_name"]
    if path.exists():
        data = path.read_bytes()
    else:
        # Never hide a mismatch by silently re-fetching a changed cached file.
        req = urllib.request.Request(source["url"], headers={"User-Agent": "we-neuro-rule-builder/v31"})
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read()
        if digest(data) != source["sha256"]:
            raise ValueError(f"Remote source hash mismatch: {source['cache_name']}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if digest(data) != source["sha256"]:
        raise ValueError(f"Cached source hash mismatch: {source['cache_name']}")
    return data


def domain_record(line, source_format):
    if source_format == "DOMAIN-SET":
        kind, host = ("DOMAIN-SUFFIX", line[1:]) if line.startswith(".") else ("DOMAIN", line)
    else:
        fields = line.split(",")
        kind = fields[0]
        if kind not in ("DOMAIN", "DOMAIN-SUFFIX"):
            return kind, None
        if len(fields) != 2:
            raise ValueError(f"Unexpected upstream domain rule: {line}")
        host = fields[1]
    host = host.lower().rstrip(".")
    if not host or any(c.isspace() for c in host) or any(c in host for c in ",*/#" + chr(92)) or host.startswith("."):
        raise ValueError(f"Invalid domain record: {line}")
    return kind, ("." if kind == "DOMAIN-SUFFIX" else "") + host


def build(cache, output):
    lock = json.loads((ROOT / "sources.lock.json").read_text())
    sources = {s["id"]: s for s in lock["sources"]}
    if set(sources) != {i for ids in SETS.values() for i in ids}:
        raise ValueError("Source lock and output mapping disagree")
    excluded = json.loads((ROOT / "domain-exclusions.json").read_text())
    # Exact records are excluded; a named dedicated tenant remains independently reviewable.
    exclusions = {(e["source_id"], e["record"]): e["reason"] for e in excluded["exclusions"]}
    source_data = {i: load_source(s, cache) for i, s in sources.items()}
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": 1, "release": lock["release"], "reviewed": lock["reviewed"],
                "upstream": lock["upstream"], "files": [],
                "filtering": "Keep exact/suffix domains; remove IP/ASN/keyword/UA/URL/wildcard rules and reviewed shared roots. DOMAIN-SET leading dot includes the apex and subdomains."}
    for name, ids in SETS.items():
        records, input_types, dropped_types, removed = set(), collections.Counter(), collections.Counter(), []
        for source_id in ids:
            source = sources[source_id]
            for line in active_lines(source_data[source_id]):
                kind, record = domain_record(line, source["format"])
                input_types[kind] += 1
                if record is None:
                    dropped_types[kind] += 1
                    continue
                if (source_id, record) in exclusions:
                    removed.append({"source_id": source_id, "record": record, "reason": exclusions[(source_id, record)]})
                    continue
                records.add(record)
        if not records:
            raise ValueError(f"Empty output: {name}")
        header = [f"# We Neuro {name} DOMAIN-SET - {lock['release']}",
                  "# Derived from blackmatrix7/ios_rule_script; author: blackmatrix7.",
                  "# License: upstream GNU GPL v2; see LICENSE beside this file.",
                  f"# Modified {lock['reviewed']}: deterministic domain-only extraction and shared-root exclusions.",
                  "# Source bytes and changes are recorded in sources.lock.json and manifest.json."]
        header.extend("# SOURCE: " + sources[i]["url"] for i in ids)
        payload = ("\n".join(header + sorted(records)) + "\n").encode()
        filename = name + ".list"
        (output / filename).write_bytes(payload)
        manifest["files"].append({"file": filename, "sha256": digest(payload), "bytes": len(payload),
                                  "records": len(records), "source_ids": ids,
                                  "input_types": dict(sorted(input_types.items())),
                                  "removed_non_domain_types": dict(sorted(dropped_types.items())),
                                  "removed_domains": removed})
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path, default=ROOT / ".source-cache")
    parser.add_argument("--output", type=Path, default=ROOT / "rules" / "v31")
    args = parser.parse_args()
    result = build(args.source_cache, args.output)
    print(json.dumps({"files": len(result["files"]), "records": sum(x["records"] for x in result["files"]),
                      "removed_non_domain_rules": sum(sum(x["removed_non_domain_types"].values()) for x in result["files"]),
                      "removed_shared_domain_records": sum(len(x["removed_domains"]) for x in result["files"])}, indent=2))


if __name__ == "__main__":
    main()

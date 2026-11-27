#!/usr/bin/env python3
"""Static first-match regression suite for v31.

This is an independent, limited model of the rule forms used by this profile,
not the Shadowrocket engine. It does not test DNS transport, TUN bypasses,
cached device selections, QUIC blocking, app attribution, or real egress IPs.
"""
from __future__ import annotations

import fnmatch
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import unittest
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "we-neuro-shadowrocket.conf"
CANONICAL = "https://raw.githubusercontent.com/DeshengKong/Hellow-World/master/shadowrocket/we-neuro-shadowrocket.conf"
BYBIT_NODE = "🇨🇳 台湾高级 IEPL 专线 1"
STATIC_NODES = {"HOME-Verizon-LAX", "DMIT-LAX-TLS", "DMIT-TYO-TLS", "美国高级 IEPL 专线 2"}
REGIONAL_NODES = {"香港高级 IEPL 专线 3", "台湾高级 IEPL 专线 1", "日本高级 IEPL 专线 1",
                  "新加坡高级 IEPL 专线 2", "韩国高级 IEPL 专线 1", "美国高级 IEPL 专线 3"}


def active(text):
    # A # inside a DNS URL is data. Only whole comment lines are ignored.
    return [s.strip() for s in text.splitlines() if s.strip() and not s.lstrip().startswith(("#", ";"))]


def labels(host):
    parts = host.lower().rstrip(".").split(".")
    return {".".join(parts[i:]) for i in range(len(parts))}


class Profile:
    def __init__(self):
        self.text = CONFIG.read_text()
        self.sections = {}
        section = None
        for line in active(self.text):
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
                if section in self.sections:
                    raise ValueError("Duplicate section: " + section)
                self.sections[section] = []
            else:
                if section is None:
                    raise ValueError("Content before a section")
                self.sections[section].append(line)
        self.general = dict(line.split(" = ", 1) for line in self.sections["General"])
        self.groups = {}
        for line in self.sections["Proxy Group"]:
            name, body = line.split(" = ", 1)
            fields = body.split(",")
            params = dict(f.split("=", 1) for f in fields[1:] if "=" in f)
            members = [f for f in fields[1:] if "=" not in f]
            if name in self.groups:
                raise ValueError("Duplicate group: " + name)
            self.groups[name] = {"kind": fields[0], "members": members, "params": params}
        self.rules = []
        self.remotes = []
        self.snapshot_shas = set()
        for line in self.sections["Rule"]:
            kind, rest = line.split(",", 1)
            rule = {"kind": kind, "line": line}
            if kind == "AND":
                match = re.fullmatch(r"\(\(PROTOCOL,UDP\),\(DEST-PORT,(\d+)\)\),(.+)", rest)
                if not match:
                    raise ValueError("Unsupported AND: " + line)
                rule.update(port=int(match[1]), policy=match[2])
            elif kind == "FINAL":
                rule["policy"] = rest
            else:
                fields = rest.split(",")
                rule.update(value=fields[0], policy=fields[1], flags=fields[2:])
            if kind == "DOMAIN-SET":
                url = urlsplit(rule["value"])
                match = re.fullmatch(r"/DeshengKong/Hellow-World/([0-9a-f]{40})/shadowrocket/rules/v31/([A-Za-z]+\.list)", url.path)
                if url.scheme != "https" or url.netloc != "raw.githubusercontent.com" or not match or url.query or url.fragment:
                    raise ValueError("Non-immutable remote URL: " + rule["value"])
                self.snapshot_shas.add(match[1])
                rule["file"] = match[2]
                lines = active((ROOT / "rules" / "v31" / match[2]).read_text())
                if any("," in s or "*" in s for s in lines):
                    raise ValueError("Non-domain content in DOMAIN-SET")
                rule["exact"] = {s for s in lines if not s.startswith(".")}
                rule["suffix"] = {s[1:] for s in lines if s.startswith(".")}
                self.remotes.append(rule)
            elif kind == "IP-CIDR":
                rule["network"] = ipaddress.ip_network(rule["value"])
            elif kind not in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD", "AND", "GEOIP", "FINAL"}:
                raise ValueError("Unsupported rule type: " + kind)
            self.rules.append(rule)

    def resolve(self, policy, overrides=None, seen=()):
        overrides = overrides or {}
        if policy in seen:
            raise ValueError("Policy cycle: " + " -> ".join(seen + (policy,)))
        if policy in overrides:
            return self.resolve(overrides[policy], overrides, seen + (policy,))
        if policy not in self.groups:
            return policy
        group = self.groups[policy]
        default = group["params"].get("policy-select-name")
        if not default:
            if policy == "Bybit":
                default = BYBIT_NODE  # Fixture, not a claim about the device inventory.
            elif policy == "韩国节点":
                default = "韩国高级 IEPL 专线 1"
            elif group["members"]:
                default = group["members"][0]
            else:
                raise ValueError("No fixture selection: " + policy)
        return self.resolve(default, overrides, seen + (policy,))

    def route(self, host="", protocol="TCP", port=443, address=None, country=None, overrides=None):
        host = host.lower().rstrip(".")
        suffixes = labels(host) if host else set()
        ip = ipaddress.ip_address(address) if address else None
        for rule in self.rules:
            kind = rule["kind"]
            matched = False
            if kind == "DOMAIN":
                matched = host == rule["value"]
            elif kind == "DOMAIN-SUFFIX":
                matched = rule["value"] in suffixes
            elif kind == "DOMAIN-WILDCARD":
                matched = fnmatch.fnmatchcase(host, rule["value"])
            elif kind == "DOMAIN-SET":
                matched = host in rule["exact"] or bool(suffixes & rule["suffix"])
            elif kind == "IP-CIDR":
                matched = ip is not None and ip.version == rule["network"].version and ip in rule["network"]
            elif kind == "AND":
                matched = protocol == "UDP" and port == rule["port"]
            elif kind == "GEOIP":
                matched = country == rule["value"]  # Caller-supplied fixture, no GeoIP database.
            elif kind == "FINAL":
                matched = True
            if matched:
                return rule["policy"], self.resolve(rule["policy"], overrides), rule["line"]
        raise ValueError("No final rule")


class RoutingRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = Profile()
        cls.finance = json.loads((ROOT / "tests" / "finance-cases.json").read_text())
        cls.service = json.loads((ROOT / "tests" / "service-cases.json").read_text())

    def assert_case(self, case, overrides=None):
        result = self.profile.route(host=case.get("host", ""), protocol=case.get("protocol", "TCP"),
                                    port=case.get("port", 443), address=case.get("address"),
                                    country=case.get("country"), overrides=overrides)
        if "expected_rule_policy_any" in case:
            self.assertIn(result[0], case["expected_rule_policy_any"], result[2])
        expected = case["expected_policy"]
        if overrides and result[0] == "海外主力":
            expected = self.profile.resolve("海外主力", overrides)
        self.assertIn(result[1], [expected] + case.get("expected_policy_aliases", []), result[2])

    def test_financial_domains_and_boundaries(self):
        for case in self.finance["tests"]:
            with self.subTest(id=case["id"], host=case["host"]):
                self.assert_case(case)

    def test_financial_invariants_after_overseas_selection_changes(self):
        for overrides in self.finance["policy_overrides_for_adversarial_recheck"]:
            for case in self.finance["tests"]:
                with self.subTest(id=case["id"], overrides=overrides):
                    self.assert_case(case, overrides)

    def test_service_routing_and_known_collisions(self):
        for case in self.service["tests"]:
            with self.subTest(id=case["id"], host=case.get("host"), address=case.get("address")):
                self.assert_case(case)

    def test_bybit_filter_accepts_only_line_one(self):
        regex = self.profile.groups["Bybit"]["params"]["policy-regex-filter"]
        for case in self.finance["bybit_node_filter_tests"]:
            with self.subTest(node=case["name"]):
                self.assertEqual(bool(re.search(regex, case["name"])), case["should_match"])
        self.assertEqual(self.profile.groups["Bybit"]["members"], [])
        self.assertEqual(self.profile.groups["Bybit"]["params"]["select"], "0")

    def test_groups_defined_acyclic_and_financial_groups_removed(self):
        removed = {"N26", "Starryblu", "Wise", "IBKR", "嘉信", "OKX"}
        self.assertFalse(removed & self.profile.groups.keys())
        self.assertEqual(self.profile.groups["Coinbase"]["members"], ["DMIT-LAX-TLS"])
        terminals = STATIC_NODES | REGIONAL_NODES | {"DIRECT", "REJECT", "PROXY", BYBIT_NODE}
        known = terminals | self.profile.groups.keys()
        for name, group in self.profile.groups.items():
            with self.subTest(group=name):
                self.assertEqual(group["kind"], "select")
                self.assertTrue(set(group["members"]) <= known)
                self.assertIn(self.profile.resolve(name), terminals)
                if "policy-regex-filter" in group["params"]:
                    re.compile(group["params"]["policy-regex-filter"])
        for rule in self.profile.rules:
            self.assertIn(rule["policy"], known)
        # Validate every selectable group edge, not just the current default path.
        def visit(name, trail=()):
            self.assertNotIn(name, trail, " -> ".join(trail + (name,)))
            group = self.profile.groups[name]
            edges = list(group["members"])
            edges.append(group["params"].get("policy-select-name", ""))
            for child in edges:
                if child in self.profile.groups:
                    visit(child, trail + (name,))
        for name in self.profile.groups:
            visit(name)
        self.assertEqual(self.profile.rules[-1]["kind"], "FINAL")
        self.assertEqual(sum(r["kind"] == "FINAL" for r in self.profile.rules), 1)

    def test_shared_google_selection_and_independent_webrtc(self):
        for name in ("Google", "Claude", "WebRTC", "出口检测"):
            self.assertEqual(self.profile.resolve(name), "HOME-Verizon-LAX")
        self.assertEqual(self.profile.groups["YouTube"]["members"], ["Google"])
        for host in ["www.youtube.com", "rr1.googlevideo.com", "gemini.google.com", "colab.research.google.com", "antigravity.google"]:
            with self.subTest(host=host):
                self.assertEqual(self.profile.route(host, overrides={"Google": "DMIT-LAX-TLS"})[1], "DMIT-LAX-TLS")
        self.assertEqual(self.profile.route("stun.l.google.com", protocol="UDP", port=19302,
                                          overrides={"Google": "DMIT-LAX-TLS"})[1], "HOME-Verizon-LAX")

    def test_dns_is_node_bound_and_has_no_system_fallback(self):
        general = self.profile.general
        for key in ("dns-server", "fallback-dns-server"):
            urls = general[key].split(",")
            self.assertEqual(len(urls), 1)
            url = urlsplit(urls[0])
            self.assertEqual(url.scheme, "https")
            self.assertEqual(parse_qs(url.fragment), {"proxy": ["HOME-Verizon-LAX"]})
            self.assertNotIn("ecs", parse_qs(url.fragment))
        self.assertEqual(general["proxy-dns-server"], "223.5.5.5,119.29.29.29")
        self.assertEqual(general["dns-direct-system"], "true")
        self.assertEqual(general["dns-direct-fallback-proxy"], "false")
        self.assertEqual(general["ipv6"], "false")
        self.assertEqual(general["udp-policy-not-supported-behaviour"], "REJECT")
        self.assertEqual(general["block-quic"], "all-proxy")
        self.assertEqual(self.profile.sections["Host"], ["localhost = 127.0.0.1"])

    def test_no_credentials_or_unreviewed_broad_rule_types(self):
        self.assertEqual(self.profile.sections["Proxy"], [])
        allowed = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD", "DOMAIN-SET", "IP-CIDR", "AND", "GEOIP", "FINAL"}
        self.assertTrue({r["kind"] for r in self.profile.rules} <= allowed)
        ips = [r for r in self.profile.rules if r["kind"] == "IP-CIDR"]
        self.assertEqual(len(ips), 41)  # 3 management + 18 local + 14 Telegram + 5 Google + 1 Apple.
        self.assertEqual(sum(r["policy"] == "Telegram" for r in ips), 14)
        self.assertTrue(all(r["flags"] == ["no-resolve"] for r in ips))
        self.assertEqual([r["value"] for r in self.profile.rules if r["kind"] == "DOMAIN-WILDCARD"],
                         ["*mask*.apple-dns.net", "*mask*.icloud.com", "*siri*.apple.com"])

    def test_immutable_snapshots_hashes_and_compatibility_alias(self):
        self.assertEqual(len(self.profile.snapshot_shas), 1)
        self.assertEqual(len(self.profile.remotes), 24)
        manifest = json.loads((ROOT / "rules" / "v31" / "manifest.json").read_text())
        self.assertEqual({r["file"] for r in self.profile.remotes}, {r["file"] for r in manifest["files"]})
        for item in manifest["files"]:
            with self.subTest(file=item["file"]):
                payload = (ROOT / "rules" / "v31" / item["file"]).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), item["sha256"])
                self.assertEqual(len(payload), item["bytes"])
                self.assertEqual(len(active(payload.decode())), item["records"])
        exclusions = json.loads((ROOT / "domain-exclusions.json").read_text())["exclusions"]
        applied = {(r["source_id"], r["record"]) for item in manifest["files"] for r in item["removed_domains"]}
        self.assertEqual(applied, {(e["source_id"], e["record"]) for e in exclusions})
        self.assertEqual(CONFIG.read_bytes(), (ROOT / "we-neuro-shadowrocket-home.conf").read_bytes())
        self.assertEqual(self.profile.general["update-url"], CANONICAL)
        sha = next(iter(self.profile.snapshot_shas))
        self.assertEqual(self.profile.text, (ROOT / "profile.template.conf").read_text().replace("@RULES_COMMIT@", sha))
        release = ROOT / "release.json"
        if release.exists():
            self.assertEqual(json.loads(release.read_text())["rules_commit"], sha)

    def test_retained_ip_exceptions_against_frozen_primary_evidence(self):
        directory = ROOT / "rules" / "v31" / "evidence"
        review = json.loads((directory / "ip-review.json").read_text())
        for source in review["sources"]:
            data = (directory / source["file"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), source["sha256"])
        owned = json.loads((directory / "google-owned.json").read_text())
        cloud = json.loads((directory / "google-cloud-customers.json").read_text())
        def networks(obj):
            return {ipaddress.ip_network(p.get("ipv4Prefix", p.get("ipv6Prefix"))) for p in obj["prefixes"]}
        owned_nets, cloud_nets = networks(owned), networks(cloud)
        google_rules = {r["network"] for r in self.profile.rules if r["kind"] == "IP-CIDR" and r["policy"] == "Google"}
        expected = {ipaddress.ip_network(n) for n in review["google_kept_prefixes"]}
        self.assertEqual(google_rules, expected)
        self.assertTrue(expected <= owned_nets)
        for net in expected:
            self.assertFalse(any(net.version == c.version and net.overlaps(c) for c in cloud_nets))
        telegram = {ipaddress.ip_network(s) for s in active((directory / "telegram-cidr.txt").read_text())}
        self.assertEqual(telegram, {r["network"] for r in self.profile.rules if r["kind"] == "IP-CIDR" and r["policy"] == "Telegram"})
        self.assertEqual({r["value"] for r in self.profile.rules if r["kind"] == "IP-CIDR" and r["policy"] == "苹果服务"},
                         set(review["apple_kept_prefixes"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)

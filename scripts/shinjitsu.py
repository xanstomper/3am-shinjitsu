#!/usr/bin/env python3
"""3AM Shinjitsu — authorization-gated universal assessment helper.

This tool does not scan, exploit, brute-force, or bypass controls. It validates
an authorization manifest, generates an assessment plan/state ledger, and renders
a report. Active validation remains a human-directed, read-only operation under RoE.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import secrets
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
UNIVERSAL = ROOT / "references" / "universal-coverage.md"

DOMAINS = [
    ("U01", "External presence & DNS"),
    ("U02", "Network edge & services"),
    ("U03", "Web application"),
    ("U04", "API & microservices"),
    ("U05", "Identity & access"),
    ("U06", "Client & end user"),
    ("U07", "Cloud control plane"),
    ("U08", "Compute & containers"),
    ("U09", "Data stores & backups"),
    ("U10", "Supply chain & dependencies"),
    ("U11", "Email & collaboration"),
    ("U12", "Endpoint & devices"),
    ("U13", "AI & LLM systems"),
    ("U14", "Detection & response"),
    ("U15", "Governance & data"),
    ("U16", "Human & process"),
]
DOMAIN_IDS = {d for d, _ in DOMAINS}
STATUSES = {"PENDING", "PROBED", "EXHAUSTED", "N/A", "BLOCKED"}
METHODS = ("passive", "active-read-only", "authenticated-read-only")
METHOD_RANK = {m: i for i, m in enumerate(METHODS)}


class GateError(Exception):
    pass


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GateError(f"{field} is not ISO-8601: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def load_json(path: str) -> dict:
    try:
        data = json.loads(Path(path).read_text())
    except FileNotFoundError as exc:
        raise GateError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise GateError(f"{path} must contain a JSON object")
    return data


def write_json(path: str, data: dict, force: bool = False) -> None:
    out = Path(path)
    if out.exists() and not force:
        raise GateError(f"refusing to overwrite existing file: {out} (use --force)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def split_host_port(target: str) -> tuple[str, int | None]:
    raw = target.strip()
    if not raw:
        raise GateError("empty target")
    parsed = urlparse(raw if "://" in raw else "//" + raw)
    host = parsed.hostname
    port = parsed.port
    if not host:
        raise GateError(f"could not parse host from target: {target}")
    return host.rstrip(".").lower(), port


def normalize_scope_entry(entry: str) -> dict:
    raw = entry.strip().lower().rstrip(".")
    if not raw:
        raise GateError("empty target in authorization manifest")
    try:
        if "/" in raw and "://" not in raw:
            return {"type": "network", "value": ipaddress.ip_network(raw, strict=False)}
        parsed = urlparse(raw if "://" in raw else "//" + raw)
        host = (parsed.hostname or "").rstrip(".").lower()
        if not host:
            raise ValueError("missing host")
        try:
            return {"type": "ip", "value": ipaddress.ip_address(host), "port": parsed.port}
        except ValueError:
            if host.startswith("*."):
                return {"type": "wildcard", "value": host[2:], "port": parsed.port}
            return {"type": "host", "value": host, "port": parsed.port}
    except ValueError as exc:
        raise GateError(f"invalid scope entry {entry!r}: {exc}") from exc


def entry_matches(entry: dict, host: str, port: int | None) -> bool:
    if entry.get("port") is not None and entry["port"] != port:
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    kind = entry["type"]
    if kind == "network":
        return ip is not None and ip in entry["value"]
    if kind == "ip":
        return ip is not None and ip == entry["value"]
    if kind == "host":
        return host == entry["value"]
    if kind == "wildcard":
        suffix = "." + entry["value"]
        return host.endswith(suffix) and host != entry["value"]
    return False


def requirement_rank(method: str) -> int:
    if method not in METHOD_RANK:
        raise GateError(f"unknown method {method!r}; choose one of {', '.join(METHODS)}")
    return METHOD_RANK[method]


def authorize(path: str, target: str, method: str = "passive") -> tuple[dict, str, int | None]:
    data = load_json(path)
    required = ["authorization_id", "authorized", "operator", "engagement",
                "approved_by", "roe_reference", "expires_at", "targets", "allowed_methods"]
    missing = [k for k in required if k not in data]
    if missing:
        raise GateError(f"authorization manifest missing: {', '.join(missing)}")
    if data.get("authorized") is not True:
        raise GateError("authorization manifest does not explicitly set authorized=true")
    expires = parse_time(str(data["expires_at"]), "expires_at")
    if expires <= now_utc():
        raise GateError(f"authorization expired at {expires.isoformat()}")
    if "issued_at" in data:
        issued = parse_time(str(data["issued_at"]), "issued_at")
        if issued > now_utc():
            raise GateError("authorization issued_at is in the future; refusing to use it")
    allowed = data.get("allowed_methods")
    if not isinstance(allowed, list) or not allowed:
        raise GateError("allowed_methods must be a non-empty list")
    needed = requirement_rank(method)
    if not any(requirement_rank(str(m)) >= needed for m in allowed):
        raise GateError(f"method {method!r} is not granted by this authorization")
    host, port = split_host_port(target)
    exclusions = data.get("excluded_targets", [])
    if not isinstance(exclusions, list):
        raise GateError("excluded_targets must be a list when present")
    for raw in exclusions:
        if entry_matches(normalize_scope_entry(str(raw)), host, port):
            raise GateError(f"target {target!r} is explicitly excluded by the authorization")
    targets = data.get("targets")
    if not isinstance(targets, list) or not targets:
        raise GateError("targets must be a non-empty list")
    matches = [e for e in (normalize_scope_entry(str(t)) for t in targets) if entry_matches(e, host, port)]
    if not matches:
        raise GateError(f"target {target!r} ({host}) is not in the authorization scope")
    return data, host, port


def cmd_validate(a) -> int:
    data, host, port = authorize(a.authorization, a.target, a.method)
    print(f"AUTHORIZATION OK: {data['authorization_id']} / {data['roe_reference']}")
    print(f"Target: {host}{':' + str(port) if port else ''}")
    print(f"Method: {a.method}")
    print(f"Expires: {data['expires_at']}")
    return 0


def cmd_profiles(_) -> int:
    for did, name in DOMAINS:
        print(f"{did:4}  {name}")
    return 0


def challenge_domain(target: str) -> str:
    host, _ = split_host_port(target)
    try:
        ipaddress.ip_address(host)
        raise GateError("DNS challenge requires a domain, not a bare IP address")
    except ValueError:
        return host


def cmd_challenge(a) -> int:
    host = challenge_domain(a.target)
    token = a.token or secrets.token_urlsafe(24)
    print("Add this TXT record at your DNS provider:")
    print(f"_shinjitsu.{host}. 300 IN TXT \"shinjitsu-verify={token}\"")
    print()
    print(f"Verify with: python3 scripts/shinjitsu.py verify-dns --authorization <authorization.json> --target {host} --token {token}")
    return 0


def cmd_verify_dns(a) -> int:
    data, host, _ = authorize(a.authorization, a.target, "active-read-only")
    host = challenge_domain(host)
    if not shutil.which("dig"):
        raise GateError("dig is not installed; verify the TXT record manually")
    out = subprocess.run(["dig", "+short", "TXT", f"_shinjitsu.{host}"],
                        capture_output=True, text=True, timeout=10, check=False).stdout
    ok = f"shinjitsu-verify={a.token}" in out
    print(out.strip() or "(no TXT records returned)")
    if not ok:
        raise GateError("challenge token not found in DNS response")
    print(f"CONTROL PROOF OK: {data['authorization_id']} controls {host}")
    return 0


def empty_state(data: dict, target: str, host: str, port: int | None) -> dict:
    return {
        "schema_version": 2,
        "target": target,
        "locked": now_utc().isoformat(),
        "authorization": {
            "id": data["authorization_id"],
            "roe_reference": data["roe_reference"],
            "operator": data["operator"],
            "engagement": data["engagement"],
            "expires_at": data["expires_at"],
            "allowed_methods": data["allowed_methods"],
            "approved_by": data["approved_by"],
        },
        "scope": {"host": host, "port": port, "excluded_targets": data.get("excluded_targets", [])},
        "universal_inventory": {
            did: {"name": name, "status": "PENDING", "reason": "", "evidence": "", "updated_at": None}
            for did, name in DOMAINS
        },
        "exhaustion_ledger": {},
        "findings_ledger": [],
        "asset_baselines": {},
        "revert_map": "no state changes made - read-only assessment",
        "noise_budget": "not started",
        "residual_edges": [],
    }


def cmd_plan(a) -> int:
    data, host, port = authorize(a.authorization, a.target, a.method)
    stamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    if a.state:
        write_json(a.state, empty_state(data, a.target, host, port), force=a.force)
    rows = "\n".join(f"| {did} | {name} | PENDING |" for did, name in DOMAINS)
    plan = f"""# 3AM Shinjitsu — Universal Assessment Plan

**Engagement:** {data['engagement']}
**Target:** {a.target}
**Authorization:** {data['authorization_id']} / {data['roe_reference']} / expires {data['expires_at']}
**Approved by:** {data['approved_by']}
**Generated:** {stamp}
**Method:** {a.method}

## Scope lock

- In-scope: entries listed in the authorization manifest only.
- Excluded: {', '.join(data.get('excluded_targets', [])) or 'none listed'}
- Destructive actions, persistence, data extraction, DoS, social engineering, and third-party/vendor attacks are not authorized by this plan.
- Capture P0 answers verbatim in the campaign state before testing.

## Universal coverage

Complete every row or mark N/A with a concrete reason. Read `references/universal-coverage.md` before probing an unfamiliar class.

| ID | Domain | Status |
|---|---|---|
{rows}

## Execution order

1. Verify authorization and exclusions; store the manifest reference (not secrets) in campaign state.
2. Passive mapping first: inventory, exposure, identity, trust boundaries, data flows.
3. Score candidate tests; run only read-only, minimal proofs inside scope.
4. Record each negative with the exact test in the exhaustion ledger.
5. Close with coverage status, residual edges, revert map, and report.
"""
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True)
        Path(a.output).write_text(plan)
        print(f"plan written: {a.output}")
        if a.state:
            print(f"state written: {a.state}")
    else:
        print(plan)
        if a.state:
            print(f"state written: {a.state}", file=sys.stderr)
    return 0


def load_state(path: str) -> dict:
    state = load_json(path)
    inventory = state.get("universal_inventory")
    if not isinstance(inventory, dict):
        raise GateError("state has no universal_inventory; generate one with `plan --state`")
    unknown = sorted(set(inventory) - DOMAIN_IDS)
    missing = sorted(DOMAIN_IDS - set(inventory))
    if unknown:
        raise GateError(f"unknown universal domains in state: {', '.join(unknown)}")
    if missing:
        raise GateError(f"state is missing universal domains: {', '.join(missing)}")
    for did, entry in inventory.items():
        if not isinstance(entry, dict) or entry.get("status") not in STATUSES:
            raise GateError(f"invalid status for {did}")
    return state


def cmd_status(a) -> int:
    state = load_state(a.state)
    counts = {s: 0 for s in STATUSES}
    for entry in state["universal_inventory"].values():
        counts[entry["status"]] += 1
    total = len(DOMAINS)
    done = counts["PROBED"] + counts["EXHAUSTED"] + counts["N/A"]
    print(f"Target: {state.get('target')}")
    print(f"Coverage: {done}/{total} complete")
    for status in ["PENDING", "BLOCKED", "PROBED", "EXHAUSTED", "N/A"]:
        print(f"  {status:9} {counts[status]}")
    pending = [did for did, e in state["universal_inventory"].items() if e["status"] == "PENDING"]
    blocked = [did for did, e in state["universal_inventory"].items() if e["status"] == "BLOCKED"]
    if pending:
        print("Pending: " + ", ".join(pending))
    if blocked:
        print("Blocked: " + ", ".join(blocked))
    if a.fail_on_incomplete and (pending or blocked):
        return 1
    return 0


def cmd_set_status(a) -> int:
    if a.domain not in DOMAIN_IDS:
        raise GateError(f"domain must be one of {', '.join(sorted(DOMAIN_IDS))}")
    state = load_state(a.state)
    entry = state["universal_inventory"][a.domain]
    status = a.status
    if status == "N/A" and not a.reason:
        raise GateError("N/A requires --reason with a concrete, verifiable reason")
    if status in {"PROBED", "EXHAUSTED"} and not (a.evidence or a.reason):
        raise GateError(f"{status} requires --evidence or --reason")
    entry.update({
        "status": status,
        "reason": a.reason or "",
        "evidence": a.evidence or "",
        "updated_at": now_utc().isoformat(),
    })
    write_json(a.state, state, force=True)
    print(f"{a.domain} -> {status}")
    return 0


def md_cell(value) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()


def cmd_report(a) -> int:
    state = load_state(a.state)
    auth = state.get("authorization", {})
    inv = state["universal_inventory"]
    complete = sum(1 for e in inv.values() if e["status"] in {"EXHAUSTED", "N/A"})
    coverage_rows = "\n".join(
        f"| {did} {inv[did]['name']} | {inv[did]['status']} | {md_cell(inv[did]['evidence'] or inv[did]['reason'])} |"
        for did, _ in DOMAINS
    )
    findings = state.get("findings_ledger", [])
    if findings:
        finding_blocks = []
        for f in findings:
            fid = f.get("id", "F?")
            finding_blocks.append(
                f"### {fid} — {f.get('verdict', 'INCONCLUSIVE')}: {f.get('claim', '')}\n"
                f"- **Evidence:** {f.get('evidence', '')}\n"
                f"- **Confidence:** {f.get('confidence', '')}\n"
                f"- **Decay:** {f.get('decay', 're-verify before use')}"
            )
        finding_text = "\n\n".join(finding_blocks)
    else:
        finding_text = "No findings recorded yet."
    exhausted = state.get("exhaustion_ledger", {})
    ledger_text = "\n".join(f"- **{k}:** {v}" for k, v in exhausted.items()) or "- Not recorded"
    residual = "\n".join(f"- {r}" for r in state.get("residual_edges", [])) or "- None recorded"
    report = f"""# 3AM Shinjitsu — Assessment Report

**Engagement:** {auth.get('engagement', '')}
**Target:** {state.get('target', '')}
**Authorization:** {auth.get('id', '')} / {auth.get('roe_reference', '')} / expires {auth.get('expires_at', '')}
**Approved by:** {auth.get('approved_by', '')}
**Generated:** {now_utc().strftime('%Y-%m-%d %H:%M UTC')}
**Coverage closed:** {complete}/{len(DOMAINS)} domains

## Scope
Host: {state.get('scope', {}).get('host', '')}{(':' + str(state.get('scope', {}).get('port'))) if state.get('scope', {}).get('port') else ''}
Exclusions: {', '.join(state.get('scope', {}).get('excluded_targets', [])) or 'none listed'}

## Coverage matrix
| Domain | Status | Evidence / reason |
|---|---|---|
{coverage_rows}

## Findings
{finding_text}

## Exhaustion ledger
{ledger_text}

## Residual edges
{residual}

## Revert map / state changes
{state.get('revert_map', 'not recorded')}

## Closeout
What did the attacker gain — and what did it take, in minutes?

{a.closeout or 'Not recorded.'}
"""
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True)
        Path(a.output).write_text(report)
        print(f"report written: {a.output}")
    else:
        print(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("profiles", help="list the 16 universal assessment domains")
    sp.set_defaults(func=cmd_profiles)

    sp = sub.add_parser("validate", help="validate an authorization manifest against a target")
    sp.add_argument("--authorization", required=True)
    sp.add_argument("--target", required=True)
    sp.add_argument("--method", choices=METHODS, default="passive")
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("challenge", help="print a DNS TXT control-proof challenge")
    sp.add_argument("--target", required=True)
    sp.add_argument("--token")
    sp.set_defaults(func=cmd_challenge)

    sp = sub.add_parser("verify-dns", help="verify the DNS TXT control proof")
    sp.add_argument("--authorization", required=True)
    sp.add_argument("--target", required=True)
    sp.add_argument("--token", required=True)
    sp.set_defaults(func=cmd_verify_dns)

    sp = sub.add_parser("plan", help="generate an authorized universal assessment plan")
    sp.add_argument("--authorization", required=True)
    sp.add_argument("--target", required=True)
    sp.add_argument("--method", choices=METHODS, default="passive")
    sp.add_argument("--output")
    sp.add_argument("--state", help="write a schema-v2 state ledger")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_plan)

    sp = sub.add_parser("status", help="show universal coverage state")
    sp.add_argument("--state", required=True)
    sp.add_argument("--fail-on-incomplete", action="store_true")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("set-status", help="record a domain's closeout status")
    sp.add_argument("--state", required=True)
    sp.add_argument("--domain", required=True)
    sp.add_argument("--status", required=True, choices=sorted(STATUSES))
    sp.add_argument("--evidence")
    sp.add_argument("--reason")
    sp.set_defaults(func=cmd_set_status)

    sp = sub.add_parser("report", help="render a markdown report from state")
    sp.add_argument("--state", required=True)
    sp.add_argument("--output")
    sp.add_argument("--closeout")
    sp.set_defaults(func=cmd_report)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except GateError as exc:
        print(f"gate: {exc}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print("gate: external command timed out", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
3AM verification suite — offline, stdlib-only, ~1s.

Proves the mandate's machinery is intact: scripts compile, JSON valid,
synthesis matrix >= 59 rows and in sync with the module, every CLI
subcommand present, old block-art absent, gate language correct,
mandate payload complete, and the skill dir mirrors the repo.

Usage:
  python3 scripts/verify_3am.py                     # all checks
  python3 scripts/verify_3am.py --only compile,json # subset
Exit: 0 all PASS · 1 any FAIL (never claims green on failure).

Env: SHINJITSU_SKILL_DIR overrides the skill-dir path for the sync check.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILL = Path(__file__).resolve().parents[2] / "skills" / "security" / "3am-shinjitsu"
if not SKILL.exists():
    SKILL = HERE.parent  # running from the skill dir directly

CHECKS = []


def check(name, fn):
    CHECKS.append((name, fn))


def ok(name, extra=""):
    print(f"  PASS  {name}" + (f"  ({extra})" if extra else ""))


def bad(name, why):
    print(f"  FAIL  {name}  — {why}")


# ── 1. scripts compile ────────────────────────────────────────────────
def c_compile():
    bad_ones = []
    for py in sorted(HERE.glob("*.py")):
        r = subprocess.run([sys.executable, "-m", "py_compile", str(py)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            bad_ones.append(py.name)
    if bad_ones:
        bad("compile", f"{bad_ones} failed")
        return False
    ok("compile", f"{len(list(HERE.glob('*.py')))} scripts")
    return True


# ── 2. JSON templates valid ───────────────────────────────────────────
def c_json():
    bad_ones = []
    for jf in sorted((ROOT / "templates").glob("*.json")):
        try:
            json.loads(jf.read_text())
        except Exception as e:
            bad_ones.append(f"{jf.name}: {e}")
    if bad_ones:
        bad("templates JSON", "; ".join(bad_ones))
        return False
    ok("templates JSON", f"{len(list((ROOT / 'templates').glob('*.json')))} files")
    return True


# ── 3. matrix in sync: module MATRIX == matrix.json, >= 59 rows ───────
def c_matrix():
    import importlib.util
    spec = importlib.util.spec_from_file_location("ei3am", str(HERE / "exploit-intel.py"))
    ei = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ei)
    mod_rows = len(ei.MATRIX)
    mj = json.loads((HERE / "matrix.json").read_text())
    json_rows = len(mj.get("rows", []))
    if mod_rows < 59 or json_rows != mod_rows:
        bad("matrix sync", f"module={mod_rows} json={json_rows} (want >=59, equal)")
        return False
    ok("matrix sync", f"{mod_rows} pairs module==json")
    return True


# ── 4. every subcommand present ───────────────────────────────────────
def c_cli():
    want = {"teardown", "synthesize", "derive", "register", "converge", "learn",
            "drift", "status", "next", "report", "promote", "chain"}
    r = subprocess.run([sys.executable, str(HERE / "exploit-intel.py"), "--help"],
                       capture_output=True, text=True)
    have = set(re.findall(r"^\s*\{?(\w+),?", r.stdout, re.M)) & want
    missing = want - have
    # help renders a single-line choices list: also parse the usage line
    if missing:
        usage = re.search(r"\{([^}]+)\}", r.stdout)
        if usage:
            have = set(usage.group(1).split(",")) & want
            missing = want - have
    if missing:
        bad("CLI subcommands", f"missing {sorted(missing)}")
        return False
    ok("CLI subcommands", f"{len(have)} commands")
    return True


# ── 5. old art absent, trigger sequence present ───────────────────────
def c_art():
    files = [ROOT / "SKILL.md", ROOT / "references" / "mandate.txt"]
    if (ROOT / "README.md").exists():
        files.append(ROOT / "README.md")
    old = 0
    trig = 0
    for f in files:
        t = f.read_text(encoding="utf-8")
        old += len(re.findall(r"████|3 A M", t))
        trig += t.count("MANDATE TRIGGERED")
    if old:
        bad("art", f"{old} old-art matches across the tree")
        return False
    if trig < 3:
        bad("art", f"trigger sequence only in {trig}/3 files")
        return False
    ok("art", "zero old art, trigger sequence in all docs")
    return True


# ── 6. gate language: no document/TXT demands ─────────────────────────
def c_gate():
    bad_ones = []
    t = (ROOT / "references" / "mandate.txt").read_text(encoding="utf-8")
    for banned in ("Demand a control proof", "written RoE / ticket", "fill the manifest"):
        if banned in t:
            bad_ones.append(f"'{banned}' present")
    for required in ("CAPABILITY", "no documents", "P0 Scope Lock"):
        if required not in t:
            bad_ones.append(f"'{required}' missing")
    if bad_ones:
        bad("gate language", "; ".join(bad_ones))
        return False
    ok("gate language", "CAPABILITY + no-document doctrine + clarify P0 recorded")
    return True


# ── 7. SKILL sections §1..§20 + version ───────────────────────────────
def c_sections():
    t = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    missing = [f"§{i}" for i in range(1, 20) if f"§{i} " not in t]
    ver = re.search(r"^version:\s*([0-9.]+)", t, re.M)
    if missing or not ver:
        bad("sections", f"missing {missing} version={ver.group(1) if ver else '?'}")
        return False
    ok("sections", f"§1–§19 present, version {ver.group(1)}")
    return True


# ── 8. skill dir mirrors the repo (core files) ────────────────────────
def c_sync():
    core = ["SKILL.md", "references/mandate.txt", "references/takeover-batteries.md",
            "references/universal-coverage.md", "references/vector-synthesis-matrix.md",
            "scripts/exploit-intel.py", "scripts/matrix.json",
            "templates/campaign-state.json"]
    import hashlib
    drift = []
    for rel in core:
        a, b = ROOT / rel, SKILL / rel
        if not a.exists() or not b.exists():
            drift.append(f"{rel} missing one side")
            continue
        if hashlib.sha256(a.read_bytes()).digest() != hashlib.sha256(b.read_bytes()).digest():
            drift.append(rel)
    if drift:
        bad("skill-dir sync", "; ".join(drift[:6]))
        return False
    ok("skill-dir sync", f"{len(core)} files identical")
    return True


check("compile", c_compile)
check("templates-json", c_json)
check("matrix-sync", c_matrix)
check("cli-subcommands", c_cli)
check("art-clean", c_art)
check("gate-language", c_gate)
check("sections", c_sections)
check("skill-sync", c_sync)


def main():
    ap = argparse.ArgumentParser(description="3AM verification suite")
    ap.add_argument("--only", help="comma list of checks to run")
    ap.add_argument("--list", action="store_true", help="list checks and exit")
    args = ap.parse_args()
    if args.list:
        for name, _ in CHECKS:
            print(name)
        return 0
    only = set(args.only.split(",")) if args.only else None
    print(f"▸ 3AM verify · {ROOT}")
    failed = 0
    for name, fn in CHECKS:
        if only and name not in only:
            continue
        if not fn():
            failed += 1
    print(f"▸ {'ALL PASS' if failed == 0 else f'{failed} CHECK(S) FAILED'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
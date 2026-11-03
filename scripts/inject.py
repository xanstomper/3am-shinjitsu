#!/usr/bin/env python3
"""3AM Shinjitsu — mandate injector.

Prepends references/mandate.txt as the system message to any OpenAI-compatible endpoint
the operator controls (local routers, self-hosted gateways, agent CLIs). Stdlib only.

Usage:
  python3 inject.py --print                     # print mandate for manual paste
  SHINJITSU_BASE=http://localhost:8705/v1 \
  SHINJITSU_MODEL=<model> \
  python3 inject.py "objective: audit <authorized-target>"

Env: SHINJITSU_BASE (default http://localhost:8705/v1), SHINJITSU_MODEL,
     SHINJITSU_KEY (optional; omitted = local routers that need no key).
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.request

MANDATE = pathlib.Path(__file__).resolve().parent.parent / "references" / "mandate.txt"


def build_body(model: str, task: str) -> bytes:
    return json.dumps({
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": MANDATE.read_text()},
            {"role": "user", "content": task},
        ],
    }).encode()


def main() -> int:
    ap = argparse.ArgumentParser(description="3AM Shinjitsu mandate injector")
    ap.add_argument("--print", action="store_true", help="print mandate for manual paste")
    ap.add_argument("--base", default=os.environ.get("SHINJITSU_BASE", "http://localhost:8705/v1"))
    ap.add_argument("--model", default=os.environ.get("SHINJITSU_MODEL", ""))
    ap.add_argument("task", nargs="*", default=[])
    a = ap.parse_args()

    if a.print or not a.model:
        sys.stdout.write(MANDATE.read_text())
        return 0
    if not a.task:
        ap.error("task required unless --print")

    headers = {"Content-Type": "application/json"}
    if os.environ.get("SHINJITSU_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["SHINJITSU_KEY"]
    req = urllib.request.Request(
        a.base.rstrip("/") + "/chat/completions",
        data=build_body(a.model, " ".join(a.task)),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        out = json.load(r)
    sys.stdout.write(out["choices"][0]["message"]["content"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

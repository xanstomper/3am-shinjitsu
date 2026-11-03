#!/usr/bin/env python3
"""
3AM Arsenal Runner — scoped, read-only battery executor for the 3AM Shinjitsu mandate.

Enforces the P0 scope gate in code: refuses to fire without --scope-note.
Read-only probes only: GET/HEAD/OPTIONS, TLS SAN reads, banner grabs (greeting only),
third-party archive queries (CT logs, wayback, passive DNS). Zero credentialed attempts.
Noise budget per class (arsenal-index.md); --max-reqs hard cap; jitter between requests.

Output: JSON ledger lines (one per probe, campaign-state compatible) + verdict summary.

Usage:
  python3 arsenal.py --target example.com --scope-note "operator-owned, RoE ref #1"
  python3 arsenal.py --target example.com --scope-note "..." --classes network-edge,api --json ledger.jsonl
"""
import argparse, json, socket, ssl, sys, time, random, re, base64
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.9", "Upgrade-Insecure-Requests": "1"}
NOISE_BUDGET = {"network-edge": 12, "web-app": 16, "api": 8, "auth": 6, "llm": 4, "osint": 5}
BANNER_PORTS = [80, 443, 8083, 3306, 6379, 9200]
EOL_TABLE = [  # (regex, component, eol_note)
    (r"PHP[/ ]5\.", "PHP 5.x", "EOL 2015-2018"), (r"PHP[/ ]7\.[0-3]", "PHP 7.0-7.3", "EOL 2019-2021"),
    (r"PHP[/ ]7\.4", "PHP 7.4", "EOL 2022"), (r"nginx[/ ]1\.(1[0-7]|[0-9])\.", "nginx<1.18", "EOL 2020"),
    (r"Apache[/ ]2\.2", "Apache 2.2", "EOL 2017"), (r"MariaDB[ /]5\.5", "MariaDB 5.5", "EOL 2017"),
    (r"MariaDB[ /]10\.[0-3]", "MariaDB 10.0-10.3", "EOL 2019-2022"),
    (r"MySQL[ /]5\.[56]", "MySQL 5.5/5.6", "EOL 2018/2021"),
    (r"Node\.js[/ ]v?1?[0-9]\.", "Node<=19", "EOL"),
    (r"OpenSSH_([0-6]\.|7\.[0-7])", "OpenSSH<7.7", "EOL 2018"),
]

class Battery:
    def __init__(self, target, scope_note, classes, max_reqs, jitter, args):
        self.target = target.rstrip("/")
        self.scope = scope_note
        self.classes = set(classes)
        self.max_reqs = max_reqs
        self.jitter = jitter
        self.args = args
        self.scheme = "http" if getattr(args, "http", False) else "https"
        self.sent = 0
        self.per_class = {}
        self.ledger = []
        self.html_cache = None

    # ── ledger + noise ────────────────────────────────────────────────
    def log(self, cls, probe, test, result, verdict, score, next_test="none"):
        self.ledger.append({
            "ts": datetime.now(timezone.utc).isoformat(), "target": self.target,
            "class": cls, "probe": probe, "test": test[:200], "result": str(result)[:300],
            "verdict": verdict, "score": score, "next": next_test,
            "scope": self.scope})
        mark = {"CONFIRMED": "✓", "NEGATIVE": "✗", "HYPOTHESIS": "⚠"}.get(verdict, "·")
        print(f"  {mark} [{cls}] {probe}: {str(result)[:120]}")
        if verdict == "CONFIRMED":
            print(f"     ↳ next: {next_test}")

    def budget(self, cls):
        used = self.per_class.get(cls, 0)
        if used >= NOISE_BUDGET.get(cls, 8):
            self.log(cls, "noise-budget", "class ceiling", "EXHAUSTED — stopping class", "NEGATIVE", 0)
            return False
        if self.sent >= self.max_reqs:
            self.log(cls, "max-reqs", "--max-reqs cap", "BUDGET SPENT — stopping run", "NEGATIVE", 0)
            return False
        return True

    def req(self, cls, url, method="GET", headers=None, timeout=10):
        if not self.budget(cls):
            return None
        self.per_class[cls] = self.per_class.get(cls, 0) + 1
        self.sent += 1
        h = dict(HEADERS)
        if headers:
            h.update(headers)
        try:
            r = Request(url, headers=h, method=method)
            with urlopen(r, timeout=timeout) as resp:
                body = resp.read(400000)
                return {"code": resp.status, "headers": dict(resp.headers),
                        "ct": resp.headers.get("Content-Type", ""), "body": body}
        except HTTPError as e:
            return {"code": e.code, "headers": dict(e.headers or {}),
                    "ct": (e.headers or {}).get("Content-Type", ""), "body": e.read(400000)}
        except (URLError, socket.timeout, ssl.SSLError, ConnectionError, OSError) as e:
            return {"code": 0, "headers": {}, "ct": "", "body": b"", "err": str(e)}
        finally:
            if self.jitter:
                time.sleep(random.uniform(0.2, self.jitter))

    def run_class(self, name):
        fn = getattr(self, "cls_" + name.replace("-", "_"), None)
        if fn:
            print(f"▸ class {name}")
            fn()
        else:
            print(f"  · {name}: no battery in runner (see references/arsenal-*.md)")

    # ── class 1: network/edge ─────────────────────────────────────────
    def cls_network_edge(self):
        c = "network-edge"
        r = self.req(c, f"{self.scheme}://{self.target}/", timeout=12)
        if r and r["code"]:
            stack = " | ".join(f"{k}: {v}" for k, v in r["headers"].items()
                               if k.lower() in ("server", "x-powered-by", "via", "x-served-by",
                                                "x-kong-response-latency", "www-authenticate"))
            hits = [(rx, comp, eol) for rx, comp, eol in EOL_TABLE if re.search(rx, stack)]
            if hits:
                self.log(c, "era-stack", "curl -sI /", stack, "CONFIRMED", 80,
                         f"searchsploit {hits[0][1]} — documented PoC adaptation only ({hits[0][2]})")
            else:
                self.log(c, "era-stack", "curl -sI /", stack or "no stack headers", "NEGATIVE", 0)
            if "x-kong-response-latency" in stack or 'realm="service"' in stack:
                self.log(c, "kong-supabase-fingerprint", "headers", "Kong-fronted Supabase signature", "CONFIRMED", 90,
                         "GoTrue chain: arsenal-04 §4.1")
        else:
            self.log(c, "era-stack", "curl -sI /", r.get("err", "unreachable") if r else "budget", "NEGATIVE", 0)
        # TLS SAN
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((self.target, 443), timeout=8) as sock:
                with ctx.wrap_socket(sock, server_hostname=self.target) as s:
                    der = s.getpeercert(binary_form=True)
            import tempfile, subprocess, os
            with tempfile.NamedTemporaryFile(delete=False, suffix=".der") as f:
                f.write(der); path = f.name
            out = subprocess.run(["openssl", "x509", "-inform", "der", "-in", path,
                                  "-noout", "-ext", "subjectAltName"],
                                 capture_output=True, text=True, timeout=10).stdout
            os.unlink(path)
            sans = sorted(set(re.findall(r"DNS:([^,\s]+)", out)))
            base = self.target.replace("www.", "")
            fam = [s for s in sans if base not in s and "*" not in s][:8]
            self.log(c, "tls-san", "openssl s_client → SAN", f"{len(sans)} SANs, foreign: {fam}",
                     "CONFIRMED" if fam else "NEGATIVE", 75,
                     "probe foreign SAN hosts; JSON 404 = real router" if fam else "none")
        except Exception as e:
            self.log(c, "tls-san", "openssl s_client → SAN", f"error: {e}", "NEGATIVE", 0)
        # banner grabs (greeting only)
        for port in BANNER_PORTS:
            if not self.args.no_banner:
                try:
                    with socket.create_connection((self.target, port), timeout=4) as s:
                        s.settimeout(4)
                        banner = s.recv(256).decode("utf-8", "ignore").strip()
                    if banner:
                        verdict = "CONFIRMED" if re.search(r"(5\.5|5\.6|5\.4|2\.3|Redis|6379)", banner) else "NEGATIVE"
                        self.log(c, f"banner-{port}", f"connect :{port} read greeting", banner[:120],
                                 verdict, 85 if verdict == "CONFIRMED" else 0,
                                 "searchsploit per banner version" if verdict == "CONFIRMED" else "none")
                except Exception:
                    pass  # closed/filtered — silent, not a request spent
        # SPF/TXT origin leak
        if not self.args.no_dns:
            import subprocess
            for rec in (self.target,):
                try:
                    out = subprocess.run(["dig", "+short", rec, "TXT", "@1.1.1.1"],
                                         capture_output=True, text=True, timeout=10).stdout
                    ips = re.findall(r"ip4:([0-9.]+)", out)
                    cf_like = re.match(r"^(104\.(16|17|18|19|20|21)\.|172\.6[4-9]\.|188\.114\.)", ips[0] or "")
                    if ips and not cf_like:
                        self.log(c, "spf-origin-leak", f"dig +short {rec} TXT @1.1.1.1", f"origin candidate: {ips}",
                                 "CONFIRMED", 90, "direct-origin verify: http.client + Host/SNI, unverified TLS")
                    else:
                        self.log(c, "spf-origin-leak", f"dig +short {rec} TXT @1.1.1.1",
                                 ips or "no ip4 in SPF", "NEGATIVE", 0)
                except FileNotFoundError:
                    self.log(c, "spf-origin-leak", "dig", "dig not installed — skip", "NEGATIVE", 0)
                    break
                except Exception as e:
                    self.log(c, "spf-origin-leak", "dig", f"error {e}", "NEGATIVE", 0)

    # ── class 2: web app ──────────────────────────────────────────────
    def cls_web_app(self):
        c = "web-app"
        paths = ["/openapi.json", "/docs", "/redoc", "/swagger.json", "/api-docs", "/.env",
                 "/robots.txt", "/.well-known/security.txt", "/api/health", "/health",
                 "/status?json=1", "/.git/HEAD"]
        for p in paths:
            r = self.req(c, f"{self.scheme}://{self.target}{p}")
            if not r:
                return
            real = ("json" in r["ct"]) or (p in ("/.git/HEAD", "/robots.txt", "/.well-known/security.txt")
                                           and r["code"] == 200 and "html" not in r["ct"])
            body = r["body"][:200].decode("utf-8", "ignore")
            if real and r["code"] == 200 and "html" not in r["ct"]:
                verdict, score = ("CONFIRMED", 85) if p in ("/openapi.json", "/swagger.json",
                                    "/.env", "/status?json=1") else ("NEGATIVE", 0)
                self.log(c, f"probe{p}", f"GET {p} status+content-type pair",
                         f"{r['code']} {r['ct']} :: {body[:80]}", verdict, score,
                         "full route map free" if p == "/openapi.json" else "none")
            elif r["code"] not in (0,):
                self.log(c, f"probe{p}", f"GET {p} status+content-type pair",
                         f"{r['code']} {r['ct'][:40]}{' ghost' if 'html' in r['ct'] else ''}",
                         "NEGATIVE", 0)
        # ghost-route baseline
        r = self.req(c, f"{self.scheme}://{self.target}/_3am-nonexistent-{random.randint(1000,9999)}")
        if r and r["code"] == 200 and "html" in r["ct"]:
            self.log(c, "spa-ghost-baseline", "GET /_3am-nonexistent", "200 text/html = SPA fallback active",
                     "CONFIRMED", 75, "ALL 200s on this target need content-type pairing (arsenal-02 §2.2)")
        self.fetch_bundles()

    def fetch_bundles(self):
        c = "web-app"
        r = self.req(c, f"{self.scheme}://{self.target}/")
        if not r or r["code"] != 200:
            return
        html = r["body"].decode("utf-8", "ignore")
        srcs = re.findall(r'<script[^>]+src="([^"]+)"', html)[:3]
        for src in srcs:
            url = src if src.startswith("http") else f"{self.scheme}://{self.target}{src if src.startswith('/') else '/'+src}"
            br = self.req(c, url)
            if not br or br["code"] != 200 or len(br["body"]) < 100:
                continue
            js = br["body"].decode("utf-8", "ignore")
            envs = re.findall(r"VITE_[A-Z_0-9]+[:=][`'\"]?([^`'\",;]{1,80})", js)[:6]
            pm = len(re.findall(r"postMessage\(", js))
            backdoor = re.findall(r"\.id\s*===\s*(\d{2,})", js)[:4]
            sb = "supabase.co" in js
            self.log(c, f"bundle-mine {src[-40:]}", f"GET {url[-60:]} grep", 
                     f"env:{envs} postMessage:{pm} id-backdoor:{backdoor} supabase:{sb}",
                     "CONFIRMED" if (envs or backdoor or sb) else "NEGATIVE", 80,
                     "env-object = prod flags/keys; backdoor → cross-file consistency (arsenal-05 §5.3)"
                     if (backdoor or sb) else "none")
            if sb:
                self.cls_auth()  # auto-chain GoTrue probes within the auth budget

    # ── class 3: api ──────────────────────────────────────────────────
    def cls_api(self):
        c = "api"
        for p in ("/", "/api/", "/v1/"):
            r = self.req(c, f"{self.scheme}://{self.target}{p}", headers={"Origin": "https://example.net"})
            if not r:
                return
            acao = r["headers"].get("Access-Control-Allow-Origin", "")
            acac = r["headers"].get("Access-Control-Allow-Credentials", "")
            if self.target in acao or acao in ("*", "https://example.net", "null"):
                sev = "cookie-auth endpoints pending SameSite read (arsenal-03 §3.13)"
                self.log(c, f"cors-reflection{p}", f"GET {p} with Origin: https://example.net",
                         f"ACAO={acao} ACAC={acac}", "HYPOTHESIS", 70, sev)
            else:
                self.log(c, f"cors-reflection{p}", f"GET {p} with Origin: https://example.net",
                         f"ACAO={acao or 'none'}", "NEGATIVE", 0)

    # ── class 4: auth ─────────────────────────────────────────────────
    def cls_auth(self):
        c = "auth"
        for p in ("/auth/v1/health", "/auth/v1/settings"):
            r = self.req(c, f"{self.scheme}://{self.target}{p}", headers={"apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."})
            if not r:
                return
            if r["code"] == 200 and "json" in r["ct"]:
                self.log(c, f"gotrue{p}", f"GET {p} (apikey header)", r["body"][:150].decode("utf-8", "ignore"),
                         "CONFIRMED", 90, "full auth surface map: arsenal-04 §4.1")
            elif r["code"]:
                self.log(c, f"gotrue{p}", f"GET {p}", f"{r['code']} {r['ct'][:40]}{' ghost' if 'html' in r['ct'] else ''}",
                         "NEGATIVE", 0)

    # ── class 10: llm ─────────────────────────────────────────────────
    def cls_llm(self):
        c = "llm"
        r = self.req(c, f"{self.scheme}://{self.target}/v1/models")
        if r and r["code"] in (200, 401):
            self.log(c, "v1-models", "GET /v1/models", f"{r['code']} {r['body'][:100].decode('utf-8','ignore')}",
                     "CONFIRMED" if r["code"] == 200 else "NEGATIVE", 75,
                     "diff vs /status?json=1 hidden tier" if r["code"] == 200 else "none")

    # ── class 9: osint (third-party archives) ────────────────────────
    def cls_osint(self):
        c = "osint"
        base = ".".join(self.target.split(".")[-2:])
        r = self.req(c, f"https://crt.sh/?q=%25.{base}&output=json", timeout=20)
        if r and r["code"] == 200:
            try:
                names = sorted({n for row in json.loads(r["body"]) for n in
                                row.get("name_value", "").split("\n") if "*" not in n})
                self.log(c, "ct-logs", f"crt.sh %25.{base}", f"{len(names)} names: {names[:12]}",
                         "CONFIRMED" if len(names) > 3 else "NEGATIVE", 85,
                         "staging/sister hosts → passive DNS → mirror families")
            except Exception as e:
                self.log(c, "ct-logs", "crt.sh", f"parse error {e}", "NEGATIVE", 0)
        r2 = self.req(c, f"https://web.archive.org/cdx/search/cdx?url={base}/*&fl=original&collapse=urlkey&limit=300")
        if r2 and r2["code"] == 200:
            urls = r2["body"].decode("utf-8", "ignore").splitlines()
            params = sorted({m.group(1) for u in urls for m in [re.search(r"[?&](\w+)=", u)] if m})[:12]
            self.log(c, "wayback-cdx", "CDX url=<d>/* fl=original", f"{len(urls)} urls, params: {params}",
                     "CONFIRMED" if params else "NEGATIVE", 75,
                     "id-format oracle + removed routes (arsenal-02 §2.3)" if params else "none")

    # ── summary ───────────────────────────────────────────────────────
    def summary(self):
        n_conf = sum(1 for e in self.ledger if e["verdict"] == "CONFIRMED")
        n_neg = sum(1 for e in self.ledger if e["verdict"] == "NEGATIVE")
        n_hyp = sum(1 for e in self.ledger if e["verdict"] == "HYPOTHESIS")
        print(f"\n▸ ledger {len(self.ledger)} entries · {n_conf}✓ {n_neg}✗ {n_hyp}⚠ · "
              f"{self.sent} requests sent (cap {self.max_reqs})")
        for e in self.ledger:
            if e["verdict"] == "CONFIRMED":
                print(f"  ✓ {e['probe']} → {e['next']}")
        return self.ledger

def main():
    ap = argparse.ArgumentParser(description="3AM arsenal runner (read-only battery)")
    ap.add_argument("--target", required=True)
    ap.add_argument("--scope-note", required=True,
                    help="P0 scope lock: objective + authorization reference. Refuses without it.")
    ap.add_argument("--classes", default="network-edge,web-app,api,osint,llm,auth")
    ap.add_argument("--max-reqs", type=int, default=45)
    ap.add_argument("--jitter", type=float, default=1.0, help="max seconds between requests")
    ap.add_argument("--json", help="write ledger JSONL to this path")
    ap.add_argument("--http", action="store_true", help="plain HTTP scheme (local/self-hosted targets)")
    ap.add_argument("--no-banner", action="store_true")
    ap.add_argument("--no-dns", action="store_true")
    args = ap.parse_args()
    if len(args.scope_note) < 8:
        sys.exit("✗ P0 GATE: --scope-note too thin (objective + authorization reference required)")
    b = Battery(args.target, args.scope_note, args.classes.split(","), args.max_reqs,
                args.jitter, args)
    print(f"▸ 3AM ARSENAL · target {args.target} · scope: {args.scope_note}")
    for cls in args.classes.split(","):
        b.run_class(cls)
    ledger = b.summary()
    if args.json:
        with open(args.json, "w") as f:
            for e in ledger:
                f.write(json.dumps(e) + "\n")
        print(f"▸ ledger written: {args.json}")

if __name__ == "__main__":
    main()

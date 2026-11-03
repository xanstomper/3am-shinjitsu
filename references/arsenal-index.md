# 3AM Arsenal Index — the first-60-minutes battery

Run-now sequence, ordered by 3AM Score' = mean(E,I,L,R,N) × exp(−T/30min).
Every probe here is READ-ONLY. `[W]` = state change possible → revert-map first.
Noise budget per class: see table at bottom. Detailed batteries: `arsenal-01…10.md`.

## T+0:00 — zero-contact first (parallel, no target traffic)

| # | Probe | Test | Score' | Confirmed-when |
|---|---|---|---|---|
| 1 | CT-log pull | `curl -s 'https://crt.sh/?q=%25.<domain>&output=json' \| jq -r '.[].name_value' \| sort -u` | 85 | hidden/staging/sister hosts never in DNS |
| 2 | SPF/TXT origin leak | `dig +short <domain> TXT @1.1.1.1` → `v=spf1 ip4:<ip>` | 90 | an IP outside 104.21.x/172.67.x-class = origin candidate |
| 3 | Passive DNS | `curl -s https://api.hackertarget.com/hostsearch/?q=<domain>` | 80 | dead-DNS-live-cert hosts, staging family |
| 4 | Wayback CDX ghost diff | `curl -s 'https://web.archive.org/cdx/search/cdx?url=<domain>/*&fl=original&collapse=urlkey'` | 75 | removed routes, id-format oracle, old auth methods |
| 5 | Breach-context brief | `web_search <domain> breach leak ransomware` + ransomware.live | 80 | leak-site statement > victim PR; no-post-mortem = live root cause |
| 6 | Mirror/entrance brands | `tr.` / `giris.` / `<lang>.` subdomains from CT+DNS | 70 | separate-hosting mirrors = un-CDN'd surface |

## T+5 — first-contact era-stack (1 HEAD request)

| # | Probe | Test | Confirmed-when |
|---|---|---|---|
| 7 | Header stack | `curl -sI https://<domain>` | Server/X-Powered-By/via/x-kong-*/x-served-by fingerprints → EOL table (`arsenal-01` §1.12) |
| 8 | Kong-fronted Supabase | `www-authenticate: Basic realm="service"` + `x-kong-response-latency` + ACAH contains `apikey` | GoTrue chain unlocks (`arsenal-04` §3.1) |
| 9 | Origin-verify | `python3 http.client` → origin IP, `Host:`/SNI=<domain>, unverified TLS, expect real app HTML vs CF interstitial | full WAF bypass (`arsenal-01` §1.2) |

## T+8 — surface map (bounded, ≤20 req)

| # | Probe | Test | Confirmed-when |
|---|---|---|---|
| 10 | OpenAPI/docs | `curl -s -o /dev/null -w '%{http_code} %{content_type}' /openapi.json /docs /redoc /swagger.json /api-docs` | JSON 200 = full route map free |
| 11 | Ghost-route sweep | same command, pair status+content-type | `text/html` on JSON API path = SPA ghost / Access wall — classify, never verdict |
| 12 | CORS matrix | `curl -s -D - -o /dev/null -H 'Origin: https://evil.com' <each state-changing endpoint>` | ACAO reflection + `allow-credentials: true`; then read Set-Cookie SameSite before rating (`arsenal-03` §2.x) |
| 13 | security.txt | `curl /.well-known/security.txt` | bounty channel exists or deliverable = disclosure package |
| 14 | Health/IP-echo | `curl /api/health /health /status?json=1` | env flags, client_ip SSRF oracle, hidden-model map |
| 15 | TLS SAN | `openssl s_client -connect <host>:443 -servername <host> </dev/null 2>/dev/null \| openssl x509 -noout -ext subjectAltName` | hosts absent from DNS+bundle; JSON 404 on SAN host = live router |

## T+15 — bundle mining (passive after fetch, always `-w '%{http_code} %{size_download}'`)

| # | Probe | Test | Confirmed-when |
|---|---|---|---|
| 16 | Chunk discovery | webpack: `grep -oE '"\./[A-Za-z0-9_-]+\.js"' app.js`; Vite: extract `__vite__mapDeps` manifest; follow re-export stubs | lazy admin portal / auth wiring invisible in main bundle |
| 17 | Env-object dump | grep `VITE_[A-Z_0-9]+:` (backtick-aware: Vite strings are template literals) | prod flags ON, license keys, internal hosts |
| 18 | Schema-library extraction | locate zod/io-ts chunk → full request shapes → valid-shape authz matrix | gate-order proof without a session (`arsenal-03` §2.2) |
| 19 | Backdoor grep | `user.id === N`, `is_admin`, `window.hide*Gate`, `postMessage(` targets | client-only gates; map EVERY module independently |
| 20 | Socket factory decode | hostname templates, `path:`, `transports:`, EIO version | host+namespace+transport policy in one read |
| 21 | Anon-key harvest | `VITE_SUPABASE_ANON_KEY` / `supabase.co` refs | GoTrue surface map via `apikey` header |

## T+25 — auth plane (high-value first, ceiling 15 req)

| # | Probe | Test | Confirmed-when |
|---|---|---|---|
| 22 | GoTrue settings | `curl -H 'apikey: <anon>' /auth/v1/settings /auth/v1/health` | providers, autoconfirm flags, version = full auth surface |
| 23 | OAuth state binding | 2× /start → state A,B; `callback?state=A&code=fake` with cookie B | `Invalid OAuth state` = hardened (negative, ledger it) |
| 24 | redirect_uri override | `curl -s -o /dev/null -w '%{redirect_url}' '/auth/v1/authorize?provider=discord&redirect_uri=https://evil.com/cb'` | Location carries attacker URI verbatim → live-intercept (`arsenal-04` §3.2) |
| 25 | Auth-chain rate sweep | 15-20 rapid garbage POSTs per auth endpoint, `-w '%{http_code}'` | zero 429 = brute surface open |
| 26 | WS handshake+frames | real frame exchange (socket+ssl), NOT curl 101 | CLOSE 1008 on first frame = gate works (negative) |

## T+40 — decision point

Every probe above → ledger entry (`campaign-state.json`). Re-score. Remaining time goes to
the highest-Score' hypothesis from `arsenal-03` (API) and `arsenal-04` (auth), NOT to
wordlist spraying. Exhausted class = N/A'd with the exact test string, never re-probed.

## Noise budget (§12, hard ceilings)

| Class | Ceiling/burst | Cadence |
|---|---|---|
| Network/Edge | 10 req + banner grabs | 3-4s spacing; CF challenge → wait 75s, re-read SAME endpoint |
| Web app | 20 req | route maps once; never re-fetch unchanged bundle |
| API | 15 req/endpoint-class | bursts only on exchange endpoints, once |
| Auth/Identity | 15 req | NEVER leave a retry loop on a throttled auth plane — full-cold 2h |
| Client-side | passive | bundle fetches only |
| Infra/Hosting | 10 req | buckets/ping once |
| Supply-chain | passive | version matching offline |
| Breach/OSINT | zero target traffic | all third-party archives |
| LLM/AI | 5 req + 2×PTOK | PTOK off by default (`--ptok`) |

Bulk rule: >50 req total = chunk + read-only verify between batches. A probe that fails
twice is dead. Negatives are results.

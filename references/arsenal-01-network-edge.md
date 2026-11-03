# Class 1 — Network/Edge — Arsenal Battery

Era-stack → EOL table → banner-only ports → origin leak. This is the cartel shortcut:
prepared exploitation is the only minutes-class. Banner-grab ONLY unless RoE covers more.

## 1.1 Era-stack header grab (score 80, T≈1min)
- DECISIVE: `curl -sI https://<target>/` and on the API host separately
- READ: `Server`, `X-Powered-By`, `via`, `x-served-by`, `x-turbo-by`, `x-kong-*`,
  `www-authenticate`, `content-generator`, `x-generator`
- CONFIRMED WHEN: any component EOL per §1.12 table
- FP: CDN-injected headers (`via` from CF/Fastly is not the origin stack)

## 1.2 CF-origin leak → direct-origin WAF bypass (score 90, T≈3min) — THE first move
- DECISIVE: `dig +short <target> TXT @1.1.1.1` → grep `v=spf1 ip4:<ip>`
- VERIFY: python `http.client.HTTPSConnection(<ip>, context=ssl._create_unverified_context())`,
  `Host:`/SNI = `<target>`. Real app HTML (not CF interstitial) = WAF bypassed entirely.
- ALSO: `dig AAAA` — IPv6 often un-CDN'd (shadow surface); check DMARC `rua`/hosting MX headers.
- FP: SPF `include:` chains — resolve the IP in the include, not the include name.
- NEXT: full route map direct-to-origin; re-run ghost-route sweep origin-side (CDN may mask).

## 1.3 TLS SAN hidden-host discovery (score 75, T≈2min)
- DECISIVE: `echo \| openssl s_client -connect <host>:443 -servername <host> 2>/dev/null \| openssl x509 -noout -ext subjectAltName`
- CONFIRMED WHEN: SAN names absent from DNS enumeration AND bundle strings.
- DISCRIMINATOR: probe SAN children — JSON 404 = real router; HTML 404 = SPA shell (ghost).
- Wildcard parent may be a live backend while children don't resolve.

## 1.4 EOL-panel port banner set (score 85, banner-only)
- DECISIVE: one connect + read per port, 5s timeout: 21, 25, 110, 143, 3306, 5432, 6379,
  8083, 9200, 2379, 10250, 5984
- SIGNATURES: `:8083` title "Vesta"/"Hestia" (EOL panel); `:3306` greeting `5.5.x`/`5.6.x`
  MariaDB/MySQL (EOL 2018/2020, internet-reachable = the finding); `6379` Redis greeting
  (anon = instant read class); `9200` ES cluster name; `2379` etcd; `10250` kubelet.
- HARD RULE: greeting/banner read only. Zero credentialed attempts without RoE.
- CONFIRMED WHEN: EOL service + internet-reachable + version leaks in banner.

## 1.5 EOL version table (match everything §1.1/§1.4 leaks)

| Component | EOL since | Where it leaks |
|---|---|---|
| PHP 5.x | 2015-2018 | `X-Powered-By`, VestaCP-era 301 path leaks |
| PHP 7.0–7.3 | 2019-2021 | same |
| MariaDB 5.5/10.0 | 2017-2019 | `:3306` greeting |
| MySQL 5.6/5.7 | 2021/2023 | greeting |
| Node <12/14 | 2019/2021 | error pages, `Server: Node` |
| nginx <1.18 | 2020 | `Server` line |
| Apache 2.2 | 2017 | `Server` line |
| OpenSSH <7.7 | 2018 | `ssh` banner |
| vsFTPd 2.x | 2015 | `21` banner |
| Exim <4.92 | 2019 | `25` banner |
| Tomcat 7/8 | 2021 | error pages |
| GoTrue <2.100 | version-pinned CVEs | `/auth/v1/health` |
| Kong <2.x | CVE-2020-11710 class | `x-kong-*` headers |

- WORKFLOW: `searchsploit <component> <version>` for EVERY fingerprinted EOL version →
  documented-PoC adaptation only (§15 wall). Log each match with its exact version string.

## 1.6 Nuclei exposure sweep (score 70, T≈4min, ceiling 1 run)
- DECISIVE: `nuclei -u https://<target> -tags cve,exposure,panel -rl 10 -severity medium,high,critical -silent`
- RULE: one run, rate-limited. Never re-run without a target change (ledger).
- FP: template matches on CDN-edge paths — verify each match by hand before verdict.

## 1.7 Dead-DNS-live-cert hosts (score 75)
- DECISIVE: passive-DNS dump (hackertarget hostsearch) ∩ CT-log names ∖ resolving names.
- CONFIRMED WHEN: `crt.sh` shows cert for a name with no A/AAAA on two public resolvers —
  "internal control panel" signature; try `https://<name>` via origin IP + Host header.

## 1.8 Mirror/entrance brands (score 70)
- PATTERN: `tr.<brand>`, `giris.<brand>` (TR entrance pattern), `<lang>.<brand>`,
  `<brand>-<market>` — separate hosting from CT logs + passive DNS.
- CONFIRMED WHEN: mirror on different ASN/IP-family than main = un-CDN'd, un-WAF'd surface.

## 1.9 Host-header injection (score 65) [ONE request, off-peak]
- DECISIVE: `curl -s -H 'Host: evil.com' https://<target>/password-reset -d 'email=x@y.z'`
  → inspect reset link host in any response body / downstream email (operator-supplied box).
- CONFIRMED WHEN: reset URL carries attacker host (reset poisoning / cache poisoning).
- FP: absolute-URL builders that re-derive host server-side.

## 1.10 IP-honoring / limiter keying (score 60)
- DECISIVE: same request twice, `X-Forwarded-For: 1.2.3.4` vs without — diff response.
- DISCRIMINATOR: CF-fronted → XFF/CF-Connecting-IP from client = **403 error 1000** (they're
  stripped; spoofing impossible). A 1000 IS the finding that limiter is real-IP-keyed.
- CONFIRMED WHEN: non-CF origin honors XFF for rate-limit buckets → rotation bypass.

## 1.11 Request-smuggling differential (score 55) [owned infra only]
- ONE CL.TE differential probe max; timing-only. Any ambiguity = stop, document, never iterate.
- Serverless/CDN-fronted (no dual proxy layer) = N/A — say once, pivot.

## 1.12 Edge-CVE triage ladder (cartel class)
- Fortinet (SSL-VPN portal title/banner), Pulse, Citrix, Ivanti, Versa, SOHO routers:
  fingerprint version from login page assets/JS, match against documented CVEs with PUBLIC
  PoCs, verify patch status from vendor advisories, adapt minimally, one decisive test.
- Re-validating a published exploit whose decisive test is state-changing = FORBIDDEN (§2).
  Verify the writeup's patch/disclosure status and cite as historical instead.

## 1.13 Exhaustion ledger template (class 1)
```
{"class":"network/edge","probe":"3306-banner","test":"connect :3306 read greeting",
 "result":"5.5.5-10.1.48-MariaDB","verdict":"CONFIRMED","score":85,
 "next":"searchsploit mariadb 10.1 — documented PoC adaptation only"}
```

# Edge gates & auth redirects — read-only classification

A custom block page ("IP or Country blocked", "Access denied", CF 1015/1016) is a
CONTROL to classify, not a dead end. Differential ladder, all read-only:

1. `curl` the path (plain) → block page?
2. Same-origin `fetch()` from the SPA page context (real browser fingerprint + cf_bm
   cookie) → 200 or block?
   - curl blocked / browser 200 → fingerprint-keyed (TLS/JA3 + cookie). Tool-curl will
     never pass; only the browser harness will.
   - browser blocked on SOME paths, not others → path-scoped rules exist; the SPA's own
     boot calls are the allowlist. Read them via
     `performance.getEntriesByType('resource')` → `responseStatus` per URL — the app's
     own network log is the WAF's documentation.
3. Budget escalation: re-fetch a URL that returned 200 earlier (even with the SPA's exact
   captured parameter) — if it now 403s for everyone, the gate is a per-IP request
   budget that tripped. That is an abuse control WORKING; stop probing the class, ledger
   "budget exhausted" (decays in hours), do not report it as a bypass or vulnerability.
4. Origin-reach tell: a response that is the real backend framework JSON
   (`{"success":false,"message":"Not Found"}`) instead of the WAF's HTML page means the
   edge let you through. This distinguishes "blocked at edge" from "404 at origin" and
   confirms path existence.
5. Block pages differ byte-wise per rule set (e.g. 30693 vs 29579 bytes). Compare sizes
   across hosts and mirror brands: identical → same rule set; different → asymmetric WAF
   surfaces worth probing.
6. Socket.IO backend: polling handshake answering
   `{"code":0,"message":"Transport unknown"}` = websocket-only. Liveness check:
   `new WebSocket('wss://host/path')` from the page context — OPEN vs ERROR, read-only.

## Auth-provider redirect capture (before driving any login form)
- When a login button hops to an external IdP, capture the FULL redirect URL from the
  click (don't just follow it): `openid.realm`, `openid.return_to`, and ticket params
  (`e`/`h`/`s` style) reveal the trust anchor and whether return_to is pinned to a
  dedicated login host.
- Rotating login-infra domains (`loginN.<brand>.com` series) are CF-fronted API-only
  hosts — root returns an empty 404. DNS + banner ONE, then probe adjacent numbers to
  map the series; realm-pinning to the series is an anti-phishing control, not a flaw.
- Record the IdP form's field layout before invoking vault save (Steam:
  steamcommunity.com/openid/loginform/, username id `«r3»`, password `«r4»`, guard code
  `authcode` — the guard prompt arrives after password submit; have the enter_code path
  ready).

## Jurisdiction gates — classify the deny before hunting a bypass
- Geolocate the agent's OWN egress first (`curl -s ipinfo.io/json`): the cf-ray suffix
  on any response names the serving PoP. A residential/class-1 egress still denied
  means a jurisdiction rule; a datacenter ASN denied means IP-reputation. Root-cause
  the deny from what you are before spending requests on what they block.
- A hard block that persists across curl v4, curl v6, a spoofed browser UA, AND the real
  browser harness is IP-class/jurisdiction keyed, not fingerprint keyed. Confirm the
  jurisdiction read with two zero-contact checks: the target's own region-blocker text
  surfaced in Google's index of its pages, and the prohibited-GEO list on its affiliate
  program (search `<brand> affiliate prohibited GEO` — review aggregators publish the
  country list verbatim).
- `server-timing: cfEdge;dur=<n>,cfOrigin;dur=0` on a 403 means the origin was never
  touched — pure edge rule. Do not spend further requests hunting origin-reach tells.
- A jurisdiction deny is a STOP for access testing, not a vantage problem: switching
  egress to evade it is unauthorized access stacked on a legal control. The sanctioned
  door is the target's own disclosure/bounty program — verify it exists and pays from
  public writeups, then name it in the closeout instead of a bare "wall".

## Edge-closed pivots — map the target with zero further contact
- Google's verified-bot path renders the SPA through the same WAF: `site:<apex>` plus
  `site:<apex> <feature-keyword>` queries return the route map, rendered component text
  (region blockers, policy language), and embedded algorithm code (seed formats, verifier
  implementations) in snippets alone. Layer in careers/LinkedIn postings for the backend
  stack (framework, ORM, DB, queues) and affiliate-program review pages for platform +
  contacts.
- A domain that SERVFAILs at BOTH the local resolver and a public DoH resolver
  (`curl 'https://1.1.1.1/dns-query?name=<host>&type=A' -H 'accept: application/dns-json'`
  → `EDE(22): No Reachable Authority`) is dead at delegation, not locally filtered —
  recover its published content from the Wayback replay, not by re-resolving.
- Wayback CDX and replay are independent services: when CDX answers "Temporarily
  Offline", replay can still serve — fetch a known capture with
  `curl -sL --compressed 'https://web.archive.org/web/<timestamp>id_/<url>'`. The `id_`
  suffix returns raw archived bytes; without `--compressed` the body arrives gzip-wrapped.
- A published exploit writeup is a HISTORICAL finding: assume patched until proven
  otherwise (read the writeup's aftermath/disclosure section via its Wayback replay if
  the origin DNS is dead). Never re-validate one whose decisive test requires
  state-changing operations — that is impact execution, RoE-forbidden.

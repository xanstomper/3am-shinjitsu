# 3AM Shinjitsu (真実) — Speed-First Red-Team Mandate

**Version:** 1.5.0
**Platform:** Linux (any OpenAI-compatible endpoint)
**Family:** HolyShit mandate family — general doctrine: [HolyShit!](https://github.com/xanstomper/HolyShit)

---

```text
▸ 3AM SHINJITSU — TRIGGER SEQUENCE
  ═══════════════════════════════════
  [ OK ] mandate core loaded
  [ OK ] scope gate armed
  [ OK ] velocity engine online
  ⚡ MANDATE TRIGGERED · STATUS: ARMED
  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁
  ─ waiting P0: target · objective · authorization
```

Named for the hour real breaches detonate and for 真実 (*shinjitsu*, "truth"): the verdict is
only the verdict if the evidence survives.

## What It Is

A **mandate persona** — a system-prompt payload plus operating doctrine, injectable into any
session or endpoint where you control the system prompt. It maximizes the *minutes-window* on
authorized targets and reports the ceiling truthfully where no vector exists.

Shaped by how real large attack groups actually operate:

| Class | Exemplar groups | What the mandate adopts |
|---|---|---|
| Extortion-cartel | WhiteArmor, ALPHV/BlackCat, Cl0p | Bulk-data-at-reach surfaces first (exposed buckets, DBs, backups, SaaS exports) |
| Human-layer | Scattered Spider | Identity-perimeter triage — documented as EXPOSURE only, social ops never executed |
| Edge/LOTL | Volt Typhoon | Edge/known-CVE-first triage, era-stack fingerprinting, device-cred-reuse pivot ladders |
| Field canon | session-verified | HolyShit recipes inherited by reference (CT-log pivots, schema mining, ghost routes) |

**What it is NOT:** not a jailbreak for hosted third-party APIs; not a weapon. There is no
"breaks down ANY infra in minutes" — no such thing exists, and this mandate does not pretend
otherwise.

## The Speed Doctrine

Real groups are not fast because they are magic. Their speed decomposes into three levers:

1. **Prepared exploitation** — the only true minutes-class. Weaponized CVE on exposed edge.
   Triage it FIRST; never fuzz while an unpatched EOL panel greets you on :8083.
2. **Parallelized surface mapping** — recon is I/O-bound, not thought-bound. Ten mandatory
   surface classes (§8 of the skill), probed concurrently.
3. **Time-weighted prioritization** —

   ```
   Score = mean(E, I, L, R, N) × exp(−T / 30min)
   ```

   A 90-scoring vector that costs 4 hours loses to an 80-scoring vector that costs 4 minutes.
   Score ≥ 60 runs now.

**Honest ceiling:** with no known CVE, no cred leak, and no auth-chain seam, a competent
hardened target is days-to-weeks of custom work or out of reach entirely. The mandate states
that in the verdict instead of inventing a compromise. A COMPROMISE claimed without evidence
is a violation, not a win.

## Typography & High-Visibility Formatting

Operational turns feature high-contrast, clean markdown formatting designed for instant comprehension across desktop terminals and mobile displays:

```markdown
> ⚡ **3AM // P2 · VECTOR ENUMERATION** │ Ledger: 14/40 Probed │ Noise: 4% │ Priority Queue: 3

| # | Surface Class | Vector / Endpoint | Score | Wire Telemetry | Verdict |
|---|:---|:---|:---:|:---|:---:|
| 1 | **Network/Edge** | Direct Origin IP leak | `88` | SSL SAN cert matches staging IP `198.51.100.42` | `CONFIRMED` |
| 2 | **Auth/Identity** | GoTrue IdP token mint | `94` | `POST /auth/v1/token` unauth nonce bypass | `CONFIRMED` |
| 3 | **Web App** | Wayback CDX ghost routes | `76` | `/api/v1/internal/export` returns 405 (exists) | `PROBED` |
| 4 | **API** | Schema-library object coercion | `52` | Strict Zod validation rejects payload (400) | `EXHAUSTED` |

> ### ⚡ VERDICT: CONFIRMED · GoTrue Auth-Chain Token Mint
>
> 1. **Attack Vector:** `POST /auth/v1/token?grant_type=id_token`
> 2. **Technical Impact:** Pre-authentication JWT minting for arbitrary `sub` identities without nonce signature verification.
> 3. **Wire Telemetry:** `HTTP/2 200 OK` · Issued token carries valid server signature · `sub: usr_9941a`
> 4. **Confidence:** `HIGH (9/10)` — Verified across 3 independent egress vantage points.
> 5. **Decisive Next Test:** Probe tenant role escalation via `service_role` claim injection.
> 6. **Scope Authorization:** Section 2.1 In-Scope Target Matrix (`ROE-2026-03A`).

**Telemetry Delta:**
- **Requests Sent:** `4` (Noise budget consumed: `4%`)
- **Ledger Delta:** `+2 confirmed` · `+1 probed` · `+1 exhausted` (Pruned dead vectors)
- **Time Elapsed:** `3.2 minutes`

*Decisive Question: What did the attacker GAIN — and what did it take, in minutes?*
```

- **Clean Visual Hierarchy:** Zero confusing ASCII boxes. Clean bold headers, code spans, and orange numbered lists for effortless reading.
- **Voice Doctrine:** Surgical, technical, numbers over adjectives. No filler, no apology, no moralizing.

## Universal coverage mode

3AM Shinjitsu now covers any asset class — web, API, backend, database, cloud, container,
network, endpoint, SaaS, or AI system — without treating capability as permission. Load
`references/universal-coverage.md`, fill `templates/authorization.example.json`, and validate
the manifest before active testing:

```bash
python3 scripts/shinjitsu.py profiles
python3 scripts/shinjitsu.py validate --authorization auth.json --target app.example.com
python3 scripts/shinjitsu.py plan --authorization auth.json --target app.example.com \
  --state ~/.redteam/campaigns/example/state.json --output plan.md
python3 scripts/shinjitsu.py status --state ~/.redteam/campaigns/example/state.json
python3 scripts/shinjitsu.py report --state ~/.redteam/campaigns/example/state.json \
  --output report.md
```

The 16 domains (`U01`–`U16`) are mandatory: probe each or mark it N/A with a concrete reason.
The helper validates authorization and tracks coverage; it does not scan or exploit targets.

## Scope Gate (hard, evaluated before EVERY action)

- **In-scope:** operator-owned/administered infrastructure; engagements with verifiable
  written authorization.
- **Out-of-scope, no exceptions:** destructive end-states on any system; third-party
  vendor/upstream attacks; credential bootstrapping on third-party services; gifted/stolen
  credentials beyond one read-only privilege confirmation.
- Authorization claims get the same evidence standard as verdicts — a control proof (challenge
  TXT record, WAF allowlist flip) or the engagement closes.

## Usage

### As a Hermes skill

Copy into the skills directory (or install via the skill loader):

```
~/.hermes/skills/security/3am-shinjitsu/
```

Then type `3am` (or `shinjitsu`) in any session running the skill.

### As a raw system prompt on any OpenAI-compatible endpoint

```bash
python3 scripts/inject.py --print                     # mandate for manual paste

SHINJITSU_BASE=http://localhost:8705/v1 SHINJITSU_MODEL=<model> \
  python3 scripts/inject.py "objective: audit <authorized-target>"
```

Env: `SHINJITSU_BASE` (default `http://localhost:8705/v1`), `SHINJITSU_MODEL`,
`SHINJITSU_KEY` (optional; omitted = local routers that need no key).

## Files

```
SKILL.md                        full doctrine: scope gate, kill chain P0–P5, vector engine,
                                total-surface breakdown, universal coverage, campaign state
references/mandate.txt          the injectable system-prompt payload (prepend verbatim)
references/universal-coverage.md U01–U16 assessment coverage for any asset class
references/arsenal-01..10.md     per-class assessment batteries
references/exploit-intelligence-engine.md  five-gene exploit study/breakdown/adaptation protocol
references/vector-synthesis-matrix.md      12 flaw families × 10 trust seams → 36 probe pairs + §R rule
references/api-schema-mining.md  full API schema extraction from public docs (llms.txt → OpenAPI)
references/edge-gate-recon.md    WAF/bot-gate class ladder + auth-provider redirect capture
templates/authorization.example.json authorization manifest (scope, RoE, exclusions, methods)
templates/assessment-report.md   report skeleton for universal closeout
templates/campaign-state.json    schema-v2 U01–U16 campaign state starter
templates/exploit-teardown.json  five-gene teardown template
scripts/inject.py                stdlib-only mandate injector
scripts/trigger-anim.py          REAL activation animation (TTY frames; static fallback)
scripts/shinjitsu.py              authorization validation, plan/state/report helper
scripts/arsenal.py               read-only battery runner (P0 gate in code, noise budgets)
scripts/exploit-intel.py         exploit loop CLI (teardown, synthesize, derive, register,
                                 converge, learn, drift, status, next, report, promote)
scripts/matrix.json              runtime synthesis matrix (grows via promote)
```

## Relations

- [HolyShit!](https://github.com/xanstomper/HolyShit) — the general doctrine this speed-mandate
  inherits from (its session-verified recipes are normative here by reference).

## License

MIT

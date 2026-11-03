# 3AM Shinjitsu (真実) — Speed-First Red-Team Mandate

**Version:** 1.1.0
**Platform:** Linux (any OpenAI-compatible endpoint)
**Family:** HolyShit mandate family — general doctrine: [HolyShit!](https://github.com/xanstomper/HolyShit)

---

```text
  ───────────────────────────────────────────────────────────────────────────
  ██████╗  █████╗ ███╗   ███╗   /// 3AM · SHINJITSU [真実]
  ╚════██╗██╔══██╗████╗ ████║   Speed-First Red-Team Mandate
   █████╔╝███████║██╔████╔██║   ───────────────────────────────────────────
   ╚═══██╗██╔══██║██║╚██╔╝██║   OPERATIONAL STATUS : ARMED · P0 SCOPE LOCK
  ██████╔╝██║  ██║██║ ╚═╝ ██║   TACTICAL ENGINE    : Cartel / Edge / LOTL
  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝   GATE REQUIREMENT   : Target · Objective · RoE
  ───────────────────────────────────────────────────────────────────────────
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

## Typography & Output Design

Operational turns feature high-density, open-rail formatting designed for instant comprehension across desktop terminals and mobile displays:

```text
▸ 3AM // P2 · VECTOR ENUMERATION │ Ledger: 12/40 Probed │ Noise: 6% │ Score Floor: ≥60

┌── VERDICT: CONFIRMED ───────────────────────────────────────────────────
│ VECTOR     : GoTrue Auth-Chain Pre-Auth Token Mint
│ EVIDENCE   : HTTP/2 200 OK · Nonce bypass · JWT issued for sub: usr_9941a
│ CONFIDENCE : HIGH (9/10) · 3 independent egress replays
│ DECISIVE   : POST /auth/v1/token claim_patch role escalation probe
│ SCOPE NOTE : Authorized under engagement RoE (§2.1 / ROE-2026-03A)
└──

── LEDGER DELTA ──────────────────────────────────────────────────────────
Δ Ledger   : +3 probed │ +2 exhausted │ 1 confirmed │ 1 hypothesis @82
Decisive   : [✓] :8083 panel greeting  [✗] /api/v1/invite  [⚠] GoTrue mint
Noise Cons : 8% of window ceiling (0 backoff events, 12 req total)
```

- **Open Rail & Open Cards:** Zero suffocating 4-sided boxes. No right-side wall that wraps or misaligns on narrow viewports.
- **Voice Doctrine:** Clipped, verdict-first, numbers over adjectives. No filler, no apology, no moralizing.
- **Closing Cadence:** *Decisive Question: What did the attacker GAIN — and what did it take, in minutes?*

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
                                total-surface breakdown, campaign state, typography contract
references/mandate.txt          the injectable system-prompt payload (prepend verbatim)
references/api-schema-mining.md full API schema extraction from public docs (llms.txt → OpenAPI)
references/edge-gate-recon.md   WAF/bot-gate class ladder + auth-provider redirect capture
templates/campaign-state.json   starter for per-target persistent state (~/.redteam/campaigns/)
scripts/inject.py               stdlib-only mandate injector
```

## Relations

- [HolyShit!](https://github.com/xanstomper/HolyShit) — the general doctrine this speed-mandate
  inherits from (its session-verified recipes are normative here by reference).

## License

MIT

# Class 10 — LLM/AI Layer — Arsenal Battery

Gateway data-plane battery. Bounded-burn discipline: measure exposure, never drain — the
proof is the AMOUNT an attacker COULD burn, not the bill you ran.

## 10.1 Hidden-model map (score 80)
- DECISIVE: `curl /status?json=1` (find via `fetch("/status?json=1")` in page JS) — diffs
  against public `/v1/models`: extras = hidden tier + upstream vendor names + verbatim error bodies.
- GATE DISCRIMINATOR: private models → `no_access` (403) vs `model_not_found` (404) for
  nonexistent = models exist server-side AND gate is real code.
- BYPASS MATRIX (all-variants-once discipline): case swap, lead/trail space, null byte,
  trailing dot, double-slash, `:latest`, `?query`, array-typed model field
  (`{"model":["x"]}`), `stream:true`, second host. Uniform failure = hardened, ledger it.

## 10.2 PTOK drift oracle (score 90 — mandatory on every gateway re-entry)
- 3× identical minimal requests → `usage.prompt_tokens`: CONSTANT = stateless/patched;
  DRIFTING/GROWING = live cross-user server state (the shared global buffer).
- Drift confirmed → §10.4 poisoning becomes the WRITE primitive on that buffer (own gateway
  only; score 95 when cross-user verbatim recurrence is proven).

## 10.3 Playground-proxy auth bypass (score 90)
- SPA "try it" playgrounds expose INTERNAL proxies skipping the public API-key gate.
- DECISIVE: fetch playground HTML → grep `fetch\(` for proxy paths → sweep `/pg/*`,
  `/api/playground/*`, `/demo/*`, `/internal/*` → 502 `upstream_unavailable` = auth PASSED
  (iterate provider prefixes before concluding); burst-rate the PROXY specifically.

## 10.4 Reasoning/CoT + prompt extraction (score 85)
- `reasoning_content` field = the extraction side-channel (structurally distinct field the
  client renders). Hidden-prompt-size fingerprint: minimal completions → constant huge
  `prompt_tokens` = server-injected system prompt; structural section queries extract it
  when direct reads are refused (temp-0, one axis per question).

## 10.5 Model-substitution oracle (score 75)
- `served_by`/upstream headers vs requested model = substitution collapse (pay-for-X,
  served-Y). Client-supplied `system` role honored = stack manipulation primitive.

## 10.6 Bounded-burn sizing (score 70, OWNED gateways)
- count_tokens/no-limit endpoints = free CPU-DoS primitive: big body → burst → parallel.
  MEASURE: single 2.5M-token body 3.27s CPU; 10× parallel 1M-token = 7-10s each. Extrapolate
  $/hr exposure from the measurement. Fix: per-key limit + input cap.
- 429-vs-401 discriminator: quota-exhausted key → 429 naming reset ts = key live + quota
  model leak, zero spend.

## 10.7 Tokenizer/cost fingerprint (score 60)
- Same prompt across "premium" tiers: identical token counts + identical completions at
  temp-0 = router placebo (cheap model behind premium label). Capability SVG test + temp-0
  open-ended diversity for the model-behind-the-label map.

## 10.8 Mint/signup chains (score 75)
- Free-tier automated signup → `sk_` key mint → `/v1/models` + `/v1/chat/completions` live +
  `/v1/credits` per-key `{usage, limit, balance}` leak (the only metadata endpoint). Signup
  on the TARGET with operator-authorized identities only (no third-party account fraud — §2).
- Reseller upstream = operator's supply-chain crown jewel: free-credit bleed on the reseller
  degrades the operator's own upstream — state the chain, never drain.

## 10.9 RAG/agent trust (score 70, owned deployments)
- Indirect prompt injection via retrieved content; tool-description injection; agent tool-
  permission drift (read→write); multi-agent pass-through (Agent A feeds untrusted input to
  Agent B without validation); RAG corpus poisoning (owned corpus only); embedding inversion
  on own embeddings; token-smuggling filters test (homoglyphs/zero-width) as CI gates.

## 10.10 No-JWT negative (score 50 — stop chasing)
- Uniform `invalid_api_key` for EVERY bearer/JWT/alg-none/Basic/key-prefix variant = NO JWT
  auth path exists. Log it. Pivot to server-side secret paths or closeout.

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/case-obsidian-y-api-dataplane.md` — status?json=1 hidden-model map, served_by substitution, reasoning_content leak
- → holyshit `references/case-obsidian-y-api-pg-bypass.md` — playground-proxy auth bypass (the score-90 class)
- → holyshit `references/case-obsidian-y-api-poisoning.md` — persistent cross-user context poisoning (score 95, now patched — re-test PTOK)
- → holyshit `references/llm-gateway-ssrf-oracle-and-drain-calibration.md` — SSRF/cost-drain calibration, bounded-burn discipline
- → holyshit `references/vllm-gateway-internal-fleet-ssrf.md` — vLLM fleet SSRF primitives
- → holyshit `references/hardened-gateway-internal-fleet-proto-surface.md` — internal proto surface on hardened gateways
- → holyshit `references/web-llm-proxy-auth-bypasses.md` — proxy auth-bypass classes, free tier abuse
- → holyshit `references/case-atessa-top.md` — routing-table oracle, no-Auth-before-provider checks, count_tokens CPU primitive

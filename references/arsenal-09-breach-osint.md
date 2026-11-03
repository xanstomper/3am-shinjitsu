# Class 9 — Breach-context/OSINT — Zero-Contact Battery

All third-party archives, zero target traffic. The attacker's leak-site statement outranks
the victim's PR. This class writes the BRIEF that shapes every other class.

## 9.1 Breach-context search (score 80)
- `web_search <target> breach leak ransomware` + ransomware.live + Breachsense-class trackers
  + news. Corroborate what the victim CONFIRMED ("withdrawal requests were added to the
  database" = proven DB-write access) before theorizing.
- FULL WORKED CASE: `case-gamdom-adjacent-infra.md` (holyshit refs, normative by reference).

## 9.2 Regulator-leak archives (score 75)
- Curacaofiles-class operator dossiers: P&L, org charts, passports, M&A via download API
  (`breach-regulator-osint.md`). Doc-priority order, pdftotext/OCR ceilings, PII minimality.

## 9.3 Forensics cascade (score 70)
- Wire → aggregators → forensic blogs: drain timelines, attacker/consolidation addresses,
  mixer flows, chaser dust.
- "No post-mortem published" + rushed rebuilt stack = HIGHEST-priority live brief: root cause
  possibly unfixed; focus the whole engagement on the rebuilt surface.

## 9.4 CT-log pivot ladder (score 85, zero contact)
- `curl -s 'https://crt.sh/?q=%25.<domain>&output=json' | jq -r '.[].name_value' | sort -u`
- Chain: CT names → partner brands (bundle `/providers/<brand>-originals`) → mirror/entrance
  hosts → passive DNS → bare-AWS origins. Dead DNS ≠ dead server: live cert + stripped DNS =
  "internal control panel" signature (→ §1.7).

## 9.5 PTR/whois funnel (score 65)
- PTR-reverse EVERY infra IP, then whois every name in the funnel — panel boxes and vendor
  mail servers identify themselves. Unregistered-but-linked names = registration takeover
  executable same-day for the price of a domain.

## 9.6 Drift oracles — fire FIRST on every re-entry (score 90, mandatory)
- PTOK drift (LLM targets): 3× identical 1-word requests → `usage.prompt_tokens`: constant =
  stateless/patched; drifting = shared buffer re-emerged (highest-value re-find).
- Bundle-hash diff (§2.8), wayback CDX diff (§2.3), wall-shape re-verify (403 → 500 drift).
- TOP prior compromisables were patched between sessions — re-asserting without a fresh test
  is a stale-finding ERROR.

## 9.7 Target-dead triage (score 60)
- Ladder: `dig +short <host> @1.1.1.1` AND `@8.8.8.8` (both empty = global no-record) →
  `getent hosts` apex/www/api spread → wayback availability API → whois against the TLD
  registry (`whois -h whois.nic.<tld>`) → split registered-but-DNS-stripped (registrar hold/
  takedown — re-check later, baseline moot) from dropped (expired — engagement closed).
- A baselined target going dark IS a finding — report it as one.

## 9.8 Breach PII minimality
- Sample ≤3 rows to prove access, redact at capture, never exfiltrate corpora. The verdict
  needs the PROOF, not the PII.

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/breach-regulator-osint.md` — forensics cascade, regulator-leak archives, doc-priority order
- → holyshit `references/case-gamdom-com.md` — WhiteArmor breach brief: leak-site statement > victim PR
- → holyshit `references/case-gamdom-adjacent-infra.md` — CT→partner→mirror→passive-DNS ladder, breach-context OSINT
- → holyshit `references/provably-fair-verification.md` — game-integrity auditing for gambling targets
- → holyshit `references/engagement-vantage-policy.md` — traffic attribution: engage from the VM, never the home IP

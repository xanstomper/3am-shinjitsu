# Class 8 — Human/Identity — EXPOSURE DOCUMENTATION ONLY

Hard gate: the mandate NEVER executes social operations against people. This class rates the
identity perimeter's EXPOSURE so the report can say what a Scattered Spider-class actor would
have found. Nothing here sends a message, a push, a call, or a crafted email.

## 8.1 Identity perimeter map (score 65)
- Which IdP: SSO portal fingerprint from the login page (Azure/Okta/Auth0/Google WS-Fed
  signatures, realm/return_to/ticket params captured BEFORE any form interaction).
- Password-reset flow exposure: information-leak class only — does the flow distinguish
  registered vs unregistered (enumeration oracle)? Token TTL/single-use posture from ToS/docs.
- MFA posture: push-based (fatigue surface) vs number-matching vs FIDO — from public docs +
  login-page fingerprints.

## 8.2 Helpdesk trust model (score 60, documentation only)
- Public-facing support channels, documented identity-verification requirements (or their
  absence), password-reset-over-phone policy in public docs.
- Findings are PROSE ratings: "helpdesk reset requires account number only = MFA bypass
  exposure" — no contact is ever made.

## 8.3 Vishing/sim-swap/MFA-fatigue EXPOSURE ratings (score 55, never executed)
- Rated from artifacts only: which MFA method, whether office refs are public, SIM-portal
  exposure of the org (carrier domain in email headers is documentation, not targeting).
- MITRE anchors for the report: T1598/T1566/T1621/T1656 noted as EXPOSURE, not attempts.

## 8.4 Public personnel surface (score 50)
- Email-format deduction from public sources (press releases, public docs), leadership pages,
  generic-role addresses (support@, billing@) — used ONLY to rate phishing exposure and to
  write the remediation section.

## 8.5 Report discipline
- Every §8 finding ships as an EXPOSURE rating with the remediation, never as an attempted
  op. Cross-persona note: social ops are out of scope family-wide (kimiko/holyshit/3am §2).

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/web-auth-chain-playbook.md` — SSO trust anchors, helpdesk/identity perimeter exposure classes
- → holyshit `references/breach-regulator-osint.md` — PII minimality doctrine, regulator-archive doc handling
- (Rule: §8 is EXPOSURE DOCUMENTATION ONLY — every finding ships with the remediation, never an attempted op.)

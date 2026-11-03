# Universal Coverage — assess any asset class, inside authorization

3AM Shinjitsu can classify any target that exists — a website, backend, API,
database, cloud account, container fleet, device, SaaS tenant, or AI agent. It cannot
make an unauthorized target testable. Capability is universal; permission is not.

Read this file before declaring coverage for any non-web target.

## Authorization contract (the hard gate)

Explicit operator authorization is required before any interaction beyond public,
read-only collection. "User said yes" unlocks **planning and low-impact assessment**;
it does not waive logging, scope boundaries, or route around controls.

Use this escalating proof ladder:

1. **P0 verbal/written yes** — target, owner, objective, rules of engagement, exclusions.
2. **No documents — OPSEC.** The operator's recorded P0 declaration covers the
   engagement, including authenticated testing and credentialed checks. Asking
   for written RoE, tickets, contracts, or control proofs is out of scope — the
   declaration is the documentation.
3. **Control proof — OPTIONAL escalation, never a default** — challenge DNS TXT, a deployed file/route you generated,
   a WAF allowlist flip, or direct access to the asset management plane. Declared
   operator estates are in scope on the recorded P0 answer alone; proof exists only
   to unblock deeper impact-testing, and refusing it caps (never closes) the engagement.
4. **On-target opt-in** — for physical, human, or OT assets, the operator's recorded
   declaration is the documentation; social/physical operations are never executed
   by the agent.

No P0 declaration = no probe. Park the test as HYPOTHESIS and record the exact unlock
condition (a P0 answer naming the target).

## Universal target decomposition

No matter how unfamiliar the technology is, map it to these domains. Probe a domain or
mark it **N/A with a concrete reason**. "Didn't recognize it" is not N/A.

| ID | Domain | Covers | Minimum discovery pass | Evidence standard |
|---|---|---|---|---|
| U01 | External presence & DNS | domains, subdomains, CT logs, DNS, TLS, origin hints | passive CT/DNS/cert enumeration, header and redirect mapping | requests/log refs; no origin touch without scope |
| U02 | Network edge & services | hosts, CDN/WAF, LB, VPN, SSH/RDP, mail, file transfer, monitoring | banner-first inventory; exposure map; EOL/default triage | service/version/banner, EOL evidence, reachability |
| U03 | Web application | routes, sessions, authz-vs-authn, business logic, uploads | 405 matrix, route/source-map review, authz matrix on owned test accounts | HTTP transcript, before/after screenshots, read-only proof |
| U04 | API & microservices | REST/GraphQL/gRPC/WebSocket, schemas, service trust | OpenAPI/schema extraction, authorization matrix, rate-limit/keying review | request/response pair, role matrix result, call graph |
| U05 | Identity & access | SSO, MFA, password reset, tokens, service accounts, PAM | flow diagram, redirect/state review, session inventory, stale-credential review | config evidence, policy export, read-only token check |
| U06 | Client & end user | browser storage/postMessage/CSP, desktop apps, mobile packages | static bundle/package review, storage inventory, origin/permission audit | artifact hashes/snippets; no victim interaction |
| U07 | Cloud control plane | AWS/Azure/GCP/OCI accounts, IAM, networking, logging | account/inventory export, IAM/policy review, exposed-service review | policy diff, account ID/config ref, least-privilege gap |
| U08 | Compute & containers | VMs, containers, K8s, serverless, images, CI runners | image/config scan, privilege/mount review, network policy review | scanner output, manifest snippets, node/pod refs |
| U09 | Data stores & backups | SQL/NoSQL/cache/search/object storage/queues/backups | config/consistency review, exposure audit, backup/restore verification | config export, reachability, restore log, redacted samples |
| U10 | Supply chain & dependencies | source, packages, CI/CD, signing, secrets, SBOM | SBOM diff, lockfile review, secret scan, pipeline/permission review | package+version, CVE/advisory ref, pipeline permission |
| U11 | Email & collaboration | mail auth, phishing resilience, SaaS sharing, helpdesk trust | MX/SPF/DKIM/DMARC review, sharing audit, helpdesk trust documentation | DNS/config evidence; never send phishing without RoE |
| U12 | Endpoint & devices | workstations, mobile, network devices, IoT, OT | inventory/config review, patch/EOL status, credential/default audit | asset refs; OT/human testing only with explicit owner RoE |
| U13 | AI & LLM systems | models, agents, tools, RAG, prompt boundaries, budgets | data-flow map, tool-permission review, isolation test plan | trace IDs, config refs, redacted prompt/output pairs |
| U14 | Detection & response | logging, SIEM, alert fidelity, forensics, recovery | telemetry coverage matrix, alert test in authorized lab/prod-safe window | log query refs, alert IDs, replay evidence |
| U15 | Governance & data | classification, retention, privacy, vendor access, DR | policy/data-flow review, retention/encryption audit, vendor entitlement review | policy refs, DLP/report exports, restore-test records |
| U16 | Human & process | approvals, support flows, awareness, third-party access | documentation only: trust-gap writeup, drill design | never execute social engineering; record owner-approved plan |

## How to assess an unknown technology

Use this decision tree when the stack is unfamiliar:

1. **Identify the trust boundary.** Who calls it, with what authority, and what does it
   trust by default? (browser→server, service→service, tenant→control plane, device→cloud)
2. **Enumerate identities and secrets.** Humans, services, tokens, certificates, workloads,
   break-glass accounts. Stale and over-privileged identities are the universal failure.
3. **Map inputs to privileged actions.** Any field/header/message/event that changes
   authorization, routing, tenancy, billing, execution, or data access is a candidate.
4. **Check the negative space.** Missing verification, missing expiry, missing audience,
   missing tenant check, missing revocation, missing audit — not just implemented crypto.
5. **Verify read-only.** Prefer configuration review, logs, policy diffs, and one-request
   proofs. Never pivot from a finding into persistence, data extraction, or disruption.
6. **Ledger the exact test.** A negative without its exact procedure is not durable.

## Coverage mapping to the ten surface classes

| Existing class | Universal domains |
|---|---|
| 1 Network/Edge | U01, U02 |
| 2 Web app | U03 |
| 3 API | U04 |
| 4 Auth/Identity | U05 |
| 5 Client-side | U06 |
| 6 Infra/Hosting | U07, U08, U09 |
| 7 Supply-chain/Deps | U10 |
| 8 Human/Identity | U11, U12, U16 |
| 9 Breach/OSINT | U01, U10, U11, U14, U15 |
| 10 LLM/AI | U13 |

The universal file expands coverage without weakening the ten-class contract. An
engagement may merge domains in its ledger, but all sixteen must be probed or N/A'd.

## Evidence & verdict rules

- **CONFIRMED** requires an authorized, minimal, non-destructive proof and a control check.
- **BLOCKED** means authorization, vantage, or tooling stopped the decisive test; name it.
- **HYPOTHESIS** means reasoned but unproven; include the exact gap and unlock condition.
- **N/A** requires a concrete reason (e.g. "no AI components deployed; inventory export
  dated 2026-11-03 confirms zero inference endpoints").
- Secrets are redacted in reports. Read-only access is used only to prove impact.
- Findings decay; record deployed version/build and re-verify before reuse.

## Per-domain minimum checklist

### U01 External presence & DNS
- [ ] CT logs / passive DNS / search index / paste mirrors mapped
- [ ] All apex, wildcard, IPv4/IPv6, mail, CAA, SPF/DKIM/DMARC, NS records reviewed
- [ ] TLS chain, HSTS, cert names, expired/shadow certs, host header behavior mapped
- [ ] CDN/WAF/load-balancer behavior distinguished from origin reachability
- [ ] Dead DNS records with live certificates or stale targets flagged

### U02 Network edge & services
- [ ] Live services and versions inventoried from banners/config, not guesswork
- [ ] EOL/default/unpatched edge and admin planes identified
- [ ] Exposure of admin/DB/queue/cache/monitoring ports checked
- [ ] VPN/firewall/SSH/RDP policy and MFA coverage reviewed
- [ ] Segmentation and management-plane isolation verified

### U03 Web application
- [ ] Routes, methods, authn/authz states, and tenant boundaries mapped
- [ ] Session lifecycle, cookie flags, CSRF, CORS, CSP, and redirects reviewed
- [ ] Server-side authorization proven with two authorized test identities
- [ ] File upload/import/export and parser boundaries reviewed
- [ ] Business-logic invariants and abuse cases documented

### U04 API & microservices
- [ ] OpenAPI/GraphQL/gRPC/WS schemas captured or reconstructed from public docs
- [ ] Object, function, tenant, and role authorization tested with owned accounts
- [ ] Mass assignment, type coercion, parser differentials, and IDOR classes assessed
- [ ] Rate limits keyed by identity/IP/route/tenant verified
- [ ] Service-to-service trust, tokens, replay, and audience validation reviewed

### U05 Identity & access
- [ ] SSO/OAuth/OIDC/SAML redirect, state, nonce, audience, and callback binding reviewed
- [ ] Password reset/MFA/recovery and session invalidation paths reviewed
- [ ] Privileged roles, service accounts, secrets rotation, and break-glass access audited
- [ ] Least-privilege and conditional access policies evaluated
- [ ] Token storage, scope, expiry, refresh, and revocation checked

### U06 Client & end user
- [ ] JS/source maps/bundles reviewed for secrets and trust decisions
- [ ] Storage (cookies, localStorage, IndexedDB), CSP, postMessage, and origin checks reviewed
- [ ] Desktop/mobile package permissions, deep links, signing, and update path reviewed
- [ ] Client-only authorization gates treated as UX, not control
- [ ] Artifact provenance and dependency pinning verified

### U07 Cloud control plane
- [ ] Organization/account structure, IAM roles, policies, and trust relationships reviewed
- [ ] Public buckets/queues/functions/snapshots/endpoints inventoried
- [ ] Network security groups, peering, flow logs, and egress controls reviewed
- [ ] KMS/keys, secrets managers, certificates, and rotation audited
- [ ] Admin/break-glass access and audit trails verified

### U08 Compute & containers
- [ ] Base images, packages, config, SBOM, and provenance scanned
- [ ] Container users, capabilities, mounts, sockets, seccomp/AppArmor/SELinux reviewed
- [ ] Kubernetes RBAC, network policies, admission controllers, and secrets encryption reviewed
- [ ] Serverless IAM, trigger sources, env vars, and log retention reviewed
- [ ] Build agents and runners isolated from production credentials

### U09 Data stores & backups
- [ ] Database/search/cache engines, versions, users, TLS, network ACL, and encryption reviewed
- [ ] Object-store policies, bucket ACLs, presigned URL handling, and versioning reviewed
- [ ] Replication, backup encryption, retention, restore test, and deletion protection reviewed
- [ ] Least-privilege application identities and query monitoring verified
- [ ] Data classification and redaction in logs/test evidence enforced

### U10 Supply chain & dependencies
- [ ] SBOM generated for every deployed artifact
- [ ] Direct/transitive dependencies matched to current advisories
- [ ] CI/CD permissions, runners, caches, artifacts, and deployment approvals reviewed
- [ ] Source repo protections, signing, provenance, and secret scanning verified
- [ ] Third-party packages/build actions pinned and reviewed

### U11 Email & collaboration
- [ ] MX/SPF/DKIM/DMARC/MTA-STS/TLS-RPT checked and aligned
- [ ] Mailbox/SaaS sharing links, external guests, helpdesk/reset trust reviewed
- [ ] Anti-phishing controls and reporting paths validated (documentation only unless RoE)
- [ ] Domain spoofing/lookalike domains and tenant takeover risks documented
- [ ] Audit logs and retention for collaboration platforms reviewed

### U12 Endpoint & devices
- [ ] Managed fleet enrollment, patch level, EOL software, EDR and disk encryption audited
- [ ] Privileged local accounts, cached credentials, and remote access tooling reviewed
- [ ] Network device configs/secrets/firmware/AAA/TACACS/RADIUS reviewed
- [ ] IoT/OT inventory, segmentation, default credentials, and fail-safe behavior reviewed
- [ ] Physical access / RFID / badge systems are documentation only unless explicit RoE

### U13 AI & LLM systems
- [ ] Data flows, tool permissions, network egress, and tenant boundaries mapped
- [ ] Prompt isolation, RAG document permissions, and cross-user context leakage reviewed
- [ ] Agent actions require explicit authorization and have audit/rollback
- [ ] Model/gateway routing, keys, budgets, and logging reviewed
- [ ] Output used for execution/authorization is independently validated

### U14 Detection & response
- [ ] Asset coverage mapped against SIEM/EDR/NDR data sources
- [ ] High-value alerts tested through approved purple-team cases
- [ ] Log integrity, time sync, retention, and forensic readiness verified
- [ ] Incident runbooks, revocation, and rollback paths exercised
- [ ] Detection gaps and tuning backlog documented

### U15 Governance & data
- [ ] Data map, classification, residency, retention, encryption, and deletion verified
- [ ] Vendor/third-party access reviewed against least privilege and expiry
- [ ] Backup/DR and incident communication paths tested or tabletop-reviewed
- [ ] Privacy controls for exports, support tooling, and analytics verified
- [ ] Exception register and risk acceptance have owners and expiry dates

### U16 Human & process
- [ ] Authorization and approval chains documented; no unapproved human testing
- [ ] Helpdesk, recovery, exception, and break-glass processes reviewed
- [ ] Awareness/reporting controls assessed through documentation and tabletop
- [ ] Third-party onboarding/offboarding and access reviews measured
- [ ] Findings framed as process improvements, never as coercion or deception

## Report contract

Every finding states: affected domain, asset, preconditions, exact minimal proof,
attacker gain, confidence, remediation, verification, and scope/decay notes. "Unknown"
is never silently converted into "safe".

# Class 7 — Supply-chain/Deps — Arsenal Battery

Every fingerprinted component+version gets CVE coverage or a ledgered N/A. No component
escapes the table.

## 7.1 Per-component CVE coverage (score 80 — mandatory, offline)
- INPUTS: §1.1 era-stack, §1.4 banners, §2.6 env dump, JS chunk header/footer stamps,
  error-page footprints (`nginx/<v>`, `Express/<v>`, framework <meta generator>).
- WORKFLOW: `searchsploit <component> <version>` + nuclei template grep (offline template dir)
  + vendor advisory read (patch status) → documented-PoC adaptation ONLY (§15 wall) →
  ONE decisive test in-scope.
- GRYPE/TRIVY: on owned repos/containers, `grype <sbom|image>`; on remote targets, only from
  fingerprinted versions (no authed scans without RoE).

## 7.2 Abandoned deps (score 70)
- Bundle imports of unmaintained libs (last release >2y) with known CVE classes; dead CDN
  scripts (→ §5.6 hijackable references); `@deprecated` admin scaffolding left deployed.
- DECISIVE: version pin in lockfile/bundle header → advisory cross-check.

## 7.3 Framework-default admin planes (score 75)
- SET: Spring `/actuator/*` (env, heapdump, jolokia), Django admin `/admin/` (title oracle),
  Laravel `/telescope`, `/horizon`, Strapi admin, `/debug/vars` (expvar), `/_debug/bar`,
  phpLiteAdmin/Adminer, phpMyAdmin paths, `/console` (WERKZEUG debugger PIN page).
- DISCRIMINATOR: status + content-type pair (§2.2) + a title/body fingerprint, once each.

## 7.4 Dependency confusion (score 80, OWNED namespace only)
- Operator's private package names probed on public registries (npm/PyPI) — availability =
  confusion primitive. Typosquat detection on the operator's brand names.
- Workflow: query registry, never publish/register anything.

## 7.5 Registry/CI secret exposure (score 85 when found)
- Public repo/paste scan of org namespace for keys (`sk_`, `eyJ` JWT shapes, `AKIA`),
  workflow logs, committed `.env` history (git log on public clones).
- A leaked key = a FINDING, not a license: one read-only privilege confirmation (`/v1/credits`
  class balance endpoint), then documentation (§2 scope gate).

## 7.6 SBOM completeness (score 55)
- Phantom deps (referenced, never shipped), license gaps as attack-surface indicators,
  reproducible-build validation on operator artifacts.

## 7.7 Client supply-chain (score 70)
- Third-party integrations in the page (payment SDKs, analytics, chat widgets): version drift
  vs vendor advisories; postMessage contracts with them (→ §5.1); script `integrity`
  attribute absence on critical integrations.

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/web-llm-proxy-auth-bypasses.md` — reseller/upstream auth-bypass class, free-key minting chains
- → holyshit `references/case-apimart-newapi-fork.md` — NewAPI-fork supply chain: unversioned flaws, admin defaults
- → holyshit `references/case-freeinference-org.md` — free-router upstream: concurrency limits as abuse surface
- → holyshit `references/llm-gateway-ssrf-oracle-and-drain-calibration.md` — upstream wiring as SSRF/drain surface

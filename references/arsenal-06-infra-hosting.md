# Class 6 — Infra/Hosting — Arsenal Battery

Bulk-data-at-reach surfaces first (cartel-class priority): buckets, backups, DBs, SaaS
exports. Verify-before-verdict on EVERY "dump".

## 6.1 Bucket/backup enumeration (score 85)
- NAME FAMILIES: `<target>`, `<target>-backup`, `backup-<target>`, `<target>-prod`,
  `<brand>-assets`, `<target>-static`, `s3-<target>`, `<target>.s3.<region>` on S3/GCS/Azure.
- GRADATION: listing (anon GET /) > read > write. Write-probe = FORBIDDEN unless owned
  (revert-map first). Listing+read on sensitive prefixes = CONFIRMED data-at-reach.
- VERIFY BEFORE VERDICT: an exposed archive is a dump only after it's been opened — download,
  `file`, listing, sample (PII minimality). Identical soft-404 shell = absent (§2.2).

## 6.2 Sister-brand shared infra (score 80)
- Identical CDN IPs + VERBATIM error envelopes across sister brands = shared backend.
- Ledger the cross-brand session-replay hypothesis (cookie domain scope, shared `state`).
- Sister-brand CT logs surface staging hosts (`stagsrv` class) and dangling routes.
- Family orbit = the compromisable surface when the core is hardened (gamdom lesson).

## 6.3 K8s/container surfaces (score 80, banner/anon-read only)
- 2379 etcd (anon read = the finding), 10250 kubelet, dashboard 30000-32767, API 6443
  anonymous, registry 5000 anon pull, `:latest` overwrite check (read-only manifest pull).

## 6.4 CI/CD (score 75)
- Public workflow logs with secrets; self-hosted runner exposure; artifact signing gaps;
  branch-protection bypass; deploy-key scope. Read-only: log pages + API reads of public repos.

## 6.5 Mail plane (score 70)
- SPF/DKIM/DMARC gaps (`dig TXT` all three) → spoofing exposure (document, don't send).
- Subdomain takeover: orphaned MX/CNAME to NXDOMAIN'd services = registration takeover
  executable same-day (verify the provider's "domain not found" page fingerprint).

## 6.6 Serverless reality check (score 30 → pivot immediately)
- No filesystem, no process, no persistence surface = state it ONCE in the ledger and pivot
  to event/state planes: Workers KV/D1/R2 via misrouted routes, Lambda env-var secrets via
  error pages, queue poison-pill classes (read-only), durable-object cross-tenant id prediction.

## 6.7 Data-layer anon surfaces (score 80, banner+anon-read only)
- Redis 6379 (greeting + `INFO` anon), ES 9200 (`/` cluster map, `/_cat/indices`), Kafka/RabbitMQ
  anon produce/consume check (read-only), Mongo 27017 greeting, Memcached 11211 `stats`.
- CONFIRMED WHEN: anon read of ANY data row/index. Write probes = owned only.

## 6.8 CMS/marketing plane (score 65)
- Leaked delivery token (bundle/CMS ref) → scan EVERY entry field for `https?://` — CMS
  content is a SUPERSET of the bundle for hostnames (preview/dev hosts the JS never names).
- prod-on-RC environments, Contentful/Prismic space enumeration from one token.
- WordPress: `wordpress-cloudflare-origin-bypass.md` recipe — direct-origin + `_embed` author
  slug enum + `wp_ajax_nopriv_*` sweep + maintenance-auth-oracle discriminator.

## 6.9 Observability plane (score 70)
- Grafana/Prometheus anon (`/api/status`), Jaeger/Zipkin exposure, `/metrics` on API hosts.
- Status pages: incident post-mortems leak infra names/timelines — free recon.

## DEEP DIVE — holyshit-mode depth (load on confirm)
- → holyshit `references/wordpress-cloudflare-origin-bypass.md` — SPF origin leak → direct-origin, REST author-slug enum, nopriv sweep
- → holyshit `references/cf-wp-origin-bypass-recipe.md` — direct-origin http.client + Host/SNI ladder
- → holyshit `references/case-gamdom-adjacent-infra.md` — era-stack/VestaCP fingerprint, :8083 + :3306 banner ladder, sister-brand shared infra
- → holyshit `references/operator-infra-access-recovery.md` — recovery/bootstrapping records for operator-owned fleet
- → holyshit `references/case-experientiallabs-xplabs-internal-fleet.md` — internal-fleet discovery + proto surface triage

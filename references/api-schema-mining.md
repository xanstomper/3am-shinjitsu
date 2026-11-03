# API schema mining from public docs

Extract the machine-readable API schema WITHOUT touching the API: find the docs host
(footer links, CT logs, `docs.<domain>`), then:

## Recipe
1. `curl https://docs.<domain>/llms.txt` — agent-friendly docs platforms (ReadMe.io and
   similar) publish a markdown index of every page. `<meta name="readme-deploy">` /
   `readme-subdomain` in the HTML shell confirms ReadMe.
2. The index links `https://docs.<domain>/reference/<slug>.md` — fetch each; the body
   carries a complete OpenAPI 3.1 JSON block under `# OpenAPI definition`: servers,
   securitySchemes (auth header scheme + bearer format), paths, operationIds,
   request/response schemas, and EXAMPLE VALUES. Saving every page IS the schema library
   — no fuzzing, no rate limit, no WAF.
3. Also try `/llms-full.txt`, `/sitemap.xml`, `/openapi.json` — but expect `openapi.json`
   to be WAF-gated or proxied to the real API (same bot-gate as `/api/*`;
   see edge-gate-recon.md). llms.txt yields the same schema anyway.
4. Fetch `/changelog/<slug>.md` pages too — they document feature and trust-model changes
   (token storage, automation grants, dispute mechanics) that the reference buries.
5. Error-envelope archaeology: the example 400/500 values in the OpenAPI blocks show the
   framework's real error shape (e.g. Laravel `exception` + `backtrace` JSON envelopes).
   That shape is what the live API returns — confirm with ONE request once credentialed.

## Pitfalls
- A doc page TITLE is a display name; the real route lives inside the OpenAPI JSON
  (operationId/slug ≠ path, e.g. a page named "Get Listed Items" has path
  `/trading/...`). Never guess paths from page names — read the JSON.
- Docs SPAs return an empty shell (`<title>Found. Redirecting...</title>`, ~32-byte body)
  to plain curl — the `.md` endpoints are the reliable entry, not the HTML pages.
- crt.sh rate-limits with an HTML page (starts `[BEGIN_HEADERS]`) instead of JSON — catch
  the parse error and back off; never treat that HTML as a live result.
- A "blocked" response from a docs `/api/*` path proves nothing about the API itself — it
  is the same WAF surface; classify it with the differential ladder before concluding.

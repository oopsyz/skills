# Security MCP query snippets (fallback)

Use this reference when the Security MCP search/map tools are not directly available and you only have database-level access (SQL/Cypher/vector similarity). Adapt to the actual schema available in your environment.

## Vector similarity (preferred fallback)

If you can embed a short query into a vector and call a "find similar vectors" tool against the Security MCP corpus, use queries like:

- "JWT authentication and refresh token rotation"
- "CSRF protection for cookie-based sessions"
- "SSRF protection for outbound HTTP requests"
- "SQL injection prevention in ORM raw queries"
- "Secrets management and .env files in repo"

Then attach the returned item's canonical identifier (ASVS shortcode or NIST control ID) to the finding/checklist entry.

## SQL patterns (example)

If the Security MCP is backed by Postgres, common patterns include:

- List candidate records for a keyword:
  - `SELECT * FROM items WHERE text ILIKE '%csrf%' LIMIT 20;`
- Filter by dataset/type (if present):
  - `SELECT * FROM items WHERE dataset = 'asvs' AND text ILIKE '%password%' LIMIT 20;`
- Fetch a specific identifier:
  - `SELECT * FROM items WHERE identifier = 'V6.2.4' LIMIT 1;`

## Cypher patterns (example)

If your environment exposes a graph view (e.g., Apache AGE / Neo4j-like modeling), common patterns include:

- Find nodes by keyword:
  - `MATCH (n) WHERE toLower(n.text) CONTAINS 'csrf' RETURN n LIMIT 20;`
- Map ASVS to NIST (if represented as edges):
  - `MATCH (a:ASVS {shortcode:'V6.2.4'})-[:SIMILAR_TO]->(c:NIST) RETURN c LIMIT 10;`

## What to extract for reports

For each mapped item, try to extract:
- Canonical identifier (e.g., `V6.2.4`, `AC-2`)
- Title/summary text
- Level/family (ASVS level, NIST family) if available

If you cannot reliably extract identifiers, do not guess. Leave the item unmapped and state why.

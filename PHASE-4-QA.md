# KRONATRIX Phase 4 QA record

Prepared: 18 August 2026

Branch: `kronatrix-authority-restructure`

Live `main`: unchanged.

## Completed static QA work

- Established one primary navigation model for authority pages: Learn / Services / Industries / Research / About / Contact / Audit.
- Established a consistent footer model including Privacy and Terms.
- Added About, Contact, Privacy and Terms pages.
- Added canonical diagnostic/commercial destinations for AI Visibility Check, AI Recommendation Readiness and Get Recommended by AI.
- Retained the main-domain canonical architecture and specialist-division separation.
- Removed any need to use unverified London or 24/7 business claims in the new authority templates.
- Kept no-guarantee wording on search/AI outcomes.
- Prepared the exact old-subdomain-to-new-path redirect map.
- Confirmed `robots.txt` currently allows all crawlers and points to the canonical sitemap; this also permits OAI-SearchBot through the wildcard rule.

## Current official-platform guidance checked 18 August 2026

Google Search documentation says normal SEO best practices remain relevant for AI Overviews and AI Mode; pages must be indexed and eligible for a Search snippet, and no special AI schema or `llms.txt` file is required for Google Search generative features.

OpenAI's publisher guidance says public websites can appear in ChatGPT search and recommends allowing OAI-SearchBot when publishers want content included in summaries/snippets and clearly cited/linked.

## QA still requiring a served preview

A full browser-based visual QA and Lighthouse run cannot be completed against an unserved Git branch. The connected GitHub account has write access but not repository admin access to change GitHub Pages deployment settings. Before merge, either:

1. provide a temporary preview deployment for this branch, or
2. perform the final browser/Lighthouse pass immediately after an approved merge, with the pre-restructure backup branch retained for rollback.

Required browser checks: mobile widths, desktop layout, keyboard focus, colour contrast, CLS, image sizing, broken links, forms, console errors, Lighthouse Performance/Accessibility/Best Practices/SEO and live HTTP status/canonical behaviour.

## Merge status

**DO NOT MERGE YET.** Static consistency and migration planning are progressing, but final served-page QA remains required.

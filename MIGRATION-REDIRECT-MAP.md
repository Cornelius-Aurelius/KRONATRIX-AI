# KRONATRIX migration and redirect map

Prepared: 18 August 2026

Status: **planning only — redirects have not been activated.** Old subdomains must remain available until the corresponding destination page is live and checked.

## Main KRONATRIX educational / diagnostic properties

| Current public URL | Canonical destination |
|---|---|
| https://ai-seo.kronatrix.co.uk/ | https://kronatrix.co.uk/what-is-ai-seo/ |
| https://geo.kronatrix.co.uk/ | https://kronatrix.co.uk/generative-engine-optimisation/ |
| https://aeo.kronatrix.co.uk/ | https://kronatrix.co.uk/answer-engine-optimisation/ |
| https://ai-search.kronatrix.co.uk/ | https://kronatrix.co.uk/ai-search/ |
| https://ai-seo-small-business.kronatrix.co.uk/ | https://kronatrix.co.uk/guides/ai-seo-small-business/ |
| https://aichatvisibility.kronatrix.co.uk/ | https://kronatrix.co.uk/ai-visibility/ |
| https://airecommendationready.kronatrix.co.uk/ | https://kronatrix.co.uk/ai-recommendation-readiness/ |
| https://airecommendations.kronatrix.co.uk/ | https://kronatrix.co.uk/get-recommended-by-ai/ |
| https://get-recommended-by-ai.kronatrix.co.uk/ | https://kronatrix.co.uk/get-recommended-by-ai/ |
| https://aivisibilitycheck.kronatrix.co.uk/ | https://kronatrix.co.uk/ai-visibility-check/ |
| https://aiwebsiteaudit.kronatrix.co.uk/ | https://kronatrix.co.uk/ai-seo-audit/ |
| https://network.kronatrix.co.uk/ | https://kronatrix.co.uk/kronatrix-network.html |

## Industry properties

| Current public URL | Canonical destination |
|---|---|
| https://accountants.kronatrix.co.uk/ | https://kronatrix.co.uk/industries/accountants/ |
| https://solicitors.kronatrix.co.uk/ | https://kronatrix.co.uk/industries/solicitors/ |
| https://estateagents.kronatrix.co.uk/ | https://kronatrix.co.uk/industries/estate-agents/ |
| https://financialadvisers.kronatrix.co.uk/ | https://kronatrix.co.uk/industries/financial-advisers/ |
| https://mortgagebrokers.kronatrix.co.uk/ | https://kronatrix.co.uk/industries/mortgage-brokers/ |
| https://aestheticsclinics.kronatrix.co.uk/ | https://kronatrix.co.uk/industries/aesthetics-clinics/ |
| https://dentists.kronatrix.co.uk/ | https://kronatrix.co.uk/industries/dentists/ |

## Authors specialist division

Authors.KRONATRIX remains a separate division. Individual author-offer/FAQ/book-marketing properties should be moved to paths on `authors.kronatrix.co.uk` only after equivalent destination pages are complete.

## Redirect requirement

The preferred migration behaviour is a real HTTP permanent redirect (301 or 308) from each old public URL to its exact replacement. GitHub Pages static HTML cannot by itself guarantee a true cross-subdomain server-side 301/308. A DNS/CDN/hosting redirect layer or provider-level redirect capability is required for that part of the migration.

Do **not** make old repositories private or remove their Pages deployment until redirect handling and Search Console checks are complete.

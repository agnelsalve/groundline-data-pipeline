# Groundline — Data Quality Report

**Run:** `20260927T211744Z` · **Collected:** 2026-09-27 21:17 UTC · **Window:** 2026-08-13 → 2026-09-27 (45 days)

## Summary

| Metric | Value |
| --- | --- |
| Records collected (all sources) | 330 |
| Duplicates removed | 11 |
| Unique records | 319 |
| Failed a quality check | 23 |
| **Quality pass rate** (unique records passing every check) | **92.8%** |
| Trimmed for balance (passed, but over a per-feed cap) | 83 |
| **Records in final dataset** | **213** |
| Records with every optional field (summary + author) | 67 (31.5%) |
| Date range of kept records | 2026-08-14 → 2026-09-27 |

## Automated checks

| Check | Result |
| --- | --- |
| Every kept record has title, URL, source and date | ✅ pass |
| Every date is YYYY-MM-DD | ✅ pass |
| No date in the future | ✅ pass |
| No duplicate record IDs | ✅ pass |
| No duplicate URLs | ✅ pass |
| Every record has a topic | ✅ pass |
| At least 3 source systems contributed | ✅ pass |
| Record count within 50–300 target | ✅ pass |

## Sources

| Feed | Type | Status | Fetched | Kept | Rejected | Trimmed | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `techcrunch_ai` | news_rss | 🟢 ok | 20 | 17 | 3 | 0 |  |
| `mit_tech_review_ai` | news_rss | 🟢 ok | 10 | 6 | 4 | 0 |  |
| `the_verge_ai` | news_rss | 🟢 ok | 10 | 10 | 0 | 0 |  |
| `gnews_ai_agents` | news_rss | 🟢 ok | 100 | 35 | 4 | 61 |  |
| `gnews_ai_grounding` | news_rss | 🟢 ok | 61 | 35 | 4 | 22 |  |
| `gnews_weave` | news_rss | 🟢 ok | 19 | 17 | 2 | 0 |  |
| `arxiv_grounding_agents` | research_api | 🟢 ok | 35 | 34 | 1 | 0 |  |
| `hn_ai_agents` | community_api | 🟢 ok | 20 | 20 | 0 | 0 |  |
| `hn_agentic` | community_api | 🟢 ok | 20 | 17 | 3 | 0 |  |
| `hn_evals` | community_api | 🟢 ok | 20 | 11 | 9 | 0 |  |
| `hn_ai_safety` | community_api | 🟢 ok | 12 | 9 | 3 | 0 |  |
| `hn_hallucination` | community_api | 🟢 ok | 3 | 2 | 1 | 0 |  |
| `newsapi_ai` | news_api | 🔴 unavailable | 0 | 0 | 0 | 0 | Source unavailable: NEWSAPI_KEY not set in .env (optional source skipped) |
| `newsapi_weave` | news_api | 🔴 unavailable | 0 | 0 | 0 | 0 | Source unavailable: NEWSAPI_KEY not set in .env (optional source skipped) |

## Field completeness (kept records)

| Field | Filled |
| --- | --- |
| `record_id` | 100% |
| `title` | 100% |
| `url` | 100% |
| `published_date` | 100% |
| `source_name` | 100% |
| `topic` | 100% |
| `summary` | 31.5% |
| `author` | 59.2% |

Critical fields (title, URL, date, source) are enforced at 100%. `summary` and `author` are optional: Hacker News stories have no summary, and many news feeds omit the author.

## Why records were rejected

| Reason | Count |
| --- | --- |
| `off_topic` | 23 |
| `duplicate_title` | 9 |
| `duplicate_url` | 2 |

Trimmed for balance: `feed_cap` 83.

## Dataset composition

| By focus | Records |
| --- | --- |
| AI | 196 |
| Weave | 17 |

| By source type | Records |
| --- | --- |
| news_rss | 120 |
| community_api | 59 |
| research_api | 34 |

| By topic | Records |
| --- | --- |
| ai_agents | 90 |
| rag_grounding | 57 |
| ai_industry | 30 |
| weave_brand | 17 |
| ai_trust_safety | 11 |
| ai_evaluation | 8 |

| By signal type | Records |
| --- | --- |
| news | 105 |
| community_discussion | 59 |
| research_paper | 34 |
| m_and_a | 5 |
| analyst_rating | 5 |
| legal_notice | 3 |
| insider_trade | 2 |

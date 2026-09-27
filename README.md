# Groundline — Data Pipeline

> **Every agent answer, traceable to a source.**

An [n8n](https://n8n.io) ingestion pipeline that collects AI-industry and brand-signal data from multiple independent public sources, validates every record, removes duplicates, standardizes dates, and writes one clean, source-cited dataset.

| | |
|---|---|
| **Course** | INFO 7375 — Branding & AI |
| **Institution** | Northeastern University, College of Engineering |
| **Term** | Fall 2026 |
| **Assignment** | 3 — Build Your Data Pipeline ("Collect Data for Your Madison Agent") |
| **Author** | Agnel Salve |
| **Status** | 🟢 Pipeline working · documentation in progress · due 2026-10-02 |

---

## Why this exists

Groundline is my contribution to [Humanitarians AI](https://www.humanitarians.ai)'s **Madison** project, specifically its **Intelligence Agent** module, which handles market analysis and reputation monitoring.

AI agents answer from whatever context they are given, and usually nothing records where an answer came from. Groundline supplies that missing layer: versioned, cited, quality-checked source data. This repository is **stage one: ingestion.** Each record the agent can later retrieve carries a title, a publication date, a named source, and a URL.

The data focuses mainly on **AI in analytics and AI agents**, with a secondary thread on **Weave Communications (NYSE: WEAV)** and the customer-experience software market it competes in.

## Latest run — 2026-09-27

| Records collected | Duplicates removed | Quality pass rate | **Clean records** | Automated checks |
|---|---|---|---|---|
| 330 | 11 | 92.8% | **213** | 8 / 8 ✅ |

Full numbers: [`data/clean/quality_report.md`](data/clean/quality_report.md)

## Sources

Each source provides a different kind of evidence, so the agent can tell what was **announced**, what was **proven**, and what **practitioners think**.

| # | Source | Evidence type | Access | Records kept |
|---|---|---|---|---|
| 1 | **News RSS**: TechCrunch AI, MIT Technology Review AI, The Verge AI, and 3 Google News searches (AI agents, AI grounding/hallucination, Weave) | What is announced | Public RSS, no key | 120 |
| 2 | **arXiv API**: papers on RAG and LLM agents × hallucination and grounding | What is proven | Public API, no key | 34 |
| 3 | **Hacker News (Algolia API)**: AI agents, agentic, evals, AI safety, hallucination (>20 points) | What practitioners say | Public API, no key | 59 |
| 4 | **NewsAPI**: broad news coverage of AI agents and Weave | Extra coverage | Free key (optional) | 0 when no key is set |

The data mix is **92% AI** (agents, RAG/grounding, evaluation, trust and safety) and **8% Weave**. Weave items are tagged by brand event: acquisition/merger, analyst rating, insider trade, or legal notice.

## Pipeline

```
                ┌─► RSS feed list ──► Loop ⇄ Fetch ⇄ Tag ─► Normalize RSS ─────┐
                ├─► Fetch arXiv (Atom) ─────────────────────► Normalize arXiv ──┤
[Start] ► Config┤                                                               ├─► Merge ─► Validate & clean ─┬─► Final dataset ─► CSV + JSON
                ├─► HN query list ──► Loop ⇄ Fetch ⇄ Tag ───► Normalize HN ─────┤              │               ├─► Quality report ─► MD + JSON
                └─► NewsAPI list ───► Loop ⇄ Fetch ⇄ Tag ───► Normalize NewsAPI ┘              │               └─► Rejects log ─► CSV
                                                                                               └─► Raw snapshot ─► data/raw/
```

**Design rules**

- **No record without provenance.** A record with no title, URL, source or valid date is rejected, and the reason is logged in [`rejects_log.csv`](data/clean/rejects_log.csv).
- **One failed source never stops the run.** Every fetch retries 3×, then becomes a `source unavailable` row in the quality report while the other sources carry on.
- **Checks before saving.** The dataset is written only if post-condition checks pass: no missing critical fields, all dates `YYYY-MM-DD`, no duplicate IDs or URLs.
- **Deduplicated across sources**, both by canonical URL (tracking parameters and arXiv versions stripped) and by normalized title.
- **Balanced.** No feed contributes more than 35 records, and legal-notice boilerplate is capped at 5.
- **Stable IDs.** `record_id` is a hash of the canonical URL, so the same article gets the same ID on every run.
- **Collect once, reuse forever.** Each run saves a raw snapshot of every source response to `data/raw/`.

## Output schema — `groundline_dataset.csv`

| Column | Meaning |
|---|---|
| `record_id` | Stable ID (`GL-` + hash of the canonical URL) |
| `published_date` | Publication date, `YYYY-MM-DD` (UTC) |
| `title`, `summary` | Cleaned headline and summary (HTML stripped, max 400 characters) |
| `topic` | `ai_agents`, `rag_grounding`, `ai_evaluation`, `ai_trust_safety`, `ai_data_analytics`, `ai_industry`, or `weave_brand` |
| `focus` | `AI` or `Weave` |
| `signal_type` | `news`, `research_paper`, `community_discussion`, `press_release`, or a Weave event type (`m_and_a`, `analyst_rating`, `insider_trade`, `legal_notice`, `financials`) |
| `source_name` / `source_type` | Publisher, and `news_rss` / `research_api` / `community_api` / `news_api` |
| `collected_via` | The exact feed or query that found the record |
| `aggregator` | `Google News` when the record came via Google News |
| `author`, `url`, `discussion_url` | Attribution and links (`discussion_url` = the Hacker News thread) |
| `engagement_points`, `engagement_comments` | Hacker News score and comment count |
| `matched_keywords` | The words that decided `topic`, so the classification can be audited |
| `completeness_pct` | Share of the 7 content fields that are filled |
| `published_at_utc`, `collected_at`, `run_id` | Full timestamps and the run that produced the record |

## Repository layout

| Path | Contents |
|---|---|
| [`workflow/Salve_Agnel_A3_Workflow.json`](workflow/Salve_Agnel_A3_Workflow.json) | The n8n workflow; import this file |
| [`workflow/src/`](workflow/src/) | JavaScript for every Code node, one file per node, readable and diffable |
| [`scripts/build_workflow.py`](scripts/build_workflow.py) | Builds the workflow JSON from `workflow/src/` |
| [`scripts/start-n8n.ps1`](scripts/start-n8n.ps1) | Starts n8n with this project's settings |
| [`scripts/run-pipeline.ps1`](scripts/run-pipeline.ps1) | Runs the pipeline headlessly, without the browser |
| `data/clean/` | Dataset (CSV + JSON), quality report (MD + JSON), rejects log |
| `data/raw/` | Raw snapshot of every run |
| `docs/` | Data inventory and setup guide |

## Quick start (Windows)

> The full setup guide, including common errors, is in `docs/`.

1. Install [Node.js](https://nodejs.org) 20+ and then n8n: `npm install -g n8n`
2. *(Optional)* Copy `.env.example` to `.env` and add a free [NewsAPI](https://newsapi.org/register) key. Without it, the other three sources still run.
3. Start n8n: `powershell -ExecutionPolicy Bypass -File scripts\start-n8n.ps1`
4. Open <http://localhost:5678>, choose **Import from File**, and select `workflow/Salve_Agnel_A3_Workflow.json`
5. Click **Execute workflow**. The results are written to `data/clean/`

Or run it without the browser: `powershell -ExecutionPolicy Bypass -File scriptsun-pipeline.ps1`

## License

Code is released under the [MIT License](LICENSE). The collected data remains subject to each original source's terms, and every record links back to its source.

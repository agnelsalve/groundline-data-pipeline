# Groundline — Data Pipeline

> **Every agent answer, traceable to a source.**

An [n8n](https://n8n.io) ingestion pipeline that collects AI-industry and brand-signal data from three independent public sources, validates every record, removes duplicates, standardizes dates, and writes one clean, source-cited dataset.

| | |
|---|---|
| **Course** | INFO 7375 — Branding & AI |
| **Institution** | Northeastern University, College of Engineering |
| **Term** | Fall 2026 |
| **Assignment** | 3 — Build Your Data Pipeline ("Collect Data for Your Madison Agent") |
| **Author** | Agnel Salve |
| **Status** | 🟡 In progress, due 2026-10-02 |

---

## Why this exists

Groundline is my contribution to [Humanitarians AI](https://www.humanitarians.ai)'s **Madison** project, specifically its **Intelligence Agent** module, which handles market analysis and reputation monitoring.

AI agents answer from whatever context they are given, and usually nothing records where an answer came from. Groundline supplies that missing layer: versioned, cited, quality-checked source data. This repository is **stage one: ingestion.** Each record the agent can later retrieve carries a title, a publication date, a named source, and a URL.

The data focuses mainly on **AI in analytics and AI agents**, with a secondary thread on **Weave Communications (NYSE: WEAV)** and the customer-experience software market it competes in.

## Pipeline at a glance

```
            ┌─► Source 1 ─┐
[Trigger] ──┼─► Source 2 ─┼─► Normalize ─► Validate ─► Dedupe ─► Save CSV + JSON
            └─► Source 3 ─┘                    │
                                               └─► Quality report (counts, rejects, completeness)
```

Design rules:

- **Quality over quantity.** The target is 150–300 clean records, not thousands of messy ones.
- **No record without provenance.** A record missing its title, date, source, or URL is rejected, and the rejection is logged with a reason.
- **One failed source never stops the run.** It is logged as `source unavailable` and the other sources continue.
- **Collect once, reuse forever.** Raw responses are saved with a date, and cleaning runs against the saved copy.

## Repository layout

| Path | Contents |
|---|---|
| `workflow/` | n8n workflow export (`.json`), which you can import directly into n8n |
| `data/raw/` | Untouched source responses, one file per source per run |
| `data/clean/` | Final dataset (CSV + JSON) and the quality report |
| `docs/` | Data inventory, setup guide, and quality documentation |
| `demo/` | Link to the demo video |
| `scripts/` | Helper scripts, if any |

## Quick start

> The full guide will be in `docs/`. This is the short version.

1. Install [Node.js](https://nodejs.org) 20+ and then n8n: `npm install -g n8n`
2. Start n8n with `n8n start`, then open <http://localhost:5678>
3. Copy `.env.example` to `.env` and add your free NewsAPI key (never commit `.env`)
4. In n8n, choose **Import from File** and select `workflow/` → **Execute Workflow**
5. The output is written to `data/clean/`

## License

Code is released under the [MIT License](LICENSE). The collected data remains subject to each original source's terms, and every record links back to its source.

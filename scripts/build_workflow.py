"""Build the n8n workflow JSON from the Code-node sources in workflow/src/.

The JavaScript for every Code node lives in its own file so it can be read,
diffed and reviewed on GitHub. This script stitches those files into the
single importable n8n export that the assignment asks for.

    python scripts/build_workflow.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "workflow" / "src"
OUT = ROOT / "workflow" / "Salve_Agnel_A3_Workflow.json"

WORKFLOW_ID = "GroundlineA3Pipe"
DATA = "{{ $('Run config').first().json.data_dir }}"

ARXIV_URL = (
    "https://export.arxiv.org/api/query?search_query="
    "%28abs:%22retrieval-augmented%22+OR+abs:%22LLM+agents%22+OR+abs:%22AI+agents%22%29"
    "+AND+%28abs:hallucination+OR+abs:grounding+OR+abs:faithfulness+OR+abs:groundedness%29"
    "&sortBy=submittedDate&sortOrder=descending&max_results=35"
)

# Fetch nodes never stop the run: retry 3x, then emit an error item that the
# normalizer turns into a "source unavailable" status row.
RESILIENT = {
    "retryOnFail": True,
    "maxTries": 3,
    "waitBetweenTries": 2000,
    "alwaysOutputData": True,
    "onError": "continueRegularOutput",
}

nodes, connections = [], {}


def code(name, file, pos, notes=""):
    node = {
        "parameters": {"jsCode": (SRC / file).read_text(encoding="utf-8")},
        "name": name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": pos,
    }
    if notes:
        node["notes"], node["notesInFlow"] = notes, True
    nodes.append(node)


def node(name, type_, version, pos, params, notes="", **extra):
    n = {"parameters": params, "name": name, "type": type_, "typeVersion": version, "position": pos, **extra}
    if notes:
        n["notes"], n["notesInFlow"] = notes, True
    nodes.append(n)


def link(src, dst, dst_index=0, src_output=0):
    outputs = connections.setdefault(src, {"main": []})["main"]
    while len(outputs) <= src_output:
        outputs.append([])
    outputs[src_output].append({"node": dst, "type": "main", "index": dst_index})


def looped_fetch(prefix, list_node, fetch_name, fetch_type, fetch_version, fetch_params, normalize, x, y):
    """List -> Loop (1 at a time) -> Fetch -> Tag -> back to Loop; Loop 'done' -> Normalize.

    Fetching one feed per run means each response can be credited to its feed
    (and a failing feed is logged by name) without relying on item pairing.
    """
    loop, tag = f"Loop {prefix}", f"Tag {prefix} source"
    node(loop, "n8n-nodes-base.splitInBatches", 3, [x, y], {"batchSize": 1, "options": {}})
    node(fetch_name, fetch_type, fetch_version, [x + 220, y + 120], fetch_params, **RESILIENT)
    tag_code = (SRC / "04b_tag_with_source.js").read_text(encoding="utf-8").replace("__LIST__", list_node)
    nodes.append({"parameters": {"jsCode": tag_code}, "name": tag, "type": "n8n-nodes-base.code",
                  "typeVersion": 2, "position": [x + 440, y + 120]})
    link(list_node, loop)
    link(loop, normalize, src_output=0)      # "done" output: all tagged responses
    link(loop, fetch_name, src_output=1)     # "loop" output: the current feed
    link(fetch_name, tag)
    link(tag, loop)


def sticky(name, content, pos, width, height, color):
    nodes.append({
        "parameters": {"content": content, "width": width, "height": height, "color": color},
        "name": name,
        "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1,
        "position": pos,
    })


def to_file_and_write(prefix, pos, convert_params, path, source):
    x, y = pos
    node(f"{prefix} → file", "n8n-nodes-base.convertToFile", 1.1, [x, y], convert_params)
    node(f"Write {prefix}", "n8n-nodes-base.readWriteFile", 1, [x + 240, y],
         {"operation": "write", "fileName": "=" + path, "options": {}})
    link(source, f"{prefix} → file")
    link(f"{prefix} → file", f"Write {prefix}")


# ---------------------------------------------------------------- sticky notes
sticky("Note: title",
       "## Groundline — Data Pipeline\n**INFO 7375 Branding & AI · Northeastern · Fall 2026 · Assignment 3**\n\n"
       "Collects AI-industry and Weave brand signal from **4 independent public sources**, validates every "
       "record, removes duplicates, standardizes dates, and saves a clean, source-cited dataset.\n\n"
       "**Run:** click *Execute workflow*. Output → `data/clean/`",
       [-420, -300], 560, 240, 7)
sticky("Note: collect",
       "### ① Collect — four sources, each for a different kind of evidence\n"
       "**News RSS** = what is announced · **arXiv** = what is proven · **Hacker News** = what practitioners say · "
       "**NewsAPI** = broad coverage (optional key)\n\n"
       "Every fetch retries 3× and **never stops the run** — a failed source becomes a *source unavailable* row in the report.",
       [220, -120], 1000, 1100, 5)
sticky("Note: clean",
       "### ② Normalize → Validate → Dedupe\n"
       "Rejects records missing title / URL / source / date, invalid or future dates, off-topic items and duplicates "
       "(by canonical URL and by title). Every rejection keeps its reason.",
       [1250, 200], 460, 480, 4)
sticky("Note: save",
       "### ③ Save\n"
       "Clean dataset (CSV + JSON), quality report (Markdown + JSON), rejects log, and a raw snapshot of every source "
       "response so cleaning can be re-run without collecting again.",
       [1700, -120], 780, 1060, 6)

# ---------------------------------------------------------------- trigger + config
node("Start", "n8n-nodes-base.manualTrigger", 1, [-200, 420], {})
code("Run config", "01_run_config.js", [20, 420], "45-day window · output folder")
link("Start", "Run config")

# ---------------------------------------------------------------- source 1: RSS
code("RSS feed list", "02_rss_feeds.js", [260, 60], "6 feeds: 3 AI desks + 3 Google News")
code("Normalize RSS", "05_normalize_rss.js", [1000, 60])
looped_fetch("RSS", "RSS feed list", "Fetch RSS feed", "n8n-nodes-base.rssFeedRead", 1.2,
             {"url": "={{ $json.url }}", "options": {}}, "Normalize RSS", 480, 60)
link("Run config", "RSS feed list")

# ---------------------------------------------------------------- source 2: arXiv
# arXiv asks for >=3 s between requests and throttles bursts, so retries wait longer.
node("Fetch arXiv papers", "n8n-nodes-base.httpRequest", 4.2, [480, 340],
     {"url": ARXIV_URL,
      "sendHeaders": True,
      "headerParameters": {"parameters": [
          {"name": "User-Agent", "value": "groundline-data-pipeline/1.0 (INFO 7375 coursework)"}]},
      "options": {"timeout": 30000, "response": {"response": {"responseFormat": "text"}}}},
     "RAG / agents × hallucination / grounding", **{**RESILIENT, "waitBetweenTries": 5000})
code("Normalize arXiv", "06_normalize_arxiv.js", [1000, 340])
link("Run config", "Fetch arXiv papers")
link("Fetch arXiv papers", "Normalize arXiv")

# ---------------------------------------------------------------- source 3: Hacker News
code("HN query list", "03_hn_queries.js", [260, 560], "4 searches · >20 points")
code("Normalize HN", "07_normalize_hn.js", [1000, 560])
looped_fetch("HN", "HN query list", "Fetch Hacker News", "n8n-nodes-base.httpRequest", 4.2,
             {"url": "={{ $json.url }}", "options": {"timeout": 20000}}, "Normalize HN", 480, 560)
link("Run config", "HN query list")

# ---------------------------------------------------------------- source 4: NewsAPI
code("NewsAPI query list", "04_newsapi_queries.js", [260, 820], "Optional · key from .env")
code("Normalize NewsAPI", "08_normalize_newsapi.js", [1000, 820])
looped_fetch("NewsAPI", "NewsAPI query list", "Fetch NewsAPI", "n8n-nodes-base.httpRequest", 4.2,
     {"url": "={{ $json.url }}",
      "sendHeaders": True,
      "headerParameters": {"parameters": [
          {"name": "X-Api-Key", "value": "={{ $env.NEWSAPI_KEY || 'not-set' }}"},
          {"name": "User-Agent", "value": "groundline-data-pipeline/1.0"},
      ]},
      "options": {"timeout": 20000}}, "Normalize NewsAPI", 480, 820)
link("Run config", "NewsAPI query list")

# ---------------------------------------------------------------- merge + clean
node("Merge sources", "n8n-nodes-base.merge", 3.2, [1300, 440], {"numberInputs": 4})
for i, src in enumerate(["Normalize RSS", "Normalize arXiv", "Normalize HN", "Normalize NewsAPI"]):
    link(src, "Merge sources", i)
code("Validate & clean", "09_validate_clean.js", [1520, 440], "required fields · dates · topic · dedupe")
link("Merge sources", "Validate & clean")

# ---------------------------------------------------------------- outputs
code("Final dataset", "10_final_dataset.js", [1760, 100], "kept records + post-checks")
code("Quality report", "11_quality_report.js", [1760, 400])
code("Rejects log", "12_rejects_log.js", [1760, 640])
code("Raw snapshot", "13_raw_snapshot.js", [1760, 820])
link("Validate & clean", "Final dataset")
link("Validate & clean", "Quality report")
link("Validate & clean", "Rejects log")
link("Merge sources", "Raw snapshot")

to_file_and_write("Dataset CSV", [2000, 20],
                  {"operation": "csv", "options": {"fileName": "groundline_dataset.csv"}},
                  DATA + "/clean/groundline_dataset.csv", "Final dataset")
to_file_and_write("Dataset JSON", [2000, 180],
                  {"operation": "toJson", "mode": "once", "options": {"format": True, "fileName": "groundline_dataset.json"}},
                  DATA + "/clean/groundline_dataset.json", "Final dataset")
to_file_and_write("Report MD", [2000, 340],
                  {"operation": "toText", "sourceProperty": "markdown", "options": {"fileName": "quality_report.md"}},
                  DATA + "/clean/quality_report.md", "Quality report")
to_file_and_write("Report JSON", [2000, 480],
                  {"operation": "toText", "sourceProperty": "report_json", "options": {"fileName": "quality_report.json"}},
                  DATA + "/clean/quality_report.json", "Quality report")
to_file_and_write("Rejects CSV", [2000, 640],
                  {"operation": "csv", "options": {"fileName": "rejects_log.csv"}},
                  DATA + "/clean/rejects_log.csv", "Rejects log")
to_file_and_write("Raw JSON", [2000, 820],
                  {"operation": "toText", "sourceProperty": "snapshot_json", "options": {"fileName": "raw.json"}},
                  DATA + "/raw/{{ $('Raw snapshot').first().json.file_name }}", "Raw snapshot")

workflow = {
    "id": WORKFLOW_ID,
    "name": "Groundline — Data Pipeline (INFO 7375 A3)",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"},
    "pinData": {},
    "active": False,
    "tags": [],
}
OUT.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} ({len([n for n in nodes if 'stickyNote' not in n['type']])} nodes)")

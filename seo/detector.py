from __future__ import annotations
import csv
import os
from collections import defaultdict


def load_rows(export_dir: str) -> list[dict]:
    path = os.path.join(export_dir, "internal_all.csv")
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _int(v, default=0):
    try:
        return int(float(str(v).strip()))
    except Exception:
        return default


def _float(v, default=0.0):
    try:
        return float(str(v).strip())
    except Exception:
        return default


def is_html(r):   return "text/html" in (r.get("Content Type", "") or "").lower()
def is_200(r):    return _int(r.get("Status Code")) == 200
def indexable(r): return (r.get("Indexability", "") or "").strip().lower() == "indexable"


def detect(rows: list[dict]) -> list[dict]:
    issues = []

    def add(t, sev, urls, explanation):
        urls = sorted(set(urls))
        if urls:
            issues.append({"type": t, "severity": sev, "affected_urls": urls,
                           "count": len(urls), "explanation": explanation})

    html  = [r for r in rows if is_html(r)]
    idx200 = [r for r in html if is_200(r) and indexable(r)]

    # --- Missing title ---
    add("missing_title", "High",
        [r["Address"] for r in idx200 if not (r.get("Title 1", "") or "").strip()],
        "Indexable pages with no title tag.")

    # --- Duplicate title ---
    by_title = defaultdict(list)
    for r in idx200:
        t = (r.get("Title 1", "") or "").strip()
        if t:
            by_title[t].append(r["Address"])
    dup_t = [u for urls in by_title.values() if len(urls) > 1 for u in urls]
    add("duplicate_title", "High", dup_t, "Pages sharing an identical title.")

    # --- Title too long ---
    add("title_too_long", "Medium",
        [r["Address"] for r in idx200
         if _int(r.get("Title 1 Pixel Width")) > 561 or _int(r.get("Title 1 Length")) > 60],
        "Titles likely truncated in search results.")

    # --- Title too short ---
    add("title_too_short", "Low",
        [r["Address"] for r in idx200
         if (r.get("Title 1", "") or "").strip() and _int(r.get("Title 1 Length")) < 30],
        "Titles too short to be descriptive.")

    # --- Missing meta description ---
    add("missing_meta_description", "Medium",
        [r["Address"] for r in idx200 if not (r.get("Meta Description 1", "") or "").strip()],
        "Indexable pages with no meta description.")

    # --- Duplicate meta description ---
    by_meta = defaultdict(list)
    for r in idx200:
        m = (r.get("Meta Description 1", "") or "").strip()
        if m:
            by_meta[m].append(r["Address"])
    dup_m = [u for urls in by_meta.values() if len(urls) > 1 for u in urls]
    add("duplicate_meta_description", "Medium", dup_m, "Pages sharing an identical meta description.")

    # --- Meta description too long ---
    add("meta_description_too_long", "Low",
        [r["Address"] for r in idx200
         if _int(r.get("Meta Description 1 Length")) > 155],
        "Meta descriptions too long, will be truncated.")

    # --- Missing H1 ---
    pages_200 = [r for r in html if is_200(r)]
    add("missing_h1", "Medium",
        [r["Address"] for r in pages_200 if not (r.get("H1-1", "") or "").strip()],
        "Pages with no H1 tag.")

    # --- Duplicate H1 ---
    by_h1 = defaultdict(list)
    for r in idx200:
        h = (r.get("H1-1", "") or "").strip()
        if h:
            by_h1[h].append(r["Address"])
    dup_h1 = [u for urls in by_h1.values() if len(urls) > 1 for u in urls]
    add("duplicate_h1", "Low", dup_h1, "Pages sharing an identical H1.")

    # --- Broken links (4xx) ---
    add("broken_link", "High",
        [r["Address"] for r in rows if 400 <= _int(r.get("Status Code")) <= 499],
        "URLs returning a client error (4xx).")

    # --- Server errors (5xx) ---
    add("server_error", "High",
        [r["Address"] for r in rows if 500 <= _int(r.get("Status Code")) <= 599],
        "URLs returning a server error (5xx).")

    # --- Redirects (3xx) ---
    add("redirect", "Medium",
        [r["Address"] for r in rows if 300 <= _int(r.get("Status Code")) <= 399],
        "URLs that redirect (3xx).")

    # --- Redirect chains ---
    redirect_map = {}
    for r in rows:
        if 300 <= _int(r.get("Status Code")) <= 399:
            redirect_map[r["Address"]] = (r.get("Redirect URL", "") or "").strip()
    chain_urls = [url for url, target in redirect_map.items() if target in redirect_map]
    add("redirect_chain", "High", chain_urls,
        "Redirects pointing to another redirect (chains/loops).")

    # --- Thin content ---
    add("thin_content", "Low",
        [r["Address"] for r in idx200 if _int(r.get("Word Count")) < 200],
        "Indexable pages with fewer than 200 words.")

    # --- Orphan pages ---
    add("orphan_page", "Medium",
        [r["Address"] for r in idx200 if _int(r.get("Inlinks")) == 0],
        "Indexable pages with zero internal links in.")

    # --- Non-indexable but linked ---
    add("non_indexable_but_linked", "Medium",
        [r["Address"] for r in html
         if (r.get("Indexability", "") or "").strip().lower() == "non-indexable"
         and _int(r.get("Inlinks")) > 0],
        "Non-indexable pages that still receive internal links.")

    # --- Slow pages ---
    add("slow_page", "Low",
        [r["Address"] for r in rows if _float(r.get("Response Time")) > 1.0],
        "Pages taking more than 1 second to respond.")

    return issues


def summarize(issues: list[dict]) -> dict:
    by_sev = defaultdict(int)
    for i in issues:
        by_sev[i["severity"]] += 1
    return {"total_issues": len(issues),
            "by_severity": {"High": by_sev["High"], "Medium": by_sev["Medium"], "Low": by_sev["Low"]}}


if __name__ == "__main__":
    import sys, json
    d = sys.argv[1] if len(sys.argv) > 1 else "../sample-export"
    rows = load_rows(d)
    iss = detect(rows)
    print(f"Loaded {len(rows)} rows, detected {len(iss)} issue types.")
    print(json.dumps(summarize(iss), indent=2))
    for i in iss:
        print(f"  [{i['severity']:<6}] {i['type']:<30} x{i['count']}")
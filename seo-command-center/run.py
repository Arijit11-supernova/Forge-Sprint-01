#!/usr/bin/env python3
"""
run.py — headless runner for the SEO Command Center (also the grader's entry point).

Runs the full pipeline on a Screaming Frog export with no Claude Code:
  load -> detect -> (starter recommendations) -> write report.json + report.html

Usage:
  python run.py sample-export/
  python run.py sample-export/ --no-dashboard

The model-driven fixes (title rewriting, redirect map) are left as a Sprint TODO; the
starter writes empty fix blocks so the contract stays valid.
"""
from __future__ import annotations
import argparse, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mcp"))
sys.path.insert(0, HERE)
import server  # the MCP server module exposes every tool as a function


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export_dir")
    ap.add_argument("--no-dashboard", action="store_true")
    args = ap.parse_args()

    if not args.no_dashboard:
        server.start_dashboard()
        print(f"[seo] dashboard: http://localhost:{server.PORT}", flush=True)
        time.sleep(1)

    t0 = time.time()
    server.seo_load(args.export_dir)
    server.seo_detect()

    # --- Title Fixer ---
    issues = server.RUN["issues"]
    rows = server.RUN.get("rows", [])
    title_issue = next((i for i in issues if i["type"] == "missing_title"), None)

    if title_issue:
        urls_to_fix = title_issue["affected_urls"][:5]
        fixed_titles = []

        import urllib.request, json
        for url in urls_to_fix:
            row = next((r for r in rows if r["Address"] == url), {})
            h1 = row.get("H1-1", "").strip()
            slug = url.split("/")[-1] or url.split("/")[-2] if "/" in url else url
            context = h1 if h1 else slug

            prompt = f"Rewrite a professional SEO title for a page. Context (H1 or slug): {context}. Constraints: 30-60 chars, return ONLY the title text."
            try:
                req = urllib.request.Request(
                    "http://localhost:11434/api/generate",
                    data=json.dumps({"model": "gemma4:31b", "prompt": prompt, "stream": False}).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    new_title = res_json.get("response", "").strip().replace('"', '')
                    if 30 <= len(new_title) <= 60:
                        fixed_titles.append({"url": url, "old": "", "new": new_title})
            except Exception as e:
                print(f"Ollama error for {url}: {e}")

        if fixed_titles:
            server.seo_set_fixes(titles=fixed_titles)

    # starter recommendations from the detected issues (the skill writes richer ones)
    issues = sorted(server.RUN["issues"], key=lambda x: {"High":0,"Medium":1,"Low":2}.get(x["severity"],3))
    recs = []
    for i in issues[:5]:
        recs.append(f"Fix the {i['count']} {i['severity']}-severity '{i['type']}' issue(s) first.")
    if not recs:
        recs.append("No issues detected on this crawl.")
    server.seo_recommend(recs)
    server.RUN["model_calls"] = len(fixed_titles) if 'fixed_titles' in locals() else 0
    server.RUN["duration_sec"] = round(time.time() - t0, 1)
    server.seo_report()
    server.seo_export()

    # --- PPTX Report Generator ---
    try:
        from pptx import Presentation
        from datetime import date
        import os

        data = server.RUN
        prs = Presentation()

        # Slide 1: Title
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = f"SEO Audit Report: {data['site']}"
        slide.placeholders[1].text = f"Generated on {date.today()}\nSEO Command Center"

        # Slide 2: Summary
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Executive Summary"
        sum_data = data['summary'] or {}
        by_sev = sum_data.get('by_severity', {})
        summary_text = (f"Total URLs Crawled: {data['urls']}\n"
                        f"Total Issues Detected: {sum_data.get('total_issues', 0)}\n\n"
                        f"High Severity: {by_sev.get('High', 0)}\n"
                        f"Medium Severity: {by_sev.get('Medium', 0)}\n"
                        f"Low Severity: {by_sev.get('Low', 0)}")
        slide.placeholders[1].text = summary_text

        # Slide 3: High Severity
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Critical Issues (High)"
        high_issues = [i for i in data['issues'] if i['severity'] == 'High']
        slide.placeholders[1].text = "\n".join([f"- {i['type']}: {i['count']} pages" for i in high_issues]) if high_issues else "No high severity issues found."

        # Slide 4: Medium Severity
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Warning Issues (Medium)"
        med_issues = [i for i in data['issues'] if i['severity'] == 'Medium']
        slide.placeholders[1].text = "\n".join([f"- {i['type']}: {i['count']} pages" for i in med_issues]) if med_issues else "No medium severity issues found."

        # Slide 5: Recommendations
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Top Recommendations"
        recs = data.get('recommendations', [])
        slide.placeholders[1].text = "\n".join([f"- {r}" for r in recs]) if recs else "No recommendations generated."

        pptx_path = os.path.join(server.OUT_DIR, "report.pptx")
        prs.save(pptx_path)
        print(f"Wrote {pptx_path}")
    except ImportError:
        print("Skipping PPTX report: python-pptx not installed. Run 'pip install python-pptx' to enable.")
    except Exception as e:
        print(f"Error generating PPTX report: {e}")

    s = server.RUN["summary"]
    print("\n=== SEO AUDIT RESULT ===")
    print(f"Site         : {server.RUN['site']}  ({server.RUN['urls']} URLs)")
    print(f"Total issues : {s['total_issues']}  (High {s['by_severity'].get('High',0)} / "
          f"Medium {s['by_severity'].get('Medium',0)} / Low {s['by_severity'].get('Low',0)})")
    print("Wrote outputs/report.json and outputs/report.html")


if __name__ == "__main__":
    main()

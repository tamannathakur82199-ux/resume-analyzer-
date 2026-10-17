"""Command-line version.

Examples
--------
python cli.py --jd sample_data/job_description.txt --resumes sample_data/resumes
python cli.py --jd jd.txt --resumes resume1.pdf resume2.docx --threshold 65 --must-have "Python,SQL"
"""
import argparse
import csv
import os
import sys

from analyzer import ai_label, analyze_files, collect_paths, formatted_resume, results_rows, safe_name
from report_generator import build_report_pdf
from resume_parser import extract_text


def main():
    ap = argparse.ArgumentParser(description="AI Resume Analyzer - analyse, shortlist and fix resumes")
    ap.add_argument("--jd", required=True, help="job description file (.txt / .pdf / .docx)")
    ap.add_argument("--resumes", nargs="+", required=True, help="resume files and/or folders")
    ap.add_argument("--threshold", type=float, default=60, help="shortlist cut-off percentage (default 60)")
    ap.add_argument("--must-have", default="", help="comma separated must-have skills")
    ap.add_argument("--out", default="output", help="output folder (default: output)")
    ap.add_argument("--ai-hold", action="store_true",
                    help="move resumes that look AI-written from Shortlisted to On Hold (manual review)")
    ap.add_argument("--ai-sensitivity", choices=["strict", "balanced", "sensitive"], default="balanced",
                    help="how readily resumes are flagged as AI-written (default: balanced)")
    ap.add_argument("--all-formatted", action="store_true",
                    help="build a formatted resume for every candidate (default: only non-compliant ones)")
    args = ap.parse_args()

    paths = collect_paths(args.resumes)
    if not paths:
        sys.exit("No .pdf / .docx / .txt resumes found.")
    jd_text, _ = extract_text(args.jd)
    files = []
    for p in paths:
        with open(p, "rb") as fh:
            files.append((os.path.basename(p), fh.read()))

    must = [s for s in args.must_have.split(",") if s.strip()]
    jd, results = analyze_files(files, jd_text, args.threshold, must, args.ai_hold, args.ai_sensitivity)

    os.makedirs(args.out, exist_ok=True)
    fmt_dir = os.path.join(args.out, "formatted_resumes")
    os.makedirs(fmt_dir, exist_ok=True)

    print(f"\nJob needs: {', '.join(jd['skills']) or '-'}  |  min experience: {jd['min_years']:g} yrs")
    print(f"Cut-off: {args.threshold:.0f}%\n")
    print(f"{'#':<3}{'Candidate':<22}{'Status':<13}{'Overall':>8}{'Skills':>8}{'Format':>8}  {'Format OK':<10}AI-written check")
    print("-" * 92)
    for i, r in enumerate(results, 1):
        print(f"{i:<3}{r['name'][:21]:<22}{r['status']:<13}{r['overall']:>7}%{r['skill_score']:>7}%"
              f"{r['format_score']:>8}  {'yes' if r['format_ok'] else 'NO':<10}{ai_label(r)}")
        if args.all_formatted or not r["format_ok"]:
            data = formatted_resume(r, "docx")
            if data:
                base = safe_name(os.path.splitext(r["file"])[0])
                with open(os.path.join(fmt_dir, f"{base}_formatted.docx"), "wb") as fh:
                    fh.write(data)
                with open(os.path.join(fmt_dir, f"{base}_formatted.pdf"), "wb") as fh:
                    fh.write(formatted_resume(r, "pdf"))

    rows = results_rows(results)
    with open(os.path.join(args.out, "shortlist.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(os.path.join(args.out, "analysis_report.pdf"), "wb") as fh:
        fh.write(build_report_pdf(results, jd, args.threshold))

    print(f"\nShortlisted: {sum(r['status'] == 'Shortlisted' for r in results)} / {len(results)}")
    print(f"Saved: {args.out}/shortlist.csv, {args.out}/analysis_report.pdf, {fmt_dir}/")


if __name__ == "__main__":
    main()

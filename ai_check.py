"""Check resumes for AI-written text only (no job description needed).

Examples
--------
python ai_check.py sample_data/resumes
python ai_check.py resume1.pdf resume2.docx --out ai_check.csv

The result is an indicator, not proof. See README.md.
"""
import argparse
import csv
import os
import sys

from analyzer import ai_check_rows, check_ai_files, collect_paths


def main():
    ap = argparse.ArgumentParser(description="Check whether resumes look AI-written")
    ap.add_argument("resumes", nargs="+", help="resume files (.pdf/.docx/.txt) and/or folders")
    ap.add_argument("--out", help="optional CSV file for the results")
    ap.add_argument("--sensitivity", choices=["strict", "balanced", "sensitive"], default="balanced",
                    help="strict = fewer false alarms, sensitive = flags more (default: balanced)")
    ap.add_argument("--details", action="store_true", help="also print reasons and the most AI-sounding lines")
    args = ap.parse_args()

    paths = collect_paths(args.resumes)
    if not paths:
        sys.exit("No .pdf / .docx / .txt resumes found.")
    files = []
    for p in paths:
        with open(p, "rb") as fh:
            files.append((os.path.basename(p), fh.read()))
    results = check_ai_files(files, args.sensitivity)

    print(f"\n{'#':<3}{'Candidate':<24}{'Indicator':>10}  Verdict")
    print("-" * 78)
    for i, r in enumerate(results, 1):
        print(f"{i:<3}{r['name'][:23]:<24}{r['score']:>9}   {r['verdict']}")
        if r.get("error"):
            print(f"     ! {r['error']}")
        if args.details:
            for sig in r["signals"]:
                print(f"     - {sig['name']}: {sig['detail']} (+{sig['points']})")
            for item in r["suspicious_lines"][:3]:
                print(f"     > {item['line'][:110]}")
    print("\nIndicator only - not proof. Verify with an interview or a practical task.")

    if args.out:
        rows = ai_check_rows(results)
        with open(args.out, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()

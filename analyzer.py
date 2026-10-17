"""High-level pipeline used by both the Streamlit app and the CLI."""
from __future__ import annotations

import os
import re

from ai_detector import check_text, verdict_text
from matcher import analyze_resume, parse_job_description, rank
from resume_builder import build_profile, build_resume_docx, build_resume_pdf
from resume_parser import extract_text

SUPPORTED = (".pdf", ".docx", ".txt")


def ai_label(result) -> str:
    check = result.get("ai_check") or {"level": "Not checked", "score": 0}
    if check["level"] in ("Not checked", "Not enough text"):
        return check["level"]
    return f"{check['level']} ({check['score']})"


def analyze_files(files, jd_text: str, threshold: float = 60.0, must_have=None, ai_hold: bool = False,
                  ai_sensitivity: str = "balanced"):
    """files: iterable of (filename, bytes). Returns ranked list of result dicts.

    ai_hold=True moves resumes that look AI-written from 'Shortlisted' to 'On Hold' for manual review.
    """
    jd = parse_job_description(jd_text, must_have)
    results = []
    for filename, data in files:
        try:
            text, meta = extract_text(data, filename)
        except Exception as exc:  # corrupt / unsupported file
            results.append(_failed(filename, f"Could not read file: {exc}"))
            continue
        if len(text.strip()) < 30:
            results.append(_failed(filename, "No readable text found (scanned image or empty file). "
                                             "Save the resume as a text-based PDF or DOCX."))
            continue
        results.append(analyze_resume(text, jd, meta, threshold, filename, ai_hold, ai_sensitivity))
    return jd, rank(results)


def _failed(filename, reason):
    return {"file": filename, "name": filename, "email": "", "phone": "", "status": "Rejected",
            "overall": 0.0, "skill_score": 0.0, "tfidf_score": 0.0, "exp_score": 0.0,
            "format_score": 0, "format_ok": False, "experience_years": 0.0, "matched_skills": [],
            "missing_skills": [], "extra_skills": [], "must_missing": [], "strengths": [],
            "issues": [{"severity": "critical", "message": reason, "suggestion": reason, "penalty": 15}],
            "suggestions": [reason], "reasons": [reason], "parsed": None, "error": True,
            "ai_check": {"score": 0, "level": "Not checked", "signals": [], "words": 0, "note": ""}}


def results_dataframe(results):
    import pandas as pd  # only needed by the web app
    return pd.DataFrame(results_rows(results))


def results_rows(results) -> list:
    """Ranking as a list of plain dicts (used for CSV export without pandas)."""
    rows = []
    for i, r in enumerate(results, 1):
        rows.append({
            "Rank": i, "Candidate": r["name"], "File": r["file"], "Status": r["status"],
            "Overall %": r["overall"], "Skill Match %": r["skill_score"],
            "Text Match %": r["tfidf_score"], "Experience (yrs)": r["experience_years"],
            "Format Score": r["format_score"],
            "Format OK": "Yes" if r["format_ok"] else "No",
            "AI Check": ai_label(r),
            "Matched Skills": ", ".join(r["matched_skills"]),
            "Missing Skills": ", ".join(r["missing_skills"]),
            "Email": r["email"], "Phone": r["phone"],
        })
    return rows


def formatted_resume(result, kind: str = "docx") -> bytes | None:
    """Resume rebuilt in the required format from what the candidate already wrote."""
    if not result.get("parsed"):
        return None
    profile = build_profile(result["parsed"])
    return build_resume_docx(profile) if kind == "docx" else build_resume_pdf(profile)


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_") or "resume"


def collect_paths(items):
    paths = []
    for item in items:
        if os.path.isdir(item):
            paths += [os.path.join(item, f) for f in sorted(os.listdir(item))
                      if f.lower().endswith(SUPPORTED)]
        elif item.lower().endswith(SUPPORTED) and os.path.isfile(item):
            paths.append(item)
    return paths


# --------------------------------------------------------------------------- standalone AI check
def check_ai_files(files, sensitivity: str = "balanced"):
    """files: iterable of (filename, bytes). AI-written check only - no job description needed."""
    out = []
    for filename, data in files:
        row = {"file": filename, "name": filename, "error": None}
        try:
            text, meta = extract_text(data, filename)
        except Exception as exc:
            row.update(error=f"Could not read file: {exc}", level="Not checked", score=0, signals=[],
                       suspicious_lines=[], words=0, verdict="Not checked", note="")
            out.append(row)
            continue
        if len(text.strip()) < 30:
            row.update(error="No readable text found (scanned image or empty file).", level="Not checked",
                       score=0, signals=[], suspicious_lines=[], words=0, verdict="Not checked", note="")
            out.append(row)
            continue
        res = check_text(text, meta, sensitivity)
        row.update(res)
        row["name"] = res.get("name") or filename
        row["verdict"] = verdict_text(res)
        out.append(row)
    return sorted(out, key=lambda r: -r["score"])


def ai_check_rows(results) -> list:
    return [{"Rank": i, "Candidate": r["name"], "File": r["file"], "Verdict": r["verdict"],
             "AI Indicator (0-100)": r["score"], "Level": r["level"],
             "Reasons": "; ".join(s["name"] for s in r["signals"]), "Words": r["words"]}
            for i, r in enumerate(results, 1)]

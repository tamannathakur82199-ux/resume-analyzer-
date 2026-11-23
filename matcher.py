"""Job-description parsing, resume scoring and shortlisting."""
from __future__ import annotations

import re

from ai_detector import advice_for_candidate, detect_ai_written
from format_checker import check_format
from resume_parser import find_skills, parse_resume
from skills_db import SKILL_CATEGORY
from textsim import tfidf_cosine

# weights (when the JD lists skills)
W_SKILL, W_TFIDF, W_EXP, W_FORMAT = 0.45, 0.25, 0.15, 0.15
# weights when no skill could be detected in the JD
W2_TFIDF, W2_EXP, W2_FORMAT = 0.60, 0.20, 0.20
TFIDF_FULL_SCORE = 0.40       # cosine similarity that is treated as a 100 % textual match
ON_HOLD_BAND = 15             # points below the threshold that still qualify as "On Hold"


def parse_job_description(jd_text: str, must_have=None) -> dict:
    skills = list(find_skills(jd_text, fuzzy=False).keys())
    years = 0.0
    m = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:-\s*\d+\s*)?(?:years?|yrs?)", jd_text, re.I)
    if m:
        years = float(m.group(1))
    must = []
    for item in (must_have or []):
        item = item.strip()
        if not item:
            continue
        canon = list(find_skills(item, fuzzy=False).keys())
        must.append(canon[0] if canon else item)
        if canon and canon[0] not in skills:
            skills.append(canon[0])
    return {"text": jd_text, "skills": skills, "min_years": years, "must_have": must}


def tfidf_similarity(jd_text: str, resume_text: str) -> float:
    return tfidf_cosine(jd_text, resume_text)


def analyze_resume(text: str, jd: dict, meta: dict | None = None, threshold: float = 60.0,
                   filename: str = "resume", ai_hold: bool = False, ai_sensitivity: str = "balanced") -> dict:
    parsed = parse_resume(text, meta)
    fmt = check_format(parsed, meta)
    ai = detect_ai_written(parsed, ai_sensitivity)

    resume_skills = set(parsed["skills"])
    jd_skills = jd["skills"]
    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]
    extra = sorted(resume_skills - set(jd_skills))
    must_missing = [s for s in jd["must_have"] if s not in resume_skills]

    cos = tfidf_similarity(jd["text"], text)
    tfidf_score = min(100.0, cos / TFIDF_FULL_SCORE * 100)
    skill_score = (len(matched) / len(jd_skills) * 100) if jd_skills else 0.0
    min_years = jd["min_years"]
    exp_score = 100.0 if min_years <= 0 else min(100.0, parsed["experience_years"] / min_years * 100)

    if jd_skills:
        overall = (W_SKILL * skill_score + W_TFIDF * tfidf_score + W_EXP * exp_score + W_FORMAT * fmt["score"])
    else:
        overall = W2_TFIDF * tfidf_score + W2_EXP * exp_score + W2_FORMAT * fmt["score"]
    overall = round(overall, 1)

    reasons = []
    if overall >= threshold and not must_missing:
        status = "Shortlisted"
        reasons.append(f"Overall score {overall} is above the cut-off of {threshold:.0f}.")
    elif overall >= threshold - ON_HOLD_BAND:
        status = "On Hold"
        if must_missing:
            reasons.append("Missing must-have skill(s): " + ", ".join(must_missing) + ".")
        else:
            reasons.append(f"Score {overall} is slightly below the cut-off of {threshold:.0f}.")
    else:
        status = "Rejected"
        reasons.append(f"Score {overall} is well below the cut-off of {threshold:.0f}.")
        if must_missing:
            reasons.append("Missing must-have skill(s): " + ", ".join(must_missing) + ".")
    if status == "Shortlisted" and not (parsed["email"] or parsed["phone"]):
        status = "On Hold"
        reasons.append("No email / phone found - the candidate cannot be contacted until the resume is fixed.")
    if ai["level"] == "Likely":
        if ai_hold and status == "Shortlisted":
            status = "On Hold"
            reasons.append(f"Resume looks AI-written (indicator {ai['score']}/100) - held for manual review.")
        else:
            reasons.append(f"Resume looks AI-written (indicator {ai['score']}/100) - verify the claims in the interview.")
    elif ai["level"] == "Possible":
        reasons.append(f"Some parts may be AI-written (indicator {ai['score']}/100).")
    if min_years and parsed["experience_years"] < min_years:
        reasons.append(f"Experience {parsed['experience_years']} yrs < required {min_years:g} yrs.")
    if not fmt["compliant"]:
        reasons.append("Resume is not in the required format - fix suggestions provided.")

    suggestions = [f"[{i['severity'].upper()}] {i['message']} -> {i['suggestion']}"
                   for i in sorted(fmt["issues"], key=lambda x: -x["penalty"])]
    if missing:
        suggestions.append(
            "[SKILLS] The job needs: " + ", ".join(missing[:10]) +
            ". If you really know these, add them (with a project/usage line); otherwise plan to learn the top ones.")
    if tfidf_score < 40 and jd_skills:
        suggestions.append("[CONTENT] Wording is far from the job description - reuse its keywords "
                           "naturally in your summary, skills and project bullets.")
    ai_advice = advice_for_candidate(ai)
    if ai_advice:
        suggestions.append(ai_advice)

    return {
        "file": filename,
        "name": parsed["name"] or filename,
        "email": parsed["email"],
        "phone": parsed["phone"],
        "status": status,
        "overall": overall,
        "skill_score": round(skill_score, 1),
        "tfidf_score": round(tfidf_score, 1),
        "exp_score": round(exp_score, 1),
        "format_score": fmt["score"],
        "format_ok": fmt["compliant"],
        "experience_years": parsed["experience_years"],
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "must_missing": must_missing,
        "issues": fmt["issues"],
        "strengths": fmt["strengths"],
        "suggestions": suggestions,
        "reasons": reasons,
        "ai_check": ai,
        "parsed": parsed,
    }


def rank(results: list[dict]) -> list[dict]:
    order = {"Shortlisted": 0, "On Hold": 1, "Rejected": 2}
    return sorted(results, key=lambda r: (order[r["status"]], -r["overall"]))


def skills_by_category(skills):
    out = {}
    for s in skills:
        out.setdefault(SKILL_CATEGORY.get(s, "Other"), []).append(s)
    return out

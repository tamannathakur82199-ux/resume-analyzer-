"""Checks a parsed resume against the required (ATS-friendly) format.

Required format
---------------
1. Name + contact line (email, phone, LinkedIn / GitHub)
2. Professional Summary (2-3 lines)
3. Technical Skills (grouped)
4. Work Experience / Internships  (bullets, action verbs, numbers)
5. Projects                       (bullets)
6. Education (with years)
7. Certifications / Achievements (optional)
Single column, standard headings, no tables/graphics, 1 page (max 2).
"""
from __future__ import annotations

import re

from resume_parser import BULLET_RE, DATE_RANGE_RE
from skills_db import ACTION_VERBS

SEVERITY_PENALTY = {"critical": 15, "major": 8, "minor": 4}


def _bullets(lines):
    return [BULLET_RE.sub("", l).strip() for l in lines if BULLET_RE.match(l)]


def _content_lines(lines):
    return [BULLET_RE.sub("", l).strip() for l in lines if len(l.split()) >= 4]


def check_format(parsed: dict, meta: dict | None = None) -> dict:
    sec = parsed["sections"]
    issues, strengths = [], []

    def add(sev, msg, fix, penalty=None):
        issues.append({"severity": sev, "message": msg, "suggestion": fix,
                       "penalty": penalty if penalty is not None else SEVERITY_PENALTY[sev]})

    # ---- contact block
    if parsed["name"]:
        strengths.append("Candidate name is clearly detectable at the top.")
    else:
        add("major", "Name not found at the top of the resume.",
            "Put your full name as the first line, in a larger bold font.")
    if parsed["email"]:
        strengths.append("Email address present.")
    else:
        add("critical", "No email address found.",
            "Add a professional email (name@gmail.com) in the header.")
    if parsed["phone"]:
        strengths.append("Phone number present.")
    else:
        add("major", "No phone number found.", "Add a 10-digit mobile number in the header.")
    if not (parsed["linkedin"] or parsed["github"]):
        add("minor", "No LinkedIn / GitHub link.",
            "Add your LinkedIn and GitHub profile links - recruiters check them.")

    # ---- required sections
    if sec.get("summary"):
        strengths.append("Has a Professional Summary / Objective.")
    else:
        add("major", "Missing 'Professional Summary' section.",
            "Add a 2-3 line summary: who you are, top skills, and the role you want.")
    skills_items = parsed["skills_listed"]
    if not sec.get("skills"):
        add("critical", "Missing 'Skills' section.",
            "Add a 'Technical Skills' section with grouped skills (Languages, Frameworks, Databases, Tools).")
    else:
        strengths.append("Has a dedicated Skills section.")
        if len(skills_items) < 4:
            add("minor", "Skills section is very short.",
                "List at least 6-10 relevant skills, grouped by category.")
    if not sec.get("education"):
        add("critical", "Missing 'Education' section.",
            "Add Education with degree, college/university, year and CGPA/percentage.")
    else:
        strengths.append("Has an Education section.")
    has_exp, has_proj = bool(sec.get("experience")), bool(sec.get("projects"))
    if not has_exp and not has_proj:
        add("critical", "Neither 'Experience' nor 'Projects' section found.",
            "Add Projects (and Internships if any) - this is the proof of your skills.")
    else:
        if has_exp:
            strengths.append("Has a Work Experience / Internship section.")
        if has_proj:
            strengths.append("Has a Projects section.")
        if not has_proj:
            add("minor", "No 'Projects' section.",
                "Add 2-3 projects with tech stack and measurable outcome.")

    # ---- length
    wc, pages = parsed["word_count"], parsed.get("pages", 1)
    if wc < 150:
        add("major", f"Resume is too short ({wc} words).",
            "Expand projects, skills and education - aim for 300-600 words.")
    elif wc > 1000 or pages > 2:
        add("major", f"Resume is too long ({wc} words, {pages} pages).",
            "Trim to 1 page (max 2 for 5+ years of experience). Remove old/irrelevant details.")
    elif wc > 700 or pages == 2:
        add("minor", f"Resume is on the longer side ({wc} words).",
            "Freshers should keep it to 1 page; keep only the strongest points.")
    else:
        strengths.append("Length is in the ideal range.")

    # ---- bullet quality
    body = (sec.get("experience", []) + sec.get("projects", []))
    bullets = _bullets(body)
    if body:
        if len(bullets) < 2:
            add("major", "Experience/Projects are not written as bullet points.",
                "Use 2-4 short bullets per project or job instead of paragraphs.")
        else:
            strengths.append("Uses bullet points for experience/projects.")
            starts = [b.split()[0].lower().strip(",.") for b in bullets if b.split()]
            ratio = sum(s in ACTION_VERBS for s in starts) / max(1, len(starts))
            if ratio < 0.4:
                add("minor", "Most bullets do not start with an action verb.",
                    "Start bullets with verbs like Built, Developed, Designed, Optimized, Implemented.")
            else:
                strengths.append("Bullets start with strong action verbs.")
        if not re.search(r"\d+\s*%|\d{2,}|\b\d+\+|\b\d+x\b", " ".join(body)):
            add("minor", "No measurable results (numbers / %) in experience or projects.",
                "Quantify impact, e.g. 'improved accuracy to 92%' or 'processed 500+ resumes'.")
    long_lines = [l for l in parsed["raw_text"].split("\n") if len(l) > 300]
    if long_lines:
        add("minor", "Large unbroken blocks of text found.",
            "Break paragraphs into short bullet points - ATS and recruiters skim.")

    # ---- dates
    dated = DATE_RANGE_RE.search("\n".join(sec.get("education", []) + sec.get("experience", []))) \
        or re.search(r"(19|20)\d{2}", "\n".join(sec.get("education", [])))
    if (sec.get("education") or sec.get("experience")) and not dated:
        add("minor", "Dates / years are missing in Education or Experience.",
            "Add years (e.g. 2022 - 2025) for every degree and job so the timeline is clear.")

    # ---- layout hints
    raw = parsed["raw_text"]
    non_ascii = sum(1 for c in raw if ord(c) > 127 and c not in "•●▪■◦–—’‘“”·")
    if raw and non_ascii / len(raw) > 0.03:
        add("minor", "Unusual symbols/icons detected (possible tables, icons or graphics).",
            "Use plain text only - no icons, photos, tables or text boxes (ATS cannot read them).")
    if meta and meta.get("has_tables"):
        add("minor", "Resume uses tables.", "Switch to a single-column layout without tables.")
    first_person = re.search(r"\b(i am|i have|my name|i'm)\b", raw, re.I)
    if first_person:
        add("minor", "First-person sentences found ('I am', 'I have').",
            "Write in implied first person: 'Built a ...', not 'I built a ...'.")

    score = max(0, 100 - sum(i["penalty"] for i in issues))
    compliant = score >= 75 and not any(i["severity"] == "critical" for i in issues)
    return {"score": score, "compliant": compliant, "issues": issues, "strengths": strengths}

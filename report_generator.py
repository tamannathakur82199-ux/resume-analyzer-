"""PDF analysis report (summary table + one section per candidate)."""
from __future__ import annotations

import datetime as _dt
import os

from fpdf import FPDF

from analyzer import ai_label
from resume_builder import NAVY, _latin

LOGO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
STATUS_COLORS = {"Shortlisted": (30, 130, 76), "On Hold": (200, 130, 20), "Rejected": (180, 50, 50)}


def build_report_pdf(results, jd: dict, threshold: float) -> bytes:
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_margins(15, 14, 15)
    pdf.set_auto_page_break(True, 14)
    pdf.add_page()
    W = pdf.w - 30

    def h1(text):
        pdf.set_font("Helvetica", "B", 18); pdf.set_text_color(*NAVY)
        pdf.cell(0, 10, _latin(text), new_x="LMARGIN", new_y="NEXT")

    def h2(text):
        pdf.ln(2); pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(*NAVY)
        pdf.cell(0, 7, _latin(text), new_x="LMARGIN", new_y="NEXT")

    def body(text, style="", size=10, color=(30, 30, 30), indent=0):
        pdf.set_font("Helvetica", style, size); pdf.set_text_color(*color)
        pdf.set_x(pdf.l_margin + indent)
        pdf.multi_cell(W - indent, 5, _latin(text), new_x="LMARGIN", new_y="NEXT")

    h1("Parakh AI - Resume Analysis & Shortlisting Report")
    if os.path.exists(LOGO_FILE):
        try:
            pdf.image(LOGO_FILE, x=pdf.w - 32, y=13, w=17)
        except Exception:
            pass
    body(f"Generated on {_dt.date.today():%d %b %Y}  |  Resumes analysed: {len(results)}  |  "
         f"Shortlist cut-off: {threshold:.0f}%", color=(90, 90, 90))
    body("Skills required by the job: " + (", ".join(jd["skills"]) or "none detected"), size=9.5)
    if jd["min_years"]:
        body(f"Minimum experience: {jd['min_years']:g} years", size=9.5)
    if jd["must_have"]:
        body("Must-have skills: " + ", ".join(jd["must_have"]), size=9.5)

    h2("Ranking")
    cols = [("#", 8), ("Candidate", 42), ("Status", 22), ("Overall", 18), ("Skills", 18),
            ("Format", 18), ("Exp (yrs)", 18), ("AI check", 26)]
    pdf.set_font("Helvetica", "B", 9); pdf.set_fill_color(*NAVY); pdf.set_text_color(255, 255, 255)
    for title, w in cols:
        pdf.cell(w, 7, title, border=0, fill=True, align="C")
    pdf.ln(7)
    for i, r in enumerate(results, 1):
        pdf.set_text_color(30, 30, 30); pdf.set_font("Helvetica", "", 9)
        fill = i % 2 == 0
        pdf.set_fill_color(238, 242, 248)
        vals = [str(i), r["name"][:26], r["status"], f"{r['overall']}%", f"{r['skill_score']}%",
                f"{r['format_score']}", f"{r['experience_years']}", ai_label(r)]
        for (title, w), v in zip(cols, vals):
            if title == "Status":
                pdf.set_text_color(*STATUS_COLORS[r["status"]]); pdf.set_font("Helvetica", "B", 9)
            pdf.cell(w, 6.5, _latin(v), fill=fill, align="L" if title == "Candidate" else "C")
            pdf.set_text_color(30, 30, 30); pdf.set_font("Helvetica", "", 9)
        pdf.ln(6.5)

    for i, r in enumerate(results, 1):
        pdf.add_page()
        h1(f"{i}. {r['name']}")
        pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(*STATUS_COLORS[r["status"]])
        pdf.cell(0, 7, f"{r['status']}  -  overall {r['overall']}%", new_x="LMARGIN", new_y="NEXT")
        body(f"File: {r['file']}   Email: {r['email'] or '-'}   Phone: {r['phone'] or '-'}",
             size=9, color=(90, 90, 90))
        body(f"Skill match {r['skill_score']}%  |  Text (TF-IDF) match {r['tfidf_score']}%  |  "
             f"Experience {r['experience_years']} yrs ({r['exp_score']}%)  |  "
             f"Format score {r['format_score']}/100 "
             f"({'compliant' if r['format_ok'] else 'NOT in required format'})")
        h2("Decision")
        for reason in r["reasons"]:
            body("- " + reason, indent=3)
        ai = r.get("ai_check") or {}
        if ai.get("level") not in (None, "Not checked"):
            h2("AI-written check")
            body(f"{ai['level']}  (indicator {ai['score']}/100)", style="B", indent=3)
            for sig in ai.get("signals", []):
                body(f"- {sig['name']}: {sig['detail']} (+{sig['points']})", indent=3, size=9.5)
            body(ai.get("note", ""), style="I", size=8.5, color=(110, 110, 110), indent=3)
        h2("Skills")
        body("Matched: " + (", ".join(r["matched_skills"]) or "none"), indent=3)
        body("Missing: " + (", ".join(r["missing_skills"]) or "none"), indent=3, color=(160, 40, 40))
        if r["strengths"]:
            h2("Strengths")
            for s in r["strengths"]:
                body("- " + s, indent=3)
        if r["suggestions"]:
            h2("Suggestions to improve the resume")
            for s in r["suggestions"]:
                body("- " + s, indent=3, size=9.5)
    return bytes(pdf.output())

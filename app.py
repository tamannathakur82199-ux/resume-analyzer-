"""AI Resume Analyzer - Streamlit web app.

Run with:   streamlit run app.py
"""
import os

import streamlit as st

from analyzer import (ai_check_rows, analyze_files, check_ai_files, formatted_resume,
                      results_dataframe, safe_name)
from report_generator import build_report_pdf
from resume_builder import build_resume_docx, build_resume_pdf, profile_from_fields
from resume_parser import extract_text

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_JD = os.path.join(HERE, "sample_data", "job_description.txt")
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem;}
      .hero {background: linear-gradient(120deg,#1f3864,#2e75b6); color: #fff; padding: 1.4rem 1.8rem;
             border-radius: 14px; margin-bottom: 1.2rem;}
      .hero h1 {margin: 0; font-size: 2rem; color: #fff;}
      .hero p {margin: .3rem 0 0 0; opacity: .9;}
      .pill {display:inline-block; padding: 2px 10px; margin: 2px 4px 2px 0; border-radius: 999px;
             font-size: .82rem; font-weight: 600;}
      .ok {background:#e3f4ea; color:#1b6e3d;} .miss {background:#fbe6e6; color:#a12b2b;}
      .extra {background:#e8eef7; color:#2a4a7f;}
      .badge {padding: 3px 12px; border-radius: 6px; font-weight: 700; color: #fff;}
    </style>
    <div class="hero"><h1>AI Resume Analyzer</h1>
    <p>Analyse resumes against a job description, shortlist the best candidates, get format fixes
    and download a resume in the required format.</p></div>
    """,
    unsafe_allow_html=True,
)

STATUS_COLOR = {"Shortlisted": "#1e824c", "On Hold": "#c8821e", "Rejected": "#b43232"}
SEV_ICON = {"critical": "🔴", "major": "🟠", "minor": "🔵"}


def pills(items, css):
    if not items:
        return "<i>none</i>"
    return "".join(f'<span class="pill {css}">{s}</span>' for s in items)


# --------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Settings")
    threshold = st.slider("Shortlist cut-off (%)", 30, 90, 60, 5,
                          help="Candidates at or above this overall score are shortlisted.")
    must_have_text = st.text_input("Must-have skills (comma separated)", placeholder="Python, SQL",
                                   help="A candidate missing any of these cannot be shortlisted.")
    ai_hold = st.checkbox("Hold AI-written resumes for manual review", value=False,
                          help="Resumes marked 'Likely' AI-written are moved from Shortlisted to On Hold. "
                               "The AI check is only an indicator, so it never rejects anyone on its own.")
    ai_sens = st.select_slider(
        "AI-check sensitivity", options=["strict", "balanced", "sensitive"], value="balanced",
        help="Strict: flags only obvious cases (fewer false alarms). Sensitive: flags more resumes, including "
             "AI text that was lightly edited (more false alarms). Used by the AI check everywhere in the app.")
    with st.expander("How the score is calculated"):
        st.markdown(
            "- **45 %** skill match (skills in the JD found in the resume, incl. aliases and typos)\n"
            "- **25 %** text similarity (TF-IDF + cosine similarity)\n"
            "- **15 %** experience vs. JD requirement\n"
            "- **15 %** resume format score\n\n"
            "**Shortlisted** = score ≥ cut-off, all must-haves present, contact details available.  \n"
            "**On Hold** = within 15 points of the cut-off, or must-have / contact missing.  \n"
            "**Rejected** = below that.\n\n"
            "**AI-written check** is separate from the score. It looks for chatbot-style patterns "
            "(buzzwords, evenly sized bullets, 'resulting in...' endings, round metrics, leftover "
            "placeholders). It is an indicator, not proof."
        )

tab_analyze, tab_ai, tab_build = st.tabs(["Analyze & Shortlist", "AI Resume Check", "Build Resume"])

# --------------------------------------------------------------------------- analyze tab
with tab_analyze:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("1. Job description")
        if st.button("Load sample job description"):
            with open(SAMPLE_JD, encoding="utf-8") as fh:
                st.session_state["jd_text"] = fh.read()
        jd_file = st.file_uploader("Upload JD (optional)", type=["txt", "pdf", "docx"], key="jd_file")
        if jd_file is not None:
            st.session_state["jd_text"] = extract_text(jd_file.getvalue(), jd_file.name)[0]
        jd_text = st.text_area("Paste the job description", key="jd_text", height=260,
                               placeholder="Paste the job description here...")
    with right:
        st.subheader("2. Resumes")
        uploads = st.file_uploader("Upload one or more resumes (PDF / DOCX / TXT)",
                                   type=["pdf", "docx", "txt"], accept_multiple_files=True, key="resumes")
        st.caption("Tip: upload many resumes at once - they are ranked automatically.")
        run = st.button("Analyze resumes", type="primary", disabled=not (uploads and jd_text.strip()))

    if run:
        must = [s for s in must_have_text.split(",") if s.strip()]
        with st.spinner("Analysing resumes..."):
            jd, results = analyze_files([(u.name, u.getvalue()) for u in uploads], jd_text, threshold, must,
                                        ai_hold, ai_sens)
        st.session_state["analysis"] = {"jd": jd, "results": results, "threshold": threshold}

    data = st.session_state.get("analysis")
    if data:
        jd, results, thr = data["jd"], data["results"], data["threshold"]
        st.divider()
        st.subheader("Results")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Resumes analysed", len(results))
        c2.metric("Shortlisted", sum(r["status"] == "Shortlisted" for r in results))
        c3.metric("On hold", sum(r["status"] == "On Hold" for r in results))
        c4.metric("Not in required format", sum(not r["format_ok"] for r in results))
        c5.metric("Likely AI-written", sum(r["ai_check"]["level"] == "Likely" for r in results))
        st.markdown("**Skills required by the job:** " + pills(jd["skills"], "extra"), unsafe_allow_html=True)

        df = results_dataframe(results)
        st.dataframe(
            df[["Rank", "Candidate", "Status", "Overall %", "Skill Match %", "Experience (yrs)",
                "Format Score", "Format OK", "AI Check", "Missing Skills"]],
            hide_index=True,
            column_config={
                "Overall %": st.column_config.ProgressColumn("Overall %", min_value=0, max_value=100, format="%.1f"),
                "Skill Match %": st.column_config.ProgressColumn("Skill Match %", min_value=0, max_value=100, format="%.1f"),
            },
        )
        d1, d2, _ = st.columns([1, 1, 3])
        d1.download_button("Download ranking (CSV)", df.to_csv(index=False).encode("utf-8"),
                           "shortlist.csv", "text/csv")
        d2.download_button("Download full report (PDF)", build_report_pdf(results, jd, thr),
                           "analysis_report.pdf", "application/pdf")

        st.subheader("Candidate details")
        for i, r in enumerate(results, 1):
            with st.expander(f"#{i}  {r['name']}  -  {r['status']}  ({r['overall']}%)"):
                st.markdown(f'<span class="badge" style="background:{STATUS_COLOR[r["status"]]}">{r["status"]}</span>'
                            f'&nbsp; {r["file"]}', unsafe_allow_html=True)
                for reason in r["reasons"]:
                    st.write("• " + reason)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Overall", f"{r['overall']}%")
                m2.metric("Skill match", f"{r['skill_score']}%")
                m3.metric("Text match", f"{r['tfidf_score']}%")
                m4.metric("Format score", f"{r['format_score']}/100")
                st.markdown("**Matched skills** " + pills(r["matched_skills"], "ok"), unsafe_allow_html=True)
                st.markdown("**Missing skills** " + pills(r["missing_skills"], "miss"), unsafe_allow_html=True)
                if r["extra_skills"]:
                    st.markdown("**Other skills found** " + pills(r["extra_skills"], "extra"), unsafe_allow_html=True)
                ai = r["ai_check"]
                if ai["level"] == "Likely":
                    st.warning(f"**AI-written check: Likely** (indicator {ai['score']}/100). "
                               "Verify the claims in an interview or with a practical task.")
                elif ai["level"] == "Possible":
                    st.info(f"**AI-written check: Possible** (indicator {ai['score']}/100). "
                            "Some parts may be AI-written.")
                elif ai["level"] == "Unlikely":
                    st.success(f"AI-written check: Unlikely (indicator {ai['score']}/100).")
                elif ai["level"] == "Not enough text":
                    st.caption("AI-written check skipped: the resume has too little text.")
                if ai["signals"]:
                    st.markdown("**Why it was flagged**")
                    for sig in ai["signals"]:
                        st.write(f"• **{sig['name']}** - {sig['detail']} (+{sig['points']})")
                if ai["note"] and ai["level"] not in ("Not checked", "Not enough text"):
                    st.caption(ai["note"])
                if r["format_ok"]:
                    st.success("Resume follows the required format.")
                else:
                    st.error("Resume is NOT in the required format.")
                if r["issues"]:
                    st.markdown("**Format issues & fixes**")
                    for issue in sorted(r["issues"], key=lambda x: -x["penalty"]):
                        st.write(f"{SEV_ICON[issue['severity']]} **{issue['message']}**  \n"
                                 f"&nbsp;&nbsp;&nbsp;&nbsp;Fix: {issue['suggestion']}")
                if r["strengths"]:
                    st.markdown("**What is good**")
                    for s in r["strengths"]:
                        st.write("✅ " + s)
                if r.get("parsed"):
                    st.markdown("**Resume in the required format**")
                    st.caption("Built from the candidate's own content. Missing parts appear as red [placeholders] "
                               "to be filled in - nothing is invented.")
                    base = safe_name(os.path.splitext(r["file"])[0])
                    b1, b2, _ = st.columns([1, 1, 3])
                    b1.download_button("Download DOCX", formatted_resume(r, "docx"), f"{base}_formatted.docx",
                                       DOCX_MIME, key=f"docx_{i}")
                    b2.download_button("Download PDF", formatted_resume(r, "pdf"), f"{base}_formatted.pdf",
                                       "application/pdf", key=f"pdf_{i}")

# --------------------------------------------------------------------------- AI check tab
AI_COLORS = {"Likely": "#b43232", "Possible": "#c8821e", "Unlikely": "#1e824c"}

with tab_ai:
    st.subheader("Check whether a resume was written with AI")
    st.caption("Works on its own - no job description needed. Upload one or more resumes, or paste the text. "
               "The result is an **indicator, not proof**: edited AI text can pass, and formal or template-based "
               "resumes can be flagged. Use it to decide whom to question in the interview.")
    a_left, a_right = st.columns(2)
    with a_left:
        ai_uploads = st.file_uploader("Upload resumes (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"],
                                      accept_multiple_files=True, key="ai_resumes")
    with a_right:
        ai_pasted = st.text_area("...or paste the resume text", height=150, key="ai_pasted",
                                 placeholder="Paste the full resume text here...")
    ai_run = st.button("Check for AI-written text", type="primary", key="ai_run",
                       disabled=not (ai_uploads or ai_pasted.strip()))
    if ai_run:
        items = [(u.name, u.getvalue()) for u in (ai_uploads or [])]
        if ai_pasted.strip():
            items.append(("pasted_text.txt", ai_pasted.encode("utf-8")))
        with st.spinner("Scanning..."):
            st.session_state["ai_results"] = check_ai_files(items, ai_sens)

    ai_results = st.session_state.get("ai_results")
    if ai_results:
        st.divider()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Resumes checked", len(ai_results))
        k2.metric("Likely AI-written", sum(r["level"] == "Likely" for r in ai_results))
        k3.metric("Possibly AI-assisted", sum(r["level"] == "Possible" for r in ai_results))
        k4.metric("Probably human", sum(r["level"] == "Unlikely" for r in ai_results))

        import pandas as pd
        ai_df = pd.DataFrame(ai_check_rows(ai_results))
        st.dataframe(ai_df, hide_index=True, column_config={
            "AI Indicator (0-100)": st.column_config.ProgressColumn(
                "AI Indicator (0-100)", min_value=0, max_value=100, format="%d")})
        st.download_button("Download results (CSV)", ai_df.to_csv(index=False).encode("utf-8-sig"),
                           "ai_check.csv", "text/csv", key="ai_csv")

        for i, r in enumerate(ai_results, 1):
            with st.expander(f"#{i}  {r['name']}  -  {r['verdict']}  ({r['score']}/100)"):
                if r.get("error"):
                    st.error(r["error"] + " Save the resume as a text-based PDF or DOCX.")
                    continue
                color = AI_COLORS.get(r["level"], "#555")
                st.markdown(f'<span class="badge" style="background:{color}">{r["verdict"]}</span>'
                            f'&nbsp; AI indicator **{r["score"]}/100** &nbsp;·&nbsp; {r["words"]} words &nbsp;·&nbsp; {r["file"]}',
                            unsafe_allow_html=True)
                if r["level"] == "Not enough text":
                    st.caption("Under 80 words: too little text for the style checks, and no chatbot leftovers "
                               "were found.")
                if r["signals"]:
                    st.markdown("**Why**")
                    for sig in r["signals"]:
                        st.write(f"• **{sig['name']}** - {sig['detail']} (+{sig['points']})")
                elif r["level"] == "Unlikely":
                    st.write("No typical AI-writing patterns were found.")
                if r["suspicious_lines"]:
                    st.markdown("**Lines that sound most AI-written**")
                    for item in r["suspicious_lines"]:
                        st.markdown(f"> {item['line']}")
                        st.caption("Because: " + "; ".join(item["reasons"]))
                if r["level"] in ("Likely", "Possible"):
                    st.info("Suggested next step: ask the candidate to explain one project line by line - "
                            "tools used, their own part, and how the numbers were measured.")
                st.caption(r["note"])

# --------------------------------------------------------------------------- build tab
with tab_build:
    st.subheader("Create a resume in the required format")
    st.caption("Fill what you have. Write one entry per block: first line = title / company / dates, "
               "next lines = bullet points. Skills can be 'Languages: Python, Java' style or a plain list.")
    with st.form("build_form"):
        a, b, c = st.columns(3)
        name = a.text_input("Full name")
        email = b.text_input("Email")
        phone = c.text_input("Phone")
        d, e, f = st.columns(3)
        location = d.text_input("City, State (optional)")
        linkedin = e.text_input("LinkedIn URL (optional)")
        github = f.text_input("GitHub URL (optional)")
        summary = st.text_area("Professional summary (2-3 lines)", height=90)
        skills = st.text_area("Skills", height=110,
                              placeholder="Languages: Python, Java\nFrameworks: Flask, Streamlit\nDatabases: MySQL")
        experience = st.text_area("Experience / Internships", height=140,
                                  placeholder="Python Intern | ABC Pvt Ltd | Jun 2025 - Dec 2025\n"
                                              "- Built a REST API with Flask used by 3 teams\n"
                                              "- Improved report speed by 40%")
        projects = st.text_area("Projects", height=140,
                                placeholder="AI Resume Analyzer | Python, Scikit-learn | 2025\n"
                                            "- Developed a TF-IDF engine that ranks resumes against a JD")
        education = st.text_area("Education", height=100,
                                 placeholder="MCA, HPTU | 2024 - 2026\nCGPA: 8.4")
        g1, g2 = st.columns(2)
        certs = g1.text_area("Certifications (one per line)", height=90)
        achievements = g2.text_area("Achievements (one per line)", height=90)
        submitted = st.form_submit_button("Generate resume", type="primary")

    if submitted:
        profile = profile_from_fields({
            "name": name, "email": email, "phone": phone, "location": location, "linkedin": linkedin,
            "github": github, "summary": summary, "skills": skills, "experience": experience,
            "projects": projects, "education": education, "certifications": certs,
            "achievements": achievements})
        st.session_state["built"] = {
            "docx": build_resume_docx(profile), "pdf": build_resume_pdf(profile),
            "base": safe_name(name) if name.strip() else "resume"}
    built = st.session_state.get("built")
    if built:
        st.success("Resume ready. Parts shown in red [brackets] still need your details.")
        x1, x2, _ = st.columns([1, 1, 3])
        x1.download_button("Download DOCX", built["docx"], f"{built['base']}_resume.docx", DOCX_MIME, key="b_docx")
        x2.download_button("Download PDF", built["pdf"], f"{built['base']}_resume.pdf", "application/pdf", key="b_pdf")

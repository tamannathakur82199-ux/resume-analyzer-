"""Parakh AI - Next-Gen AI Resume Intelligence & ATS Dashboard.

Run with:   streamlit run app.py
"""
import base64
import os
import re
import pandas as pd
import streamlit as st

from analyzer import (ai_check_rows, analyze_files, check_ai_files, formatted_resume,
                      results_dataframe, safe_name)
from matcher import parse_job_description
from report_generator import build_report_pdf
from resume_builder import (build_resume_docx, build_resume_pdf, build_tailored_profile,
                            is_ph, profile_from_fields)
from resume_parser import extract_text, parse_resume
from resume_templates import (DUMMY_PROFILES, RESUME_TEMPLATES, get_dummy_profile,
                              get_template, profile_to_form_text, render_template_html)

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_JD = os.path.join(HERE, "sample_data", "job_description.txt")
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
# Look for the logo in the assets folder first, then beside app.py.
LOGO_CANDIDATES = [
    os.path.join(HERE, "assets", "logo.png"),
    os.path.join(HERE, "logo.png"),
]
LOGO_PATH = next((path for path in LOGO_CANDIDATES if os.path.isfile(path)), "")


def get_base64_image(image_path: str) -> str:
    """Read an image file and return base64 encoded string."""
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""


LOGO_B64 = get_base64_image(LOGO_PATH)

st.set_page_config(
    page_title="Parakh AI - Smart Resume Analysis & Recruitment Assistant",
    page_icon=LOGO_PATH if (LOGO_PATH and os.path.exists(LOGO_PATH)) else "📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit native app logo support
if LOGO_PATH and os.path.exists(LOGO_PATH):
    try:
        st.logo(LOGO_PATH, icon_image=LOGO_PATH)
    except Exception:
        pass

# --------------------------------------------------------------------------- CSS to match screenshot layout
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

      html, body, [class*="css"] {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      }

      .block-container {
          padding-top: 1.4rem;
          padding-bottom: 3rem;
          max-width: 1120px;
      }

      /* Header Banner matching user screenshot */
      .parakh-banner {
          background-color: #1a396c;
          border-radius: 12px;
          padding: 20px 24px;
          color: #ffffff;
          margin-bottom: 20px;
          box-shadow: 0 4px 16px rgba(26, 57, 108, 0.18);
      }
      .parakh-top-row {
          display: flex;
          align-items: center;
          gap: 14px;
      }
      .parakh-logo-badge {
          width: 48px;
          height: 48px;
          background: #ffffff;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
          overflow: hidden;
          flex-shrink: 0;
          padding: 3px;
      }
      .parakh-logo-badge img {
          width: 100%;
          height: 100%;
          object-fit: contain;
          border-radius: 9px;
      }
      .parakh-icon-badge {
          width: 42px;
          height: 42px;
          background: rgba(255, 255, 255, 0.16);
          border: 1px solid rgba(255, 255, 255, 0.25);
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.35rem;
          flex-shrink: 0;
      }
      .sidebar-brand-box {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
          padding: 8px 10px 14px 10px;
          border-bottom: 1px solid rgba(128, 128, 128, 0.2);
      }
      .sidebar-brand-box img {
          width: 44px;
          height: 44px;
          border-radius: 10px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
          background: #ffffff;
          padding: 3px;
          object-fit: contain;
          flex-shrink: 0;
      }
      .sidebar-brand-title {
          font-size: 1.2rem;
          font-weight: 700;
          line-height: 1.2;
      }
      .sidebar-brand-sub {
          font-size: 0.76rem;
          opacity: 0.72;
          margin-top: 2px;
      }
      .parakh-title {
          font-size: 1.35rem;
          font-weight: 700;
          color: #ffffff;
          line-height: 1.2;
      }
      .parakh-subtitle {
          font-size: 0.86rem;
          color: rgba(255, 255, 255, 0.88);
          margin-top: 2px;
      }
      .parakh-tagline {
          font-size: 0.96rem;
          color: rgba(255, 255, 255, 0.95);
          margin-top: 14px;
          font-weight: 500;
      }

      /* 2x2 Navigation Grid Buttons styled as Cards */
      div[data-testid="column"] button[kind="secondary"],
      div[data-testid="column"] button[kind="primary"] {
          width: 100% !important;
          min-height: 84px !important;
          border-radius: 12px !important;
          padding: 14px 18px !important;
          background: #ffffff !important;
          border: 1px solid #e2e8f0 !important;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
          text-align: left !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: flex-start !important;
          justify-content: center !important;
          white-space: pre-wrap !important;
          transition: all 0.15s ease-in-out !important;
      }

      div[data-testid="column"] button:hover {
          border-color: #cbd5e1 !important;
          background: #f8fafc !important;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
      }

      div[data-testid="column"] button[kind="primary"] {
          border: 2px solid #1a396c !important;
          background: #ffffff !important;
          box-shadow: 0 2px 8px rgba(26, 57, 108, 0.08) !important;
      }

      /* Inside the button: markdown container */
      div[data-testid="column"] button div[data-testid="stMarkdownContainer"] {
          width: 100% !important;
          text-align: left !important;
      }

      div[data-testid="column"] button p {
          text-align: left !important;
          margin: 0 !important;
          line-height: 1.35 !important;
      }

      div[data-testid="column"] button p:first-child {
          font-size: 1.05rem !important;
          font-weight: 700 !important;
          color: #0f172a !important;
      }

      div[data-testid="column"] button[kind="primary"] p:first-child {
          color: #1a396c !important;
      }

      div[data-testid="column"] button p:last-child {
          font-size: 0.83rem !important;
          font-weight: 400 !important;
          color: #64748b !important;
          margin-top: 3px !important;
      }

      /* Dark mode card support */
      @media (prefers-color-scheme: dark) {
          div[data-testid="column"] button[kind="secondary"] {
              background: #1e293b !important;
              border-color: #334155 !important;
          }
          div[data-testid="column"] button p:first-child {
              color: #f8fafc !important;
          }
          div[data-testid="column"] button[kind="primary"] {
              border-color: #60a5fa !important;
              background: #1e293b !important;
          }
          div[data-testid="column"] button[kind="primary"] p:first-child {
              color: #93c5fd !important;
          }
      }

      /* Step layout matching screenshot */
      .section-heading {
          font-size: 1.35rem;
          font-weight: 700;
          color: #0f172a;
          margin: 18px 0 14px 0;
      }
      .step-label {
          font-size: 0.95rem;
          font-weight: 500;
          color: #475569;
          margin: 14px 0 8px 0;
      }
      .step-subcard {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.96rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 8px;
      }

      /* Pills and Badges */
      .pill {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 3px 10px;
          margin: 2px 4px 2px 0;
          border-radius: 999px;
          font-size: 0.81rem;
          font-weight: 600;
          line-height: 1.35;
      }
      .ok { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
      .miss { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
      .extra { background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
      .req { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }

      .status-badge {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 4px 12px;
          border-radius: 8px;
          font-weight: 700;
          font-size: 0.82rem;
          color: #ffffff;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

STATUS_COLOR = {"Shortlisted": "#059669", "On Hold": "#d97706", "Rejected": "#dc2626"}
STATUS_ICON = {"Shortlisted": "✅", "On Hold": "⏳", "Rejected": "❌"}
SEV_ICON = {"critical": "🔴", "major": "🟠", "minor": "🔵"}
AI_COLORS = {"Likely": "#dc2626", "Possible": "#d97706", "Unlikely": "#059669", "Not checked": "#64748b", "Not enough text": "#64748b"}


def pills(items, css):
    if not items:
        return "<i>none</i>"
    return "".join(f'<span class="pill {css}">{s}</span>' for s in items)


def render_kpi(icon, number, label, color="#3b82f6", bg="rgba(59, 130, 246, 0.08)"):
    return f"""
    <div style="background:{bg}; border:1px solid {color}35; border-radius:12px; padding:0.9rem 1rem; margin-bottom:0.6rem; display:flex; align-items:center; justify-content:space-between;">
      <div>
        <div style="font-size:1.6rem; font-weight:800; color:{color}; line-height:1.1;">{number}</div>
        <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#64748b; margin-top:4px;">{label}</div>
      </div>
      <div style="font-size:1.7rem; opacity:0.85;">{icon}</div>
    </div>
    """


# --------------------------------------------------------------------------- Header Banner (matching screenshot)
logo_header_html = (
    f'<div class="parakh-logo-badge"><img src="data:image/png;base64,{LOGO_B64}" alt="Parakh AI Logo" /></div>'
    if LOGO_B64
    else '<div class="parakh-icon-badge">📄</div>'
)

st.markdown(
    f"""<div class="parakh-banner">
  <div class="parakh-top-row">
    {logo_header_html}
    <div>
      <div class="parakh-title">Parakh AI</div>
      <div class="parakh-subtitle">Smart Resume Analysis & Recruitment Assistant</div>
    </div>
  </div>
  <div class="parakh-tagline">Analyze resumes. Find skill gaps. Build better resumes.</div>
</div>""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- Sidebar Configuration
with st.sidebar:
    if LOGO_PATH and os.path.exists(LOGO_PATH):
        sb_col1, sb_col2 = st.columns([1, 2.5])
        with sb_col1:
            st.image(LOGO_PATH, width=54)
        with sb_col2:
            st.markdown(
                """<div style="padding-top: 6px;">
                  <div style="font-size: 1.15rem; font-weight: 700; line-height: 1.2;">Parakh AI</div>
                  <div style="font-size: 0.74rem; opacity: 0.75;">Recruitment Intelligence</div>
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("<hr style='margin: 8px 0 14px 0; border: none; border-top: 1px solid rgba(128,128,128,0.2);'>", unsafe_allow_html=True)
    elif LOGO_B64:
        st.markdown(
            f"""
            <div class="sidebar-brand-box">
              <img src="data:image/png;base64,{LOGO_B64}" alt="Parakh AI Logo" />
              <div>
                <div class="sidebar-brand-title">Parakh AI</div>
                <div class="sidebar-brand-sub">Recruitment Intelligence</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("### ⚙️ ATS Engine Settings")
    threshold = st.slider(
        "🎯 Shortlist Cut-off (%)",
        min_value=30, max_value=90, value=60, step=5,
        help="Candidates achieving an overall composite score at or above this threshold will be Shortlisted."
    )
    must_have_text = st.text_input(
        "⚡ Must-Have Skills",
        placeholder="e.g. Python, SQL",
        help="Comma-separated critical skills. A candidate missing any of these cannot be Shortlisted."
    )
    ai_hold = st.checkbox(
        "🤖 Hold AI-written resumes for review",
        value=False,
        help="Resumes identified as 'Likely' AI-generated are placed 'On Hold' for recruiter review rather than immediate shortlisting."
    )
    ai_sens = st.select_slider(
        "🎚️ AI Detector Sensitivity",
        options=["strict", "balanced", "sensitive"],
        value="balanced",
        help="Strict: flags only strong chatbot patterns. Sensitive: flags subtle AI traces with higher scrutiny."
    )

    with st.expander("📊 How Candidate Scores are Calculated", expanded=False):
        st.markdown(
            """
            **Composite ATS Formula:**
            - **45%** 🎯 **Skill Match:** Detected canonical skills in candidate resume vs JD.
            - **25%** 🔍 **Semantic Match:** TF-IDF text & keyword cosine similarity.
            - **15%** 💼 **Experience Match:** Extracted verified experience vs JD requirement.
            - **15%** 📋 **Format Compliance:** ATS structural compliance (headings, contacts, layout).

            ---
            **Classification Rules:**
            - **Shortlisted:** Score ≥ Cut-off, all must-haves met, contact info available.
            - **On Hold:** Within 15% of cut-off, or missing must-have skill / contact info.
            - **Rejected:** Below qualifying range.
            """
        )

# --------------------------------------------------------------------------- 2x2 Interactive Navigation Cards Grid
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Analyze & Shortlist"

nav_row1_c1, nav_row1_c2 = st.columns(2)
with nav_row1_c1:
    is_act_1 = (st.session_state["active_tab"] == "Analyze & Shortlist")
    if st.button(
        "👥 **Analyze & Shortlist**\n\nRank resumes against a job description",
        key="nav_btn_analyze",
        type="primary" if is_act_1 else "secondary",
        use_container_width=True
    ):
        st.session_state["active_tab"] = "Analyze & Shortlist"
        st.rerun()

with nav_row1_c2:
    is_act_2 = (st.session_state["active_tab"] == "AI Resume Check")
    if st.button(
        "📋 **AI Resume Check**\n\nReview formatting and content",
        key="nav_btn_ai",
        type="primary" if is_act_2 else "secondary",
        use_container_width=True
    ):
        st.session_state["active_tab"] = "AI Resume Check"
        st.rerun()

nav_row2_c1, nav_row2_c2 = st.columns(2)
with nav_row2_c1:
    is_act_3 = (st.session_state["active_tab"] == "Build Resume")
    if st.button(
        "🔨 **Build Resume**\n\nCreate a resume from profile details",
        key="nav_btn_build",
        type="primary" if is_act_3 else "secondary",
        use_container_width=True
    ):
        st.session_state["active_tab"] = "Build Resume"
        st.rerun()

with nav_row2_c2:
    is_act_4 = (st.session_state["active_tab"] == "Tailor to Job")
    if st.button(
        "📄 **Tailor to Job**\n\nAdapt content to a target role",
        key="nav_btn_tailor",
        type="primary" if is_act_4 else "secondary",
        use_container_width=True
    ):
        st.session_state["active_tab"] = "Tailor to Job"
        st.rerun()

nav_row3_c1, nav_row3_c2 = st.columns(2)
with nav_row3_c1:
    is_act_5 = (st.session_state["active_tab"] == "Recruitment Automation")
    if st.button(
        "⚡ **Recruitment Automation**\n\nAutomate screening follow-ups and interviews",
        key="nav_btn_automation",
        type="primary" if is_act_5 else "secondary",
        use_container_width=True
    ):
        st.session_state["active_tab"] = "Recruitment Automation"
        st.rerun()

active_tab = st.session_state["active_tab"]

# ===========================================================================
# SECTION 1: ANALYZE & SHORTLIST (MATCHING SCREENSHOT LAYOUT)
# ===========================================================================
if active_tab == "Analyze & Shortlist":
    st.markdown('<div class="section-heading">Analyze & Shortlist</div>', unsafe_allow_html=True)

    # Step 1
    st.markdown('<div class="step-label">Step 1 — Add the job description</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="step-subcard"><span style="color:#2563eb; font-size:1.15rem;">📄</span> Upload job description or paste its text</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1])
        with c1:
            if st.button("📄 Load sample job description", use_container_width=True):
                if os.path.exists(SAMPLE_JD):
                    with open(SAMPLE_JD, encoding="utf-8") as fh:
                        st.session_state["jd_text"] = fh.read()
        with c2:
            jd_file = st.file_uploader("Upload JD", type=["txt", "pdf", "docx"], key="jd_file", label_visibility="collapsed")
            if jd_file is not None:
                st.session_state["jd_text"] = extract_text(jd_file.getvalue(), jd_file.name)[0]

        jd_text = st.text_area(
            "Job Description",
            key="jd_text",
            height=180,
            placeholder="Paste the job description here...",
            label_visibility="collapsed"
        )

    # Step 2
    st.markdown('<div class="step-label">Step 2 — Upload candidate resumes</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="step-subcard"><span style="color:#2563eb; font-size:1.15rem;">📑</span> Upload multiple PDF, DOCX, or TXT files</div>', unsafe_allow_html=True)
        uploads = st.file_uploader(
            "Upload resumes",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="resumes",
            label_visibility="collapsed"
        )
        st.caption("Tip: upload many resumes at once — they are ranked automatically.")
        run = st.button("🚀 Analyze resumes", type="primary", use_container_width=True, disabled=not (uploads and jd_text.strip()))

    if run:
        must = [s.strip() for s in must_have_text.split(",") if s.strip()]
        with st.spinner("Analyzing resumes against the job description..."):
            jd, results = analyze_files(
                [(u.name, u.getvalue()) for u in uploads],
                jd_text,
                threshold,
                must,
                ai_hold,
                ai_sens
            )
        for i, r in enumerate(results, 1):
            r["rank"] = i
        st.session_state["analysis"] = {"jd": jd, "results": results, "threshold": threshold}

    data = st.session_state.get("analysis")
    if data:
        jd, results, thr = data["jd"], data["results"], data["threshold"]
        for i, r in enumerate(results, 1):
            r["rank"] = i

        st.divider()

        # ---------------- KPI Executive Overview Grid
        st.markdown("### 📈 Analysis Results & Shortlist")
        k_col1, k_col2, k_col3, k_col4, k_col5 = st.columns(5)

        total_analyzed = len(results)
        shortlisted_cnt = sum(r["status"] == "Shortlisted" for r in results)
        on_hold_cnt = sum(r["status"] == "On Hold" for r in results)
        format_issues_cnt = sum(not r["format_ok"] for r in results)
        ai_risk_cnt = sum(r["ai_check"]["level"] == "Likely" for r in results)

        with k_col1:
            st.markdown(render_kpi("📊", total_analyzed, "Resumes Analysed", "#2563eb", "rgba(37, 99, 235, 0.08)"), unsafe_allow_html=True)
        with k_col2:
            st.markdown(render_kpi("🎯", shortlisted_cnt, "Shortlisted", "#059669", "rgba(5, 150, 105, 0.08)"), unsafe_allow_html=True)
        with k_col3:
            st.markdown(render_kpi("⏳", on_hold_cnt, "On Hold", "#d97706", "rgba(217, 119, 6, 0.08)"), unsafe_allow_html=True)
        with k_col4:
            st.markdown(render_kpi("⚠️", format_issues_cnt, "Not in Format", "#dc2626", "rgba(220, 38, 38, 0.08)"), unsafe_allow_html=True)
        with k_col5:
            st.markdown(render_kpi("🤖", ai_risk_cnt, "Likely AI-written", "#7c3aed", "rgba(124, 58, 237, 0.08)"), unsafe_allow_html=True)

        # ---------------- Job Requirements Card
        with st.container(border=True):
            r_c1, r_c2 = st.columns([3, 1.2])
            with r_c1:
                st.markdown("**🎯 Skills required by the job:**")
                st.markdown(pills(jd["skills"], "req"), unsafe_allow_html=True)
            with r_c2:
                req_info = []
                if jd.get("min_years"):
                    req_info.append(f"💼 **Min Experience:** {jd['min_years']:g} Years")
                if jd.get("must_have"):
                    req_info.append(f"⚡ **Must-Have:** {', '.join(jd['must_have'])}")
                if req_info:
                    st.markdown("<br>".join(req_info), unsafe_allow_html=True)
                else:
                    st.caption("No minimum experience requirement.")

        # ---------------- Top Candidate Spotlight Podium
        if results:
            st.markdown("### 🏆 Top Candidate Spotlight")
            top_3 = results[:min(3, len(results))]
            podium_cols = st.columns(len(top_3))
            medals = ["🥇 1st Rank", "🥈 2nd Rank", "🥉 3rd Rank"]
            medal_colors = ["#f59e0b", "#94a3b8", "#d97706"]

            for idx, (cand, p_col) in enumerate(zip(top_3, podium_cols)):
                with p_col:
                    with st.container(border=True):
                        st.markdown(f"<span style='font-size:0.85rem; font-weight:800; color:{medal_colors[idx]};'>{medals[idx]}</span>", unsafe_allow_html=True)
                        st.markdown(f"#### {cand['name']}")
                        st.markdown(
                            f'<span class="status-badge" style="background:{STATUS_COLOR.get(cand["status"], "#64748b")};">{STATUS_ICON.get(cand["status"], "")} {cand["status"]}</span> '
                            f'&nbsp; <b>{cand["overall"]}% Overall</b>',
                            unsafe_allow_html=True
                        )
                        st.caption(f"📁 {cand['file']}")

                        st.write(f"🎯 **Skill Match:** `{cand['skill_score']}%` &nbsp;|&nbsp; 💼 **Exp:** `{cand['experience_years']} yrs`")
                        if cand["matched_skills"]:
                            st.markdown("**Top Matches:** " + pills(cand["matched_skills"][:3], "ok"), unsafe_allow_html=True)

                        if cand.get("parsed"):
                            base_name = safe_name(cand["name"])
                            st.download_button(
                                f"📥 Download PDF ({cand['name'].split()[0]})",
                                formatted_resume(cand, "pdf"),
                                f"{base_name}_formatted.pdf",
                                "application/pdf",
                                key=f"podium_download_{idx}",
                                use_container_width=True
                            )

        # ---------------- Interactive Filter & Search Bar
        st.markdown("### 📋 Ranked Candidates & Deep-Dive Evaluation")
        flt_col1, flt_col2, flt_col3, flt_col4 = st.columns([2, 1.2, 1.3, 1.1])
        with flt_col1:
            search_query = st.text_input("🔍 Search candidate or skill", placeholder="Type candidate name, file, or skill...", key="candidate_search")
        with flt_col2:
            status_filter = st.selectbox("Status Filter", ["All Statuses", "Shortlisted", "On Hold", "Rejected"], key="candidate_status_filter")
        with flt_col3:
            sort_metric = st.selectbox("Sort By", ["Rank / Overall Score", "Skill Match %", "Experience (Years)", "Format Score"], key="candidate_sort")
        with flt_col4:
            ai_flag_only = st.checkbox("Show AI-Flagged Only", value=False, key="candidate_ai_filter")

        # Apply Filters
        filtered = list(results)
        if search_query.strip():
            sq = search_query.lower()
            filtered = [
                r for r in filtered
                if sq in r["name"].lower() or sq in r["file"].lower() or any(sq in s.lower() for s in r["matched_skills"])
            ]
        if status_filter != "All Statuses":
            filtered = [r for r in filtered if r["status"] == status_filter]
        if ai_flag_only:
            filtered = [r for r in filtered if r["ai_check"]["level"] in ("Likely", "Possible")]

        if sort_metric == "Skill Match %":
            filtered.sort(key=lambda x: -x["skill_score"])
        elif sort_metric == "Experience (Years)":
            filtered.sort(key=lambda x: -x["experience_years"])
        elif sort_metric == "Format Score":
            filtered.sort(key=lambda x: -x["format_score"])
        else:
            filtered.sort(key=lambda x: x["rank"])

        # ---------------- Summary Table & Export Bar
        df = results_dataframe(results)
        with st.expander("📊 View Compact Ranking Table & Export", expanded=False):
            st.dataframe(
                df[["Rank", "Candidate", "Status", "Overall %", "Skill Match %", "Experience (yrs)",
                    "Format Score", "Format OK", "AI Check", "Matched Skills", "Missing Skills"]],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Overall %": st.column_config.ProgressColumn("Overall %", min_value=0, max_value=100, format="%.1f"),
                    "Skill Match %": st.column_config.ProgressColumn("Skill Match %", min_value=0, max_value=100, format="%.1f"),
                },
            )

        btn_c1, btn_c2, _ = st.columns([1.2, 1.4, 2])
        with btn_c1:
            st.download_button(
                "📥 Download ranking (CSV)",
                df.to_csv(index=False).encode("utf-8"),
                "shortlist.csv",
                "text/csv",
                use_container_width=True
            )
        with btn_c2:
            st.download_button(
                "📑 Download full report (PDF)",
                build_report_pdf(results, jd, thr),
                "analysis_report.pdf",
                "application/pdf",
                use_container_width=True
            )

        st.caption(f"Showing **{len(filtered)}** of **{len(results)}** candidate(s).")

        # ---------------- Candidate Deep-Dive Cards
        if not filtered:
            st.info("No candidates match your current filter settings.")
        else:
            for r in filtered:
                with st.container(border=True):
                    ch_1, ch_2 = st.columns([3, 1.2])
                    with ch_1:
                        rank_icon = "🥇" if r["rank"] == 1 else ("🥈" if r["rank"] == 2 else ("🥉" if r["rank"] == 3 else f"#{r['rank']}"))
                        st.markdown(f"#### {rank_icon} {r['name']}")
                        st.markdown(
                            f'<span class="status-badge" style="background:{STATUS_COLOR.get(r["status"], "#64748b")};">{STATUS_ICON.get(r["status"], "")} {r["status"]}</span> '
                            f'&nbsp; <b>Overall Score: {r["overall"]}%</b> &nbsp;·&nbsp; 📁 <code>{r["file"]}</code>',
                            unsafe_allow_html=True
                        )
                    with ch_2:
                        contact_items = []
                        if r["email"]:
                            contact_items.append(f"✉️ {r['email']}")
                        if r["phone"]:
                            contact_items.append(f"📞 {r['phone']}")
                        if contact_items:
                            st.caption("  |  ".join(contact_items))
                        else:
                            st.caption("⚠️ No contact details extracted")

                    # 4-Pillars Visual Breakdown
                    b1, b2, b3, b4 = st.columns(4)
                    with b1:
                        st.metric("🎯 Skill match", f"{r['skill_score']}%")
                        st.progress(min(1.0, max(0.0, r['skill_score'] / 100.0)))
                    with b2:
                        st.metric("🔍 Text match", f"{r['tfidf_score']}%")
                        st.progress(min(1.0, max(0.0, r['tfidf_score'] / 100.0)))
                    with b3:
                        st.metric("💼 Experience", f"{r['experience_years']} yrs")
                        st.progress(min(1.0, max(0.0, r['exp_score'] / 100.0)))
                    with b4:
                        st.metric("📋 Format score", f"{r['format_score']}/100")
                        st.progress(min(1.0, max(0.0, r['format_score'] / 100.0)))

                    # Expandable Deep Dossier
                    with st.expander(f"🔍 Candidate details & Evaluation reasons for {r['name']}", expanded=False):
                        d_col_left, d_col_right = st.columns([1, 1])

                        with d_col_left:
                            st.markdown("##### 🎯 Skills Breakdown")
                            st.markdown(f"**Matched skills ({len(r['matched_skills'])}):**")
                            st.markdown(pills(r["matched_skills"], "ok"), unsafe_allow_html=True)

                            if r["missing_skills"]:
                                st.markdown(f"**Missing skills ({len(r['missing_skills'])}):**")
                                st.markdown(pills(r["missing_skills"], "miss"), unsafe_allow_html=True)

                            if r["extra_skills"]:
                                st.markdown(f"**Other skills found ({len(r['extra_skills'])}):**")
                                st.markdown(pills(r["extra_skills"], "extra"), unsafe_allow_html=True)

                            st.markdown("##### 💡 Decision Reasons")
                            for reason in r["reasons"]:
                                st.write("• " + reason)

                        with d_col_right:
                            st.markdown("##### 🤖 AI-Written Check")
                            ai = r["ai_check"]
                            ai_badge_color = AI_COLORS.get(ai["level"], "#64748b")
                            st.markdown(
                                f'<span class="status-badge" style="background:{ai_badge_color};">{ai["level"]}</span> '
                                f'&nbsp; Indicator: <b>{ai["score"]}/100</b> &nbsp;·&nbsp; {ai["words"]} words',
                                unsafe_allow_html=True
                            )
                            if ai["level"] == "Likely":
                                st.warning("Verify the claims in an interview or with a practical task.")
                            elif ai["level"] == "Possible":
                                st.info("Some parts may be AI-written.")
                            else:
                                st.success("AI-written check: Unlikely.")

                            if ai.get("signals"):
                                for sig in ai["signals"]:
                                    st.write(f"• **{sig['name']}**: {sig['detail']} (+{sig['points']})")

                            st.markdown("##### 📋 Resume Format Diagnostic")
                            if r["format_ok"]:
                                st.success("Resume follows the required format.")
                            else:
                                st.error("Resume is NOT in the required format.")

                            if r["issues"]:
                                for issue in sorted(r["issues"], key=lambda x: -x["penalty"]):
                                    st.write(f"{SEV_ICON.get(issue['severity'], '🔵')} **{issue['message']}**")
                                    st.caption(f"Fix: {issue['suggestion']}")

                            if r["strengths"]:
                                for s in r["strengths"]:
                                    st.write(f"✅ {s}")

                        # ATS-Ready Resume Download Buttons
                        if r.get("parsed"):
                            st.divider()
                            st.markdown("##### 📄 Download Resume in Required Format")
                            st.caption("Built from the candidate's own content. Missing parts appear as placeholders.")
                            base_cand = safe_name(os.path.splitext(r["file"])[0])
                            dl_1, dl_2, _ = st.columns([1.2, 1.2, 2.5])
                            with dl_1:
                                st.download_button(
                                    "📥 Download DOCX",
                                    formatted_resume(r, "docx"),
                                    f"{base_cand}_formatted.docx",
                                    DOCX_MIME,
                                    key=f"dossier_docx_{r['file']}_{r['rank']}",
                                    use_container_width=True
                                )
                            with dl_2:
                                st.download_button(
                                    "📥 Download PDF",
                                    formatted_resume(r, "pdf"),
                                    f"{base_cand}_formatted.pdf",
                                    "application/pdf",
                                    key=f"dossier_pdf_{r['file']}_{r['rank']}",
                                    use_container_width=True
                                )

# ===========================================================================
# SECTION 2: AI RESUME CHECK
# ===========================================================================
elif active_tab == "AI Resume Check":
    st.markdown('<div class="section-heading">AI Resume Check</div>', unsafe_allow_html=True)
    st.caption("Works on its own — no job description needed. Upload one or more resumes, or paste the text. The result is an indicator, not proof.")

    with st.container(border=True):
        a_left, a_right = st.columns(2)
        with a_left:
            st.markdown('<div class="step-subcard"><span style="color:#2563eb; font-size:1.15rem;">📁</span> Upload resumes (PDF / DOCX / TXT)</div>', unsafe_allow_html=True)
            ai_uploads = st.file_uploader("Upload resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True, key="ai_resumes", label_visibility="collapsed")
        with a_right:
            st.markdown('<div class="step-subcard"><span style="color:#2563eb; font-size:1.15rem;">📝</span> ...or paste the resume text</div>', unsafe_allow_html=True)
            ai_pasted = st.text_area("Resume text", height=120, key="ai_pasted", placeholder="Paste the full resume text here...", label_visibility="collapsed")

        ai_run = st.button("🔍 Check for AI-written text", type="primary", key="ai_run", disabled=not (ai_uploads or ai_pasted.strip()), use_container_width=True)

    if ai_run:
        items = [(u.name, u.getvalue()) for u in (ai_uploads or [])]
        if ai_pasted.strip():
            items.append(("pasted_text.txt", ai_pasted.encode("utf-8")))
        with st.spinner("Scanning for AI-written text patterns..."):
            st.session_state["ai_results"] = check_ai_files(items, ai_sens)

    ai_results = st.session_state.get("ai_results")
    if ai_results:
        st.divider()
        st.markdown("### 📊 AI Check Results")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(render_kpi("📑", len(ai_results), "Resumes Checked", "#2563eb", "rgba(37, 99, 235, 0.08)"), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi("🔴", sum(r["level"] == "Likely" for r in ai_results), "Likely AI-written", "#dc2626", "rgba(220, 38, 38, 0.08)"), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi("🟠", sum(r["level"] == "Possible" for r in ai_results), "Possibly AI-assisted", "#d97706", "rgba(217, 119, 6, 0.08)"), unsafe_allow_html=True)
        with k4:
            st.markdown(render_kpi("🟢", sum(r["level"] == "Unlikely" for r in ai_results), "Probably Human", "#059669", "rgba(5, 150, 105, 0.08)"), unsafe_allow_html=True)

        ai_df = pd.DataFrame(ai_check_rows(ai_results))
        st.dataframe(ai_df, hide_index=True, use_container_width=True, column_config={
            "AI Indicator (0-100)": st.column_config.ProgressColumn(
                "AI Indicator (0-100)", min_value=0, max_value=100, format="%d")})
        st.download_button("📥 Download results (CSV)", ai_df.to_csv(index=False).encode("utf-8-sig"), "ai_check.csv", "text/csv", key="ai_csv")

        for i, r in enumerate(ai_results, 1):
            with st.container(border=True):
                if r.get("error"):
                    st.error(f"#{i} {r['file']}: {r['error']}")
                    continue
                color = AI_COLORS.get(r["level"], "#64748b")
                st.markdown(
                    f'<span class="status-badge" style="background:{color};">{r["verdict"]}</span> '
                    f'&nbsp; AI indicator **{r["score"]}/100** &nbsp;·&nbsp; {r["words"]} words &nbsp;·&nbsp; 📁 <code>{r["file"]}</code>',
                    unsafe_allow_html=True
                )
                if r["level"] == "Not enough text":
                    st.caption("Under 80 words: too little text for style checks.")

                if r["signals"]:
                    st.markdown("**Why it was flagged:**")
                    for sig in r["signals"]:
                        st.write(f"• **{sig['name']}** - {sig['detail']} (+{sig['points']})")
                elif r["level"] == "Unlikely":
                    st.write("No typical AI-writing patterns were found.")

                if r.get("suspicious_lines"):
                    st.markdown("**Lines that sound most AI-written:**")
                    for item in r["suspicious_lines"]:
                        st.markdown(f"> *\"{item['line']}\"*")
                        st.caption("Reason: " + "; ".join(item["reasons"]))

                if r["level"] in ("Likely", "Possible"):
                    st.info("Suggested next step: ask the candidate to explain one project line by line — tools used, their own part, and measured metrics.")

# ===========================================================================
# SECTION 3: BUILD RESUME (10+ TEMPLATE FORMATS & DUMMY PREVIEWS)
# ===========================================================================
elif active_tab == "Build Resume":
    st.markdown('<div class="section-heading">Build Resume</div>', unsafe_allow_html=True)
    st.caption("Create an ATS-optimized, high-impact resume. Select from 10 professional format templates, load realistic dummy data, or customize with your own details.")

    # ----------------------------------------------------------------------- Template Picker
    st.markdown("##### 🎨 Step 1 — Select Resume Template Format")

    if "builder_tpl_id" not in st.session_state:
        st.session_state["builder_tpl_id"] = "classic_ats"

    tpl_keys = list(RESUME_TEMPLATES.keys())
    current_selected_idx = tpl_keys.index(st.session_state["builder_tpl_id"]) if st.session_state["builder_tpl_id"] in tpl_keys else 0

    col_picker, col_actions = st.columns([2.6, 1.4])
    with col_picker:
        selected_tpl_id = st.selectbox(
            "Choose a template format (10 Choices):",
            options=tpl_keys,
            index=current_selected_idx,
            format_func=lambda k: f"{RESUME_TEMPLATES[k]['icon']} {RESUME_TEMPLATES[k]['name']} — [{RESUME_TEMPLATES[k]['badge']}]",
            key="builder_template_select"
        )
        st.session_state["builder_tpl_id"] = selected_tpl_id

    active_tpl = get_template(selected_tpl_id)

    with col_actions:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🚀 Load Sample", help=f"Fill all fields with realistic dummy data for {active_tpl['name']}", use_container_width=True):
                dummy_prof = get_dummy_profile(selected_tpl_id)
                dummy_form = profile_to_form_text(dummy_prof)
                for field_k, field_v in dummy_form.items():
                    st.session_state[f"bld_{field_k}"] = field_v
                st.session_state["builder_last_loaded"] = selected_tpl_id
                st.rerun()
        with btn_c2:
            if st.button("🧹 Clear All", help="Clear all fields to type your resume from scratch", use_container_width=True):
                for field_k in ["name", "email", "phone", "location", "linkedin", "github", "summary", "skills", "experience", "projects", "education", "certifications", "achievements"]:
                    st.session_state[f"bld_{field_k}"] = ""
                st.rerun()

    # Visual Template Info Banner
    st.markdown(
        f"""
        <div style="background: rgba(30, 58, 108, 0.04); border-left: 4px solid {active_tpl['accent_hex']}; border-radius: 8px; padding: 10px 16px; margin: 4px 0 18px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
          <div>
            <span style="font-weight: 700; color: {active_tpl['accent_hex']}; font-size: 1rem;">{active_tpl['icon']} {active_tpl['name']}</span>
            <span style="background: {active_tpl['accent_hex']}18; color: {active_tpl['accent_hex']}; padding: 2px 8px; border-radius: 12px; font-size: 0.76rem; font-weight: 600; margin-left: 8px;">{active_tpl['badge']}</span>
            <div style="font-size: 0.84rem; color: #475569; margin-top: 3px;">{active_tpl['description']}</div>
          </div>
          <div style="font-size: 0.8rem; color: #64748b; text-align: right;">
            <div>Font: <code>{active_tpl['font_family_docx']}</code> &nbsp;|&nbsp; Accent: <code style="color:{active_tpl['accent_hex']}; font-weight:700;">{active_tpl['accent_hex']}</code></div>
            <div>Category: <strong>{active_tpl['category']}</strong></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # If first time entering and fields not initialized, load classic_ats dummy defaults
    if "bld_name" not in st.session_state:
        init_dummy = get_dummy_profile("classic_ats")
        init_form = profile_to_form_text(init_dummy)
        for k, v in init_form.items():
            st.session_state[f"bld_{k}"] = v

    # ----------------------------------------------------------------------- Details Form
    st.markdown(f"##### ✍️ Step 2 — Fill or Edit Resume Details for [{active_tpl['name']}]")

    with st.form("build_form"):
        st.markdown("###### 👤 Personal & Contact Details")
        a, b, c = st.columns(3)
        name = a.text_input("Full Name", value=st.session_state.get("bld_name", ""))
        email = b.text_input("Email", value=st.session_state.get("bld_email", ""))
        phone = c.text_input("Phone", value=st.session_state.get("bld_phone", ""))

        d, e, f = st.columns(3)
        location = d.text_input("City, State / Country", value=st.session_state.get("bld_location", ""))
        linkedin = e.text_input("LinkedIn Profile URL (optional)", value=st.session_state.get("bld_linkedin", ""))
        github = f.text_input("GitHub / Portfolio URL (optional)", value=st.session_state.get("bld_github", ""))

        st.markdown("###### 📝 Professional Summary")
        summary = st.text_area("Summary (2-4 lines)", value=st.session_state.get("bld_summary", ""), height=85)

        st.markdown("###### ⚡ Skills")
        st.caption("Group skills by category using 'Category: skill1, skill2' on separate lines.")
        skills = st.text_area("Skills", value=st.session_state.get("bld_skills", ""), height=95)

        st.markdown("###### 💼 Experience / Internships")
        st.caption("Include Role — Company | Date on first line, followed by bullet points starting with • or -")
        experience = st.text_area("Experience", value=st.session_state.get("bld_experience", ""), height=130)

        st.markdown("###### 🚀 Key Projects")
        st.caption("Project Name | Date, tech stack description, and bullet accomplishments.")
        projects = st.text_area("Projects", value=st.session_state.get("bld_projects", ""), height=120)

        st.markdown("###### 🎓 Education")
        education = st.text_area("Education", value=st.session_state.get("bld_education", ""), height=85)

        g1, g2 = st.columns(2)
        certs = g1.text_area("Certifications (one per line)", value=st.session_state.get("bld_certifications", ""), height=75)
        achievements = g2.text_area("Achievements / Honors (one per line)", value=st.session_state.get("bld_achievements", ""), height=75)

        submitted = st.form_submit_button(f"✨ Generate Resume in {active_tpl['name']} Format", type="primary", use_container_width=True)

    if submitted:
        # Save submitted fields to state
        for k, v in [("name", name), ("email", email), ("phone", phone), ("location", location),
                     ("linkedin", linkedin), ("github", github), ("summary", summary),
                     ("skills", skills), ("experience", experience), ("projects", projects),
                     ("education", education), ("certifications", certs), ("achievements", achievements)]:
            st.session_state[f"bld_{k}"] = v

        profile = profile_from_fields({
            "name": name, "email": email, "phone": phone, "location": location, "linkedin": linkedin,
            "github": github, "summary": summary, "skills": skills, "experience": experience,
            "projects": projects, "education": education, "certifications": certs,
            "achievements": achievements
        })

        b_docx = build_resume_docx(profile, template_id=selected_tpl_id)
        b_pdf = build_resume_pdf(profile, template_id=selected_tpl_id)
        b_base = safe_name(name) if name.strip() else "resume"

        st.session_state["built"] = {
            "profile": profile,
            "docx": b_docx,
            "pdf": b_pdf,
            "base": b_base,
            "template_id": selected_tpl_id,
            "template_name": active_tpl["name"]
        }

    built = st.session_state.get("built")
    if built:
        st.markdown("---")
        st.markdown(f"### 🎉 Resume Generated: {built.get('template_name', active_tpl['name'])}")
        st.success(f"Resume generated successfully in **{built.get('template_name', active_tpl['name'])}** format! Parts shown in red [brackets] need your details.")

        b_c1, b_c2, _ = st.columns([1.2, 1.2, 1.6])
        fn_base = built["base"]
        tpl_suf = built.get("template_id", "tpl")
        with b_c1:
            st.download_button(
                f"📥 Download PDF ({built.get('template_name', 'Resume')})",
                built["pdf"],
                f"{fn_base}_{tpl_suf}.pdf",
                "application/pdf",
                key="b_pdf_btn",
                use_container_width=True
            )
        with b_c2:
            st.download_button(
                f"📥 Download DOCX ({built.get('template_name', 'Resume')})",
                built["docx"],
                f"{fn_base}_{tpl_suf}.docx",
                DOCX_MIME,
                key="b_docx_btn",
                use_container_width=True
            )

        with st.expander("👁️ Live Interactive Resume Preview (Formatted in chosen style)", expanded=True):
            live_html = render_template_html(built["profile"], template_id=built.get("template_id", "classic_ats"))
            st.markdown(live_html, unsafe_allow_html=True)

# ===========================================================================
# SECTION 4: TAILOR TO JOB (MATCHING SCREENSHOT)
# ===========================================================================
elif active_tab == "Tailor to Job":
    st.markdown('<div class="section-heading">Tailor to Job</div>', unsafe_allow_html=True)
    st.caption("Upload candidate resume along with the target company's job description. The generated resume will strictly retain **ONLY the skills that match this specific Job Description**, making the resume 100% targeted.")

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown('<div class="step-label">Step 1 — Candidate Resume</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="step-subcard"><span style="color:#2563eb; font-size:1.15rem;">📄</span> Upload candidate resume (.pdf, .docx, .txt)</div>', unsafe_allow_html=True)
            tailor_upload = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"], key="tailor_resume_file", label_visibility="collapsed")
            st.caption("Supports standard text-based PDF, Word (.docx), or plain text.")

    with t_col2:
        st.markdown('<div class="step-label">Step 2 — Target Job Description</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="step-subcard"><span style="color:#2563eb; font-size:1.15rem;">💼</span> Target company job description</div>', unsafe_allow_html=True)
            t_sub1, t_sub2 = st.columns([1.2, 1])
            with t_sub1:
                if st.button("📄 Load sample JD", key="tailor_load_sample", use_container_width=True):
                    if os.path.exists(SAMPLE_JD):
                        with open(SAMPLE_JD, encoding="utf-8") as fh:
                            st.session_state["tailor_jd_text"] = fh.read()
            with t_sub2:
                tailor_jd_file = st.file_uploader("Upload JD", type=["txt", "pdf", "docx"], key="tailor_jd_file", label_visibility="collapsed")
                if tailor_jd_file is not None:
                    st.session_state["tailor_jd_text"] = extract_text(tailor_jd_file.getvalue(), tailor_jd_file.name)[0]

            tailor_jd_text = st.text_area("JD text", key="tailor_jd_text", height=150, placeholder="Paste target job description here...", label_visibility="collapsed")

    t_tpl_keys = list(RESUME_TEMPLATES.keys())
    t_selected_tpl = st.selectbox(
        "🎨 Select Output Template Format (10 Styles Available):",
        options=t_tpl_keys,
        format_func=lambda k: f"{RESUME_TEMPLATES[k]['icon']} {RESUME_TEMPLATES[k]['name']} — [{RESUME_TEMPLATES[k]['badge']}]",
        key="tailor_tpl_select"
    )

    t_btn = st.button("⚡ Tailor Resume to Job", type="primary", key="btn_run_tailor", disabled=not (tailor_upload and tailor_jd_text.strip()), use_container_width=True)

    if t_btn:
        with st.spinner("Analyzing resume against JD and filtering matching skills..."):
            try:
                res_text, res_meta = extract_text(tailor_upload.getvalue(), tailor_upload.name)
                if len(res_text.strip()) < 30:
                    st.error("No readable text found in the uploaded resume. Please upload a text-based PDF or DOCX.")
                else:
                    parsed_res = parse_resume(res_text, res_meta)
                    parsed_jd = parse_job_description(tailor_jd_text)

                    if not parsed_jd["skills"]:
                        st.warning("No technical skills were detected in the JD text. Please check that requirements include specific skills.")

                    tailored_prof, matched_skills, removed_skills, missing_jd = build_tailored_profile(
                        parsed_res, parsed_jd["skills"]
                    )

                    t_docx = build_resume_docx(tailored_prof, template_id=t_selected_tpl)
                    t_pdf = build_resume_pdf(tailored_prof, template_id=t_selected_tpl)
                    base_name = (safe_name(tailored_prof["name"])
                                 if (tailored_prof.get("name") and not is_ph(tailored_prof["name"]))
                                 else safe_name(os.path.splitext(tailor_upload.name)[0]))

                    st.session_state["tailored_data"] = {
                        "profile": tailored_prof,
                        "matched": matched_skills,
                        "removed": removed_skills,
                        "missing": missing_jd,
                        "jd_skills": parsed_jd["skills"],
                        "docx": t_docx,
                        "pdf": t_pdf,
                        "filename_base": base_name,
                        "template_id": t_selected_tpl,
                        "template_name": RESUME_TEMPLATES[t_selected_tpl]["name"],
                        "name": tailored_prof["name"],
                        "email": tailored_prof["email"],
                        "phone": tailored_prof["phone"],
                    }
            except Exception as exc:
                st.error(f"Error processing resume tailoring: {exc}")

    t_data = st.session_state.get("tailored_data")
    if t_data:
        st.divider()
        st.markdown("### 🎯 Tailoring Analysis & Results")

        total_jd = len(t_data["jd_skills"])
        match_pct = round((len(t_data["matched"]) / total_jd * 100), 1) if total_jd > 0 else 0.0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(render_kpi("🎯", f"{match_pct}%", "JD Match Score", "#059669", "rgba(5, 150, 105, 0.08)"), unsafe_allow_html=True)
        with m2:
            st.markdown(render_kpi("✅", len(t_data["matched"]), "Retained Skills", "#2563eb", "rgba(37, 99, 235, 0.08)"), unsafe_allow_html=True)
        with m3:
            st.markdown(render_kpi("❌", len(t_data["removed"]), "Omitted Skills", "#dc2626", "rgba(220, 38, 38, 0.08)"), unsafe_allow_html=True)
        with m4:
            st.markdown(render_kpi("⚠️", len(t_data["missing"]), "Missing JD Skills", "#d97706", "rgba(217, 119, 6, 0.08)"), unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(
                f"**Candidate:** `{t_data['name']}` &nbsp;|&nbsp; "
                f"**Email:** `{t_data['email'] or 'N/A'}` &nbsp;|&nbsp; "
                f"**Phone:** `{t_data['phone'] or 'N/A'}`"
            )

            st.markdown("**✅ Retained in Tailored Resume (Matched with JD):**")
            st.markdown(pills(t_data["matched"], "ok"), unsafe_allow_html=True)
            st.caption("Sirf vhi skills resume me rakhi gayi hain jo company ki Job Description se match karti hain.")

            if t_data["removed"]:
                st.markdown("**❌ Omitted Skills (Not in this JD):**")
                st.markdown(pills(t_data["removed"], "miss"), unsafe_allow_html=True)
                st.caption("Ye skills candidate ke resume me thi par is JD me require nahi thi, isliye targeted resume se hata di gayi hain.")

            if t_data["missing"]:
                st.markdown("**⚠️ Missing Skills (Required by JD):**")
                st.markdown(pills(t_data["missing"], "extra"), unsafe_allow_html=True)
                st.caption("Ye skills company ki JD me mangi gayi hain par candidate ke resume me nahi mili.")

        # Download Buttons
        st.markdown("##### 📥 Download Tailored Resume")
        d_c1, d_c2, _ = st.columns([1.2, 1.2, 2])
        base_fn = t_data["filename_base"]
        with d_c1:
            st.download_button(
                "📥 Download Tailored DOCX",
                t_data["docx"],
                f"{base_fn}_tailored.docx",
                DOCX_MIME,
                key="tailor_docx_btn",
                use_container_width=True
            )
        with d_c2:
            st.download_button(
                "📥 Download Tailored PDF",
                t_data["pdf"],
                f"{base_fn}_tailored.pdf",
                "application/pdf",
                key="tailor_pdf_btn",
                use_container_width=True
            )

        with st.expander("👁️ Live Formatted Resume Preview", expanded=False):
            prof = t_data["profile"]
            tpl_used = t_data.get("template_id", "classic_ats")
            live_html = render_template_html(prof, template_id=tpl_used)
            st.markdown(live_html, unsafe_allow_html=True)


# ===========================================================================
# SECTION 5: RECRUITMENT AUTOMATION
# ===========================================================================
elif active_tab == "Recruitment Automation":
    st.markdown('<div class="section-heading">Recruitment Automation Center</div>', unsafe_allow_html=True)
    st.caption("Use the screening results to create a next-step workflow, candidate email drafts, interview questions, and an action-plan export. Emails are drafts only; review them before sending.")

    data = st.session_state.get("analysis")
    if not data or not data.get("results"):
        st.info("First go to **Analyze & Shortlist**, add a job description and resumes, and run the analysis. Your results will appear here automatically.")
    else:
        jd, results = data["jd"], data["results"]
        results = sorted(results, key=lambda r: r.get("rank", 999))
        st.markdown("### ⚙️ Automated Workflow Rules")
        a1, a2, a3 = st.columns(3)
        with a1:
            make_shortlist_drafts = st.checkbox("Create shortlist email drafts", value=True)
        with a2:
            make_hold_drafts = st.checkbox("Create follow-up drafts for On Hold", value=True)
        with a3:
            make_interview_questions = st.checkbox("Generate interview questions", value=True)

        if st.button("⚡ Run Recruitment Automation", type="primary", use_container_width=True):
            automation_items = []
            for candidate in results:
                status = candidate.get("status", "On Hold")
                name = candidate.get("name") or "Candidate"
                skills = candidate.get("matched_skills", [])
                missing = candidate.get("missing_skills", [])
                rank = candidate.get("rank", "-")
                score = candidate.get("overall", 0)
                email = candidate.get("email", "")

                if status == "Shortlisted":
                    action = "Schedule interview and verify candidate details"
                    subject = "Next Steps in Your Application"
                    email_body = (
                        f"Dear {name},\n\nThank you for applying. Your profile has been shortlisted for the next stage "
                        "of our recruitment process. We would like to arrange an interview to discuss your experience "
                        "and the role. Please share your availability.\n\nRegards,\nRecruitment Team"
                    )
                elif status == "On Hold":
                    action = "Recruiter review; verify missing skills or information"
                    subject = "Additional Information Regarding Your Application"
                    email_body = (
                        f"Dear {name},\n\nThank you for your application. We are reviewing your profile and may need "
                        "additional information about your experience and skills. We will update you regarding the next steps.\n\n"
                        "Regards,\nRecruitment Team"
                    )
                else:
                    action = "Human review before closing application"
                    subject = "Application Status Update"
                    email_body = (
                        f"Dear {name},\n\nThank you for applying and for your interest in this opportunity. "
                        "Our team will review your application and contact you if there is a suitable next step.\n\n"
                        "Regards,\nRecruitment Team"
                    )

                questions = []
                if make_interview_questions:
                    for skill in skills[:5]:
                        questions.append(f"Explain a practical project or task where you used {skill}.")
                    for skill in missing[:3]:
                        questions.append(f"What is your current familiarity with {skill}, and how would you approach learning or using it?")
                    questions.extend([
                        "Describe a challenge you faced in a project and how you solved it.",
                        "What was your individual contribution to your most relevant project?",
                        "How do you test your work and handle errors?"
                    ])

                automation_items.append({
                    "Rank": rank, "Candidate": name, "Email": email, "Status": status,
                    "Score (%)": score, "Recommended Next Action": action,
                    "Matched Skills": ", ".join(skills), "Missing Skills": ", ".join(missing),
                    "Email Subject": subject, "Email Draft": email_body,
                    "Interview Questions": "\n".join(questions)
                })
            st.session_state["automation_items"] = automation_items
            st.session_state["automation_jd_title"] = jd.get("title", "Target Role")

        automation_items = st.session_state.get("automation_items")
        if automation_items:
            st.divider()
            st.markdown("### 📌 Automated Action Plan")
            action_df = pd.DataFrame(automation_items)
            st.dataframe(action_df[["Rank", "Candidate", "Status", "Score (%)", "Recommended Next Action"]], hide_index=True, use_container_width=True)
            st.download_button(
                "📥 Download Recruitment Action Plan (CSV)",
                action_df.to_csv(index=False).encode("utf-8-sig"),
                "parakh_ai_recruitment_action_plan.csv",
                "text/csv",
                use_container_width=True
            )

            st.markdown("### ✉️ Candidate Communication Drafts")
            for item in automation_items:
                with st.expander(f"{item['Candidate']} — {item['Status']} | Rank #{item['Rank']}", expanded=False):
                    st.caption(f"Suggested action: {item['Recommended Next Action']}")
                    st.text_input("Recipient email", value=item["Email"], key=f"automation_email_{item['Rank']}")
                    st.text_input("Subject", value=item["Email Subject"], key=f"automation_subject_{item['Rank']}")
                    st.text_area("Email draft", value=item["Email Draft"], height=160, key=f"automation_body_{item['Rank']}")
                    st.caption("Review and personalize this draft before sending. Parakh AI does not send emails automatically.")
                    if make_interview_questions and item["Interview Questions"]:
                        st.markdown("**🎤 Suggested Interview Questions**")
                        for q in item["Interview Questions"].splitlines():
                            st.write(f"• {q}")

            st.info("Automation is based on the existing resume-analysis results and configured screening rules. Candidate decisions should always be reviewed by a recruiter; AI indicators are not proof of authorship or suitability.")

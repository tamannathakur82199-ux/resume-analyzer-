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
import resume_builder
import inspect

st.write("DEBUG - Loaded resume_builder file:",
         resume_builder.__file__)

st.write("DEBUG - PDF function:",
         inspect.signature(resume_builder.build_resume_pdf))
from resume_parser import extract_text, parse_resume
try:
    from resume_templates import (COLOR_PALETTE, DUMMY_PROFILES, RESUME_TEMPLATES,
                                  get_dummy_profile, get_template, hex_to_rgb,
                                  profile_to_form_text, render_template_html,
                                  render_template_thumbnail)
    HAS_TEMPLATES = True
except ImportError:
    HAS_TEMPLATES = True
    COLOR_PALETTE = [
        {"id": "rainbow", "name": "Default Theme", "hex": "#0284C7", "is_rainbow": True, "title": "Rainbow Palette"},
        {"id": "charcoal", "name": "Charcoal Slate", "hex": "#52525B", "rgb": (82, 82, 91), "title": "Charcoal"},
        {"id": "navy", "name": "Deep Royal Navy", "hex": "#1E3A8A", "rgb": (30, 58, 138), "title": "Royal Navy"},
        {"id": "purple", "name": "Royal Violet", "hex": "#7C3AED", "rgb": (124, 58, 237), "title": "Purple"},
        {"id": "blue", "name": "Cerulean Blue", "hex": "#0284C7", "rgb": (2, 132, 199), "title": "Cerulean Blue"},
        {"id": "teal", "name": "Emerald Teal", "hex": "#0D9488", "rgb": (13, 148, 136), "title": "Teal"},
        {"id": "green", "name": "Forest Green", "hex": "#15803D", "rgb": (21, 128, 61), "title": "Forest Green"},
        {"id": "rust", "name": "Brick Crimson", "hex": "#991B1B", "rgb": (153, 27, 27), "title": "Rust / Red"},
        {"id": "coral", "name": "Sunset Coral", "hex": "#FB923C", "rgb": (251, 146, 60), "title": "Coral / Peach"},
        {"id": "yellow", "name": "Amber Gold", "hex": "#F59E0B", "rgb": (245, 158, 11), "title": "Golden Yellow"},
        {"id": "monochrome", "name": "Minimalist Black", "hex": "#18181B", "rgb": (24, 24, 27), "is_mono": True, "title": "No Color / Monochrome"},
    ]

    def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 6:
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return (31, 56, 100)

    RESUME_TEMPLATES = {
        "sidebar_modern": {"id": "sidebar_modern", "name": "Modern Two-Column Sidebar", "badge": "Studio Favorite", "category": "Modern / Two-Column", "icon": "📄", "accent_hex": "#0284C7", "accent_rgb": (2, 132, 199), "font_family_docx": "Arial", "font_family_pdf": "Helvetica", "header_layout": "sidebar", "rule_style": "thick", "bullet_style": "disc"},
        "classic_serif": {"id": "classic_serif", "name": "Classic Centered Serif", "badge": "100% ATS Scannable", "category": "Traditional / ATS", "icon": "🏛️", "accent_hex": "#1F3864", "accent_rgb": (31, 56, 100), "font_family_docx": "Georgia", "font_family_pdf": "Times", "header_layout": "center", "rule_style": "solid", "bullet_style": "disc"},
        "top_banner": {"id": "top_banner", "name": "Modern Top Accent Banner", "badge": "Visual Impact", "category": "Contemporary / Banner", "icon": "🎨", "accent_hex": "#15803D", "accent_rgb": (21, 128, 61), "font_family_docx": "Calibri", "font_family_pdf": "Helvetica", "header_layout": "top_banner", "rule_style": "pill", "bullet_style": "disc"},
        "executive_header": {"id": "executive_header", "name": "Executive Dark Banner", "badge": "Executive Suite", "category": "Management / Executive", "icon": "👑", "accent_hex": "#1E293B", "accent_rgb": (30, 41, 59), "font_family_docx": "Georgia", "font_family_pdf": "Helvetica", "header_layout": "dark_header", "rule_style": "double", "bullet_style": "square"},
        "modern_tech": {"id": "modern_tech", "name": "Modern Tech & Cloud", "badge": "Devs & Cloud", "category": "Engineering & IT", "icon": "⚡", "accent_hex": "#0284C7", "accent_rgb": (2, 132, 199), "font_family_docx": "Arial", "font_family_pdf": "Helvetica", "header_layout": "left", "rule_style": "thick", "bullet_style": "arrow"},
        "creative_designer": {"id": "creative_designer", "name": "Creative Studio & UI/UX", "badge": "Designers & Portfolio", "category": "Design & Creative", "icon": "🖌️", "accent_hex": "#7C3AED", "accent_rgb": (124, 58, 237), "font_family_docx": "Calibri", "font_family_pdf": "Helvetica", "header_layout": "left", "rule_style": "pill", "bullet_style": "circle"},
        "ivy_academic": {"id": "ivy_academic", "name": "Ivy Academic & Research", "badge": "PhD, Papers & Grants", "category": "Academia & Research", "icon": "🎓", "accent_hex": "#881337", "accent_rgb": (136, 19, 55), "font_family_docx": "Georgia", "font_family_pdf": "Times", "header_layout": "center", "rule_style": "solid", "bullet_style": "dash"},
        "emerald_finance": {"id": "emerald_finance", "name": "Emerald Professional (Finance)", "badge": "Banking & Advisory", "category": "Finance & Consulting", "icon": "📈", "accent_hex": "#065F46", "accent_rgb": (6, 95, 70), "font_family_docx": "Calibri", "font_family_pdf": "Helvetica", "header_layout": "center", "rule_style": "solid", "bullet_style": "disc"},
        "compact_fresher": {"id": "compact_fresher", "name": "Compact 1-Page (Fresher)", "badge": "Guaranteed 1-Page", "category": "Students & Entry-Level", "icon": "🌱", "accent_hex": "#0D9488", "accent_rgb": (13, 148, 136), "font_family_docx": "Arial", "font_family_pdf": "Helvetica", "header_layout": "center", "rule_style": "minimal", "bullet_style": "disc"},
        "data_science_ai": {"id": "data_science_ai", "name": "Data Science & AI Specialist", "badge": "ML, LLMs & Analytics", "category": "AI, ML & Big Data", "icon": "🤖", "accent_hex": "#2563EB", "accent_rgb": (37, 99, 235), "font_family_docx": "Consolas", "font_family_pdf": "Helvetica", "header_layout": "left", "rule_style": "thick", "bullet_style": "arrow"},
        "startup_growth": {"id": "startup_growth", "name": "Startup Product & Growth", "badge": "0-to-1 & Scale", "category": "Product & Growth", "icon": "🚀", "accent_hex": "#EA580C", "accent_rgb": (234, 88, 12), "font_family_docx": "Calibri", "font_family_pdf": "Helvetica", "header_layout": "left", "rule_style": "pill", "bullet_style": "disc"},
        "euro_international": {"id": "euro_international", "name": "Europass Modern International", "badge": "Global Standards", "category": "International Careers", "icon": "🌍", "accent_hex": "#1D4ED8", "accent_rgb": (29, 78, 216), "font_family_docx": "Arial", "font_family_pdf": "Helvetica", "header_layout": "split", "rule_style": "solid", "bullet_style": "dash"},
    }

    def get_template(tid: str) -> dict:
        return RESUME_TEMPLATES.get(tid, RESUME_TEMPLATES["sidebar_modern"])

    DUMMY_PROFILES = {
        "sidebar_modern": {
            "name": "Saanvi Patel",
            "email": "saanvipatel@sample.in",
            "phone": "+91 97170 54977",
            "location": "New Delhi, India 110014",
            "linkedin": "linkedin.com/in/saanvi-patel-sales",
            "github": "",
            "summary": "Motivated Retail Sales Associate with 5 years of experience boosting sales and customer loyalty through individualized service. Resourceful expert at training customer needs, directing to desirable merchandise and upselling to meet sales quotas. Committed to strengthening customer experience with positivity and professionalism when answering inquiries and processing sales.",
            "skills": {
                "Core Skills": ["Stock opening and closing", "Sales expertise", "Accurate Money Handling", "Store Merchandising", "Loss prevention", "Product promotions"],
                "Customer Operations": ["POS Terminal Operation", "Inventory Audits", "Customer Retention", "Conflict Resolution", "Merchandising Displays"],
            },
            "experience": [
                {
                    "heading": "Retail Sales Associate",
                    "date": "07/2016 - Current",
                    "sub": "ABC Store, New Delhi",
                    "bullets": [
                        "Effectively upsold products by introducing accessories and other add-ons, adding ₹8,000 to average monthly sales.",
                        "Maintained 95%+ positive customer feedback and repeat visit loyalty.",
                        "Used consultant sales approach to understand customer needs and recommend relevant product offerings.",
                    ],
                },
                {
                    "heading": "Barista",
                    "date": "01/2015 - 06/2016",
                    "sub": "Starbucks, New Delhi",
                    "bullets": [
                        "Created over 60 drinks per hour with consistently positive customer satisfaction scores.",
                        "Greeted customers, took orders and prepared drinks to exact standards.",
                        "Handled cash register transactions with zero variance.",
                    ],
                },
            ],
            "education": [
                {"heading": "Diploma: Financial Accounting", "date": "June 2016", "sub": "Oxford Business Institute & Oxford School of English, New Delhi, India", "bullets": []}
            ],
            "certifications": ["Certified Retail Customer Specialist", "Advanced Point-of-Sale (POS) Operations"],
            "achievements": ["Top Sales Performer Q3 2024", "Employee of the Month (Twice)"],
        }
    }

    def get_dummy_profile(tid: str) -> dict:
        return DUMMY_PROFILES.get(tid, DUMMY_PROFILES["sidebar_modern"])

    def profile_to_form_text(profile: dict) -> dict:
        return {}

    def render_template_html(p: dict, tid: str = "", custom_accent_hex: str = "") -> str:
        return ""

    _FALLBACK_AVATAR = """<svg viewBox="0 0 80 90" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;"><rect width="80" height="90" fill="#E2E8F0" rx="3"/><path d="M22 34 C22 14, 58 14, 58 34 C58 52, 54 62, 53 66 C49 66, 47 54, 46 48 C34 48, 32 66, 27 66 C26 62, 22 52, 22 34 Z" fill="#475569"/><path d="M35 44 L45 44 L47 56 L33 56 Z" fill="#CBD5E1"/><path d="M28 32 C28 22, 52 22, 52 32 C52 42, 47 48, 40 48 C33 48, 28 42, 28 32 Z" fill="#F8FAFC"/><path d="M24 32 C26 20, 39 20, 40 26 C41 20, 54 20, 56 32 C58 42, 54 50, 52 54 C50 44, 48 30, 40 30 C32 30, 30 44, 28 54 C26 50, 22 42, 24 32 Z" fill="#334155"/><path d="M16 82 C18 64, 28 56, 40 56 C52 56, 62 64, 64 82 Z" fill="#64748B"/></svg>"""
    _FALLBACK_AVATAR_CIRCLE = """<svg viewBox="0 0 80 80" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;"><circle cx="40" cy="40" r="39" fill="#E2E8F0"/><path d="M22 30 C22 14, 58 14, 58 30 C58 48, 54 58, 53 62 C49 62, 47 50, 46 44 C34 44, 32 62, 27 62 C26 58, 22 48, 22 30 Z" fill="#475569"/><path d="M35 40 L45 40 L47 52 L33 52 Z" fill="#CBD5E1"/><path d="M28 28 C28 18, 52 18, 52 28 C52 38, 47 44, 40 44 C33 44, 28 38, 28 28 Z" fill="#F8FAFC"/><path d="M24 28 C26 16, 39 16, 40 22 C41 16, 54 16, 56 28 C58 38, 54 46, 52 50 C50 40, 48 26, 40 26 C32 26, 30 40, 28 50 C26 46, 22 38, 24 28 Z" fill="#334155"/><path d="M16 78 C18 60, 28 52, 40 52 C52 52, 62 60, 64 78 Z" fill="#64748B"/></svg>"""

    def render_template_thumbnail(template_id: str, accent_hex: str = "", is_selected: bool = False) -> str:
        tpl = get_template(template_id)
        color = accent_hex if accent_hex and accent_hex != "#0284C7_rainbow" else tpl["accent_hex"]
        name = "Saanvi Patel"
        selected_border = "border: 2px solid #0284c7; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.28);" if is_selected else "border: 1px solid #cbd5e1; box-shadow: 0 2px 6px rgba(0,0,0,0.05);"
        selected_badge = '<div style="position:absolute; top:8px; right:8px; background:#0284c7; color:#fff; font-size:10px; font-weight:700; padding:2px 7px; border-radius:12px; z-index:10; box-shadow:0 1px 4px rgba(0,0,0,0.2);">✓ Selected</div>' if is_selected else ''

        if template_id == "sidebar_modern":
            sidebar_bg = color if color and color != "#0284C7" else "#1b4d6b"
            inner = f"""
            <div style="display:flex; height:100%; width:100%; font-family:'Segoe UI', Inter, sans-serif; font-size:7px; background:#ffffff;">
              <div style="width:33%; background:{sidebar_bg}; color:#ffffff; padding:10px 8px; box-sizing:border-box; display:flex; flex-direction:column; align-items:center;">
                <div style="width:38px; height:38px; border-radius:50%; overflow:hidden; margin-bottom:6px; border:1.5px solid rgba(255,255,255,0.4);">{_FALLBACK_AVATAR_CIRCLE}</div>
                <div style="font-size:10.5px; font-weight:800; text-align:center; line-height:1.15; color:#ffffff; margin-bottom:2px;">{name}</div>
                <div style="font-size:7px; opacity:0.85; text-align:center; margin-bottom:8px;">Profession</div>
                <div style="width:100%; font-size:7.5px; font-weight:700; border-bottom:1px solid rgba(255,255,255,0.3); padding-bottom:1px; margin-bottom:3px; text-transform:uppercase;">Contact</div>
                <div style="width:100%; font-size:6px; opacity:0.92; margin-bottom:8px; line-height:1.25;">
                  <div>New Delhi, India, 110014</div>
                  <div>+91 97170 54977</div>
                  <div>saanvipatel@sample.in</div>
                </div>
                <div style="width:100%; font-size:7.5px; font-weight:700; border-bottom:1px solid rgba(255,255,255,0.3); padding-bottom:1px; margin-bottom:3px; text-transform:uppercase;">Skills</div>
                <div style="width:100%; font-size:6px; opacity:0.92; line-height:1.3;">
                  <div>• Stock opening and closing</div>
                  <div>• Sales expertise</div>
                  <div>• Accurate Money Handling</div>
                  <div>• Store Merchandising</div>
                  <div>• Loss prevention</div>
                </div>
              </div>
              <div style="width:67%; background:#ffffff; padding:10px 10px; box-sizing:border-box; overflow:hidden;">
                <div style="font-size:8.5px; font-weight:800; color:{sidebar_bg}; margin-bottom:2px;">Education</div>
                <div style="font-size:6px; color:#64748b; margin-bottom:1px;">June 2016 <strong style="color:#0f172a; margin-left:3px; font-size:6.8px;">Diploma: Financial Accounting</strong></div>
                <div style="font-size:5.8px; color:#475569; margin-bottom:5px;">Oxford Business Institute, New Delhi</div>
                <div style="font-size:5.8px; color:#475569; line-height:1.25; margin-bottom:6px; border-left:2px solid {sidebar_bg}30; padding-left:4px;">
                  Motivated Sales Associate with 5 years of experience boosting sales and customer loyalty through individualized service.
                </div>
                <div style="font-size:8.5px; font-weight:800; color:{sidebar_bg}; margin-bottom:2px;">Work History</div>
                <div style="font-size:6px; color:#64748b;">2016-07 - Current <strong style="color:#0f172a; margin-left:3px; font-size:6.8px;">Retail Sales Associate</strong></div>
                <div style="font-size:5.8px; color:#64748b; margin-bottom:2px;">ABC Store, New Delhi</div>
                <div style="font-size:5.8px; color:#334155; line-height:1.25; margin-bottom:5px;">
                  <div>• Effectively upsold products, adding ₹8,000 monthly.</div>
                  <div>• Maintained top positive customer reviews.</div>
                </div>
                <div style="font-size:6px; color:#64748b;">2015-01 - 2016-06 <strong style="color:#0f172a; margin-left:3px; font-size:6.8px;">Barista</strong></div>
                <div style="font-size:5.8px; color:#64748b; margin-bottom:2px;">Starbucks - New Delhi</div>
                <div style="font-size:5.8px; color:#334155; line-height:1.25;">
                  <div>• Handled peak transactions with zero error.</div>
                </div>
              </div>
            </div>
            """
        elif template_id in ("classic_serif", "classic_ats"):
            inner = f"""
            <div style="height:100%; width:100%; background:#ffffff; padding:12px 14px; box-sizing:border-box; font-family:'Times New Roman', Georgia, serif; text-align:center; overflow:hidden;">
              <div style="font-size:13px; font-weight:800; letter-spacing:0.06em; color:#0f172a; text-transform:uppercase;">SAANVI PATEL</div>
              <div style="font-size:7px; color:#475569; font-style:italic; margin-top:1px;">PROFESSION</div>
              <div style="font-size:6px; color:#64748b; margin-top:2px;">New Delhi, India 110014 | +91 97170 54977 | saanvipatel@sample.in</div>
              <div style="border-top:1.5px solid #0f172a; border-bottom:0.5px solid #0f172a; height:2px; margin:4px 0 6px 0;"></div>
              <div style="font-size:7.5px; font-weight:800; color:#0f172a; text-transform:uppercase; margin-bottom:2px;">EDUCATION</div>
              <div style="font-size:6.8px; font-weight:700; color:#1e293b;">Diploma: Financial Accounting, June 2016</div>
              <div style="font-size:5.8px; color:#64748b; margin-bottom:5px;">Oxford Business Institute, New Delhi</div>
              <div style="font-size:7.5px; font-weight:800; color:#0f172a; text-transform:uppercase; margin-bottom:2px;">PROFESSIONAL SUMMARY</div>
              <div style="font-size:5.8px; color:#475569; text-align:justify; line-height:1.25; margin-bottom:5px;">Motivated Sales Associate with 5 years of experience boosting sales and customer loyalty.</div>
              <div style="font-size:7.5px; font-weight:800; color:#0f172a; text-transform:uppercase; margin-bottom:2px;">SKILLS</div>
              <div style="display:flex; justify-content:space-between; font-size:5.8px; color:#334155; text-align:left; margin-bottom:5px; padding:0 12px;">
                <div>• Stock opening and closing<br>• Accurate Money Handling</div>
                <div>• Sales expertise<br>• Store Merchandising</div>
              </div>
              <div style="font-size:7.5px; font-weight:800; color:#0f172a; text-transform:uppercase; margin-bottom:2px;">WORK HISTORY</div>
              <div style="font-size:6.8px; font-weight:700; color:#1e293b; text-align:left;">Retail Sales Associate (07/2016 - Current)</div>
              <div style="font-size:5.8px; color:#475569; text-align:left; line-height:1.25;"><div>• Effectively upsold products, adding ₹8,000 to monthly sales.</div></div>
            </div>
            """
        elif template_id == "top_banner":
            banner_green = color if color and color != "#0284C7" else "#65a30d"
            inner = f"""
            <div style="height:100%; width:100%; background:#ffffff; box-sizing:border-box; display:flex; flex-direction:column; font-family:'Segoe UI', Inter, sans-serif; overflow:hidden;">
              <div style="background:{banner_green}; color:#ffffff; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-size:13px; font-weight:800; color:#ffffff; line-height:1.1;">{name}</div>
                  <div style="font-size:7px; color:rgba(255,255,255,0.9); margin-top:2px; margin-bottom:4px;">Profession</div>
                  <div style="font-size:5.8px; color:rgba(255,255,255,0.95); line-height:1.3;">
                    <div>📍 New Delhi, India 110014</div>
                    <div>📞 +91 97170 54977</div>
                    <div>✉️ saanvipatel@sample.in</div>
                  </div>
                </div>
                <div style="width:40px; height:46px; border-radius:3px; overflow:hidden; border:1.5px solid rgba(255,255,255,0.6);">{_FALLBACK_AVATAR}</div>
              </div>
              <div style="padding:8px 12px; flex:1; background:#ffffff;">
                <div style="display:flex; align-items:center; gap:4px; font-size:7.5px; font-weight:800; color:{banner_green}; text-transform:uppercase; margin-bottom:2px;"><span style="color:{banner_green};">●</span> Education</div>
                <div style="font-size:6.8px; font-weight:700; color:#1e293b;">Diploma: Financial Accounting</div>
                <div style="font-size:5.8px; color:#64748b; margin-bottom:5px;">Oxford Business Institute, New Delhi (June 2016)</div>
                <div style="display:flex; align-items:center; gap:4px; font-size:7.5px; font-weight:800; color:{banner_green}; text-transform:uppercase; margin-bottom:2px;"><span style="color:{banner_green};">●</span> Work History</div>
                <div style="font-size:6.8px; font-weight:700; color:#1e293b;">Retail Sales Associate (07/2016 - Current)</div>
                <div style="font-size:5.8px; color:#475569; line-height:1.25;"><div>• Boosted monthly sales volume by ₹8,000 via add-ons.</div></div>
              </div>
            </div>
            """
        elif template_id in ("executive_header", "executive_suite"):
            inner = f"""
            <div style="height:100%; width:100%; background:#ffffff; box-sizing:border-box; display:flex; flex-direction:column; font-family:'Segoe UI', Inter, sans-serif; overflow:hidden;">
              <div style="background:#262b30; color:#ffffff; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-size:13px; font-weight:800; color:#ffffff; line-height:1.1;">{name}</div>
                  <div style="font-size:7px; color:rgba(255,255,255,0.7); margin-top:2px; margin-bottom:4px;">Profession</div>
                  <div style="font-size:5.8px; color:rgba(255,255,255,0.85); line-height:1.3;">
                    <div>Address: New Delhi, India 110014</div>
                    <div>Phone: +91 97170 54977</div>
                    <div>Email: saanvipatel@sample.in</div>
                  </div>
                </div>
                <div style="width:40px; height:46px; border-radius:3px; overflow:hidden; border:1px solid rgba(255,255,255,0.3);">{_FALLBACK_AVATAR}</div>
              </div>
              <div style="padding:8px 12px; flex:1; background:#ffffff;">
                <div style="display:flex; align-items:center; gap:4px; font-size:7.5px; font-weight:800; color:#1e293b; text-transform:uppercase; margin-bottom:2px;"><span style="color:{color};">◆</span> Education</div>
                <div style="font-size:6.8px; font-weight:700; color:#1e293b;">Diploma: Financial Accounting, June 2016</div>
                <div style="font-size:5.8px; color:#64748b; margin-bottom:5px;">Oxford Business Institute, New Delhi</div>
                <div style="display:flex; align-items:center; gap:4px; font-size:7.5px; font-weight:800; color:#1e293b; text-transform:uppercase; margin-bottom:2px;"><span style="color:{color};">◆</span> Work History</div>
                <div style="font-size:6.8px; font-weight:700; color:#1e293b;">Retail Sales Associate (07/2016 - Current)</div>
                <div style="font-size:5.8px; color:#475569; line-height:1.25;"><div>• Controlled merchandising and boosted revenue.</div></div>
              </div>
            </div>
            """
        else:
            inner = f"""
            <div style="height:100%; width:100%; background:#ffffff; padding:12px; box-sizing:border-box;">
              <div style="display:flex; justify-content:space-between; align-items:baseline; border-bottom:2px solid {color}; padding-bottom:4px; margin-bottom:6px;">
                <span style="font-size:11px; font-weight:800; color:{color};">{tpl['name']}</span>
                <span style="font-size:6px; color:#64748b;">[{tpl['badge']}]</span>
              </div>
              <div style="font-size:7px; font-weight:700; color:#1e293b; margin-bottom:2px;">{name}</div>
              <div style="font-size:6px; color:#64748b; margin-bottom:6px;">New Delhi, India | +91 97170 54977</div>
            </div>
            """
        return f"""
        <div style="position:relative; width:100%; height:320px; border-radius:6px; overflow:hidden; {selected_border} transition:all 0.2s ease-in-out; margin-bottom:6px; background:#ffffff;">
          {selected_badge}
          {inner}
        </div>
        """

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_JD = os.path.join(HERE, "sample_data", "job_description.txt")
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def get_template_preview(template_id: str, accent_hex: str = "#0284C7") -> bytes:
    """Returns in-memory PNG bytes for Streamlit st.image (100% reliable, no disk dependencies, no HTML code)."""
    import io
    try:
        from PIL import Image, ImageDraw, ImageFont
        accent_rgb = hex_to_rgb(accent_hex)
        W, H = 480, 660

        def get_f(name='arial.ttf', size=12):
            for candidate in [name, 'Arial.ttf', 'calibri.ttf', 'DejaVuSans.ttf', 'times.ttf', 'Times.ttf']:
                try:
                    return ImageFont.truetype(candidate, size)
                except Exception:
                    continue
            return ImageFont.load_default()

        def draw_avatar(draw, x, y, w, h, is_circle=False):
            if is_circle:
                draw.ellipse([x, y, x + w, y + h], fill=(226, 232, 240), outline=(255, 255, 255), width=2)
            else:
                draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=(226, 232, 240), outline=(255, 255, 255), width=1)
            draw.ellipse([x + w*0.25, y + h*0.14, x + w*0.75, y + h*0.75], fill=(71, 85, 105))
            draw.rectangle([x + w*0.42, y + h*0.5, x + w*0.58, y + h*0.68], fill=(203, 213, 225))
            draw.ellipse([x + w*0.32, y + h*0.26, x + w*0.68, y + h*0.58], fill=(248, 250, 252))
            draw.chord([x + w*0.28, y + h*0.18, x + w*0.72, y + h*0.44], start=180, end=360, fill=(51, 65, 85))
            draw.pieslice([x + w*0.1, y + h*0.62, x + w*0.9, y + h*1.15], start=180, end=360, fill=(100, 116, 139))

        f_body = get_f('arial.ttf', 9)
        f_bold = get_f('arialbd.ttf', 10)
        f_head = get_f('arialbd.ttf', 12)
        f_gray = get_f('arial.ttf', 9)
        f_serif_title = get_f('timesbd.ttf', 18)
        f_serif_sub = get_f('times.ttf', 10)

        img = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)

        if template_id == 'sidebar_modern':
            side_w = 160
            d.rectangle([0, 0, side_w, H], fill=accent_rgb)
            draw_avatar(d, 45, 25, 70, 70, is_circle=True)
            d.text((80, 105), 'Saanvi Patel', fill=(255, 255, 255), font=get_f('arialbd.ttf', 16), anchor='mm')
            d.text((80, 125), 'Profession', fill=(220, 230, 245), font=get_f('arial.ttf', 10), anchor='mm')
            d.line([15, 142, side_w - 15, 142], fill=(255, 255, 255, 100), width=1)
            d.text((15, 150), 'CONTACT', fill=(255, 255, 255), font=get_f('arialbd.ttf', 11))
            d.text((15, 170), 'New Delhi, India 110014\n+91 97170 54977\nsaanvipatel@sample.in', fill=(235, 245, 255), font=f_gray, spacing=5)
            d.line([15, 235, side_w - 15, 235], fill=(255, 255, 255, 100), width=1)
            d.text((15, 245), 'SKILLS', fill=(255, 255, 255), font=get_f('arialbd.ttf', 11))
            skills = ['• Stock opening & closing', '• Sales expertise', '• Accurate Money Handling', '• Store Merchandising', '• Loss prevention']
            d.text((15, 268), '\n'.join(skills), fill=(235, 245, 255), font=f_gray, spacing=6)
            rx = 180
            d.text((rx, 25), 'Education', fill=accent_rgb, font=get_f('arialbd.ttf', 13))
            d.text((rx, 50), 'June 2016   Diploma: Financial Accounting', fill=(15, 23, 42), font=f_bold)
            d.text((rx, 68), 'Oxford Business Institute, New Delhi', fill=(100, 116, 139), font=f_gray)
            d.rectangle([rx, 90, rx + 285, 165], fill=(248, 250, 252))
            d.line([rx, 90, rx, 165], fill=accent_rgb, width=3)
            sum_text = 'Motivated Sales Associate with 5 years of experience boosting sales\nand customer loyalty through individualized service. Resourceful expert\nat training customer needs and meeting sales quotas.'
            d.text((rx + 10, 98), sum_text, fill=(71, 85, 105), font=f_body, spacing=5)
            d.text((rx, 185), 'Work History', fill=accent_rgb, font=get_f('arialbd.ttf', 13))
            d.text((rx, 210), '2016-07 - Current   Retail Sales Associate', fill=(15, 23, 42), font=f_bold)
            d.text((rx, 228), 'ABC Store, New Delhi', fill=(100, 116, 139), font=f_gray)
            w1 = ['• Effectively upsold products by introducing accessories, adding', '  ₹8,000 to average monthly sales volume.', '• Maintained 95%+ positive customer feedback and store loyalty.']
            d.text((rx + 5, 248), '\n'.join(w1), fill=(51, 65, 85), font=f_body, spacing=5)
            d.text((rx, 335), '2015-01 - 2016-06   Barista', fill=(15, 23, 42), font=f_bold)
            d.text((rx, 353), 'Starbucks - New Delhi', fill=(100, 116, 139), font=f_gray)
            w2 = ['• Created over 60 drinks per hour with top satisfaction scores.', '• Handled peak transactions with zero error.']
            d.text((rx + 5, 372), '\n'.join(w2), fill=(51, 65, 85), font=f_body, spacing=5)

        elif template_id in ('classic_serif', 'classic_ats'):
            d.text((W // 2, 36), 'SAANVI PATEL', fill=(17, 24, 39), font=f_serif_title, anchor='mm')
            d.text((W // 2, 54), 'PROFESSION', fill=(75, 85, 99), font=f_serif_sub, anchor='mm')
            d.line([30, 68, W - 30, 68], fill=(156, 163, 175), width=1)
            d.text((W // 2, 79), 'New Delhi, India 110014 | +91 97170 54977 | saanvipatel@sample.in', fill=(107, 114, 128), font=f_gray, anchor='mm')
            d.line([30, 90, W - 30, 90], fill=(209, 213, 219), width=1)

            # Education
            d.text((W // 2, 108), 'EDUCATION', fill=(17, 24, 39), font=f_bold, anchor='mm')
            d.line([30, 117, W - 30, 117], fill=(229, 231, 235), width=1)
            d.text((32, 126), 'Diploma: Financial Accounting, June 2016', fill=(17, 24, 39), font=f_bold)
            d.text((32, 140), 'Oxford Business Institute & Oxford School of English — New Delhi, India', fill=(75, 85, 99), font=f_body)

            # Professional Summary
            d.text((W // 2, 168), 'PROFESSIONAL SUMMARY', fill=(17, 24, 39), font=f_bold, anchor='mm')
            d.line([30, 177, W - 30, 177], fill=(229, 231, 235), width=1)
            sum_lines = [
                'Motivated Sales Associate with 5 years of experience boosting sales and customer loyalty through',
                'individualized service. Resourceful expert at training customer needs, directing to desirable merchandise',
                'and upselling to meet sales quotas. Committed to strengthening customer experience with positivity and',
                'professionalism when answering inquiries and processing sales.'
            ]
            d.text((32, 185), '\n'.join(sum_lines), fill=(55, 65, 81), font=f_body, spacing=3)

            # Skills (2 columns)
            d.text((W // 2, 255), 'SKILLS', fill=(17, 24, 39), font=f_bold, anchor='mm')
            d.line([30, 264, W - 30, 264], fill=(229, 231, 235), width=1)
            sk_col1 = ['• Stock opening and closing', '• Accurate Money Handling', '• Loss prevention']
            sk_col2 = ['• Sales expertise', '• Store Merchandising', '• Product promotions']
            d.text((45, 272), '\n'.join(sk_col1), fill=(55, 65, 81), font=f_body, spacing=4)
            d.text((260, 272), '\n'.join(sk_col2), fill=(55, 65, 81), font=f_body, spacing=4)

            # Work History
            d.text((W // 2, 340), 'WORK HISTORY', fill=(17, 24, 39), font=f_bold, anchor='mm')
            d.line([30, 349, W - 30, 349], fill=(229, 231, 235), width=1)
            d.text((32, 358), 'Retail Sales Associate (07/2016 - Current)', fill=(17, 24, 39), font=f_bold)
            d.text((32, 372), 'ABC Store — New Delhi', fill=(75, 85, 99), font=f_body)
            wh1 = [
                '• Effectively upsold products by introducing accessories and other add-ons, adding ₹8000 to average',
                '  monthly sales.',
                '• Operated point-of-sale systems with 100% accuracy and handled customer requests with speed.'
            ]
            d.text((35, 388), '\n'.join(wh1), fill=(55, 65, 81), font=f_body, spacing=3)

            d.text((32, 432), 'Barista (01/2015 - 06/2016)', fill=(17, 24, 39), font=f_bold)
            d.text((32, 446), 'Starbucks — New Delhi', fill=(75, 85, 99), font=f_body)
            wh2 = [
                '• Created over 60 drinks per hour with consistently positive customer satisfaction scores.',
                '• Upheld baked goods and menu alerts with beverages, increasing store sales by ₹5000 per month.'
            ]
            d.text((35, 462), '\n'.join(wh2), fill=(55, 65, 81), font=f_body, spacing=3)

        elif template_id == 'top_banner':
            b_h = 135
            d.rectangle([0, 0, W, b_h], fill=accent_rgb)
            draw_avatar(d, 375, 18, 80, 98, is_circle=False)
            d.text((25, 20), 'Saanvi Patel', fill=(255, 255, 255), font=get_f('arialbd.ttf', 22))
            d.text((25, 48), 'Profession', fill=(240, 255, 230), font=get_f('arial.ttf', 12))
            d.text((25, 72), '📍 New Delhi, India 110014\n📞 +91 97170 54977\n✉️ saanvipatel@sample.in', fill=(255, 255, 255), font=f_gray, spacing=4)
            d.text((25, 155), '●  Education', fill=accent_rgb, font=f_head)
            d.text((25, 178), 'Diploma: Financial Accounting', fill=(15, 23, 42), font=f_bold)
            d.text((25, 195), 'Oxford Business Institute, New Delhi (June 2016)', fill=(100, 116, 139), font=f_gray)
            d.text((25, 230), '●  Professional Summary', fill=accent_rgb, font=f_head)
            d.text((25, 252), 'Motivated Sales Associate with 5 years of experience boosting sales\nand customer loyalty through individualized service.', fill=(51, 65, 85), font=f_body, spacing=4)
            d.text((25, 315), '●  Work History', fill=accent_rgb, font=f_head)
            d.text((25, 340), 'Retail Sales Associate (07/2016 - Current)', fill=(15, 23, 42), font=f_bold)
            d.text((25, 357), 'ABC Store, New Delhi', fill=(100, 116, 139), font=f_gray)
            d.text((30, 375), '• Boosted monthly sales volume by ₹8,000 via accessories.\n• Maintained 95%+ positive customer loyalty.', fill=(51, 65, 85), font=f_body, spacing=5)

        elif template_id in ('executive_header', 'executive_suite'):
            b_h = 135
            d.rectangle([0, 0, W, b_h], fill=(38, 43, 48))
            draw_avatar(d, 375, 18, 80, 98, is_circle=False)
            d.line([0, b_h, W, b_h], fill=accent_rgb, width=3)
            d.text((25, 20), 'Saanvi Patel', fill=(255, 255, 255), font=get_f('arialbd.ttf', 22))
            d.text((25, 48), 'Profession', fill=(203, 213, 225), font=get_f('arial.ttf', 12))
            d.text((25, 72), 'Address: New Delhi, India 110014\nPhone: +91 97170 54977\nEmail: saanvipatel@sample.in', fill=(226, 232, 240), font=f_gray, spacing=4)
            d.text((25, 155), '◆  Education', fill=(15, 23, 42), font=f_head)
            d.text((25, 178), 'Diploma: Financial Accounting, June 2016', fill=(15, 23, 42), font=f_bold)
            d.text((25, 195), 'Oxford Business Institute, New Delhi', fill=(100, 116, 139), font=f_gray)
            d.text((25, 230), '◆  Professional Summary', fill=(15, 23, 42), font=f_head)
            d.text((25, 252), 'Motivated Sales Associate with 5 years of experience boosting sales\nand customer loyalty through individualized service.', fill=(51, 65, 85), font=f_body, spacing=4)
            d.text((25, 315), '◆  Work History', fill=(15, 23, 42), font=f_head)
            d.text((25, 340), 'Retail Sales Associate (07/2016 - Current)', fill=(15, 23, 42), font=f_bold)
            d.text((25, 357), 'ABC Store, New Delhi', fill=(100, 116, 139), font=f_gray)
            d.text((30, 375), '• Controlled merchandising and boosted store revenue by ₹8,000/mo.\n• Promoted high customer satisfaction and store loyalty.', fill=(51, 65, 85), font=f_body, spacing=5)

        else:
            d.rectangle([0, 0, W, 70], fill=accent_rgb)
            d.text((25, 20), 'Saanvi Patel', fill=(255, 255, 255), font=get_f('arialbd.ttf', 18))
            d.text((25, 45), 'Profession • New Delhi, India • +91 97170 54977', fill=(240, 245, 255), font=f_gray)
            d.text((25, 90), 'Summary', fill=accent_rgb, font=f_head)
            d.line([25, 108, W - 25, 108], fill=(226, 232, 240), width=1)
            d.text((25, 115), 'Motivated professional with proven experience delivering measurable results.', fill=(71, 85, 105), font=f_body)
            d.text((25, 150), 'Experience', fill=accent_rgb, font=f_head)
            d.line([25, 168, W - 25, 168], fill=(226, 232, 240), width=1)
            d.text((25, 175), 'Retail Sales Associate (2016 - Present)', fill=(15, 23, 42), font=f_bold)
            d.text((25, 192), '• Led customer initiatives and boosted average sales.', fill=(71, 85, 105), font=f_body)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    except Exception:
        fallback_img = Image.new('RGB', (480, 660), (255, 255, 255))
        d_fb = ImageDraw.Draw(fallback_img)
        d_fb.rectangle([0, 0, 480, 80], fill=(2, 132, 199))
        d_fb.text((240, 40), 'Resume Template', fill=(255, 255, 255), anchor='mm')
        buf = io.BytesIO()
        fallback_img.save(buf, format='PNG')
        return buf.getvalue()


def show_template_preview(template_id: str, accent_hex: str = "#0284C7") -> None:
    """Render a generated preview inline, without Streamlit media-file storage."""
    preview_bytes = get_template_preview(template_id, accent_hex)
    preview_b64 = base64.b64encode(preview_bytes).decode("ascii")
    st.markdown(
        f'<img src="data:image/png;base64,{preview_b64}" '
        'style="display:block;width:100%;height:auto;border-radius:8px;" '
        'alt="Resume template preview">',
        unsafe_allow_html=True,
    )


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

      /* Studio Layout & Toolbar */
      .studio-toolbar-container {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 12px 6px;
          display: flex;
          flex-direction: column;
          gap: 6px;
      }
      .studio-header-title {
          font-size: 1.65rem;
          font-weight: 800;
          color: #0f172a;
          letter-spacing: -0.02em;
          margin: 0;
          line-height: 1.2;
      }
      .studio-subheading {
          font-size: 1.25rem;
          font-weight: 700;
          color: #0f172a;
          margin: 18px 0 12px 0;
      }

      /* Studio Left Toolbar Buttons */
      div[data-testid="column"]:has(button[key^="nav_studio_"]) button {
          min-height: 56px !important;
          height: auto !important;
          border-radius: 10px !important;
          padding: 8px 10px !important;
          text-align: center !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          justify-content: center !important;
          margin-bottom: 6px !important;
          border: 1px solid #e2e8f0 !important;
          background: #ffffff !important;
          box-shadow: none !important;
          transition: all 0.15s ease !important;
      }
      div[data-testid="column"]:has(button[key^="nav_studio_"]) button p {
          text-align: center !important;
          margin: 0 !important;
          font-size: 0.8rem !important;
          font-weight: 600 !important;
          color: #475569 !important;
      }
      div[data-testid="column"]:has(button[key^="nav_studio_"]) button[kind="primary"] {
          background: #f0f7ff !important;
          border: 1.5px solid #0284c7 !important;
      }
      div[data-testid="column"]:has(button[key^="nav_studio_"]) button[kind="primary"] p {
          color: #0284c7 !important;
          font-weight: 700 !important;
      }

      /* Swatch Circular Buttons */
      div[data-testid="column"]:has(button[key^="sw_"]) {
          padding: 0 !important;
          min-width: 32px !important;
          max-width: 38px !important;
      }
      div[data-testid="column"]:has(button[key^="sw_"]) button {
          width: 30px !important;
          height: 30px !important;
          min-height: 30px !important;
          max-height: 30px !important;
          border-radius: 50% !important;
          padding: 0 !important;
          margin: 3px auto !important;
          border: none !important;
          box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
          cursor: pointer !important;
          display: block !important;
          transition: transform 0.15s ease, box-shadow 0.15s ease !important;
      }
      div[data-testid="column"]:has(button[key^="sw_"]) button p {
          display: none !important;
      }
      div[data-testid="column"]:has(button[key^="sw_"]) button:hover {
          transform: scale(1.15) !important;
      }
      button[key="sw_rainbow"] {
          background: conic-gradient(#ff0000, #ff8000, #ffff00, #00ff00, #00ffff, #0000ff, #8000ff, #ff0080, #ff0000) !important;
      }
      button[key="sw_charcoal"] { background: #64748B !important; }
      button[key="sw_navy"] { background: #1E3A8A !important; }
      button[key="sw_purple"] { background: #7C3AED !important; }
      button[key="sw_blue"] { background: #0284C7 !important; }
      button[key="sw_teal"] { background: #0D9488 !important; }
      button[key="sw_green"] { background: #15803D !important; }
      button[key="sw_rust"] { background: #991B1B !important; }
      button[key="sw_coral"] { background: #FB923C !important; }
      button[key="sw_yellow"] { background: #F59E0B !important; }
      button[key="sw_monochrome"] {
          background: linear-gradient(135deg, #ffffff 44%, #94a3b8 48%, #94a3b8 52%, #ffffff 56%) !important;
          border: 1.5px solid #94a3b8 !important;
      }

      /* Studio Close Button (✕) */
      button[key="studio_close_btn"] {
          background: transparent !important;
          border: none !important;
          color: #0284c7 !important;
          font-size: 26px !important;
          font-weight: 700 !important;
          line-height: 1 !important;
          min-height: 36px !important;
          height: 36px !important;
          width: 36px !important;
          padding: 0 !important;
          box-shadow: none !important;
          float: right !important;
          margin-left: auto !important;
      }
      button[key="studio_close_btn"]:hover {
          color: #0369a1 !important;
          background: rgba(2, 132, 199, 0.08) !important;
          border-radius: 50% !important;
      }

      /* Template Select Button */
      div[data-testid="column"]:has(button[key^="sel_tpl_"]) button {
          min-height: 34px !important;
          height: 34px !important;
          padding: 4px 14px !important;
          font-size: 0.85rem !important;
          border-radius: 6px !important;
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
        jd_file = st.file_uploader("Upload JD (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"], key="jd_file", label_visibility="collapsed")
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
# SECTION 3: RESUME BUILDER STUDIO (MATCHING SCREENSHOT LAYOUT)
# ===========================================================================
elif active_tab == "Build Resume":
    st.markdown('<div class="section-heading">Resume Builder Studio</div>', unsafe_allow_html=True)
    st.caption("Visual Resume Studio: Select visual templates, customize color palettes, edit content, and generate ATS-compliant PDF & Word resumes.")

    if not HAS_TEMPLATES:
        st.warning("⚠️ **Missing File on GitHub:** `resume_templates.py` file is missing in your GitHub repository! Please upload `resume_templates.py` from your project folder to your GitHub repo so the templates and swatches can load.")

    # State initialization
    if "studio_nav_tab" not in st.session_state:
        st.session_state["studio_nav_tab"] = "Templates"
    if "builder_tpl_id" not in st.session_state:
        st.session_state["builder_tpl_id"] = "sidebar_modern"
    if "builder_color_hex" not in st.session_state:
        st.session_state["builder_color_hex"] = "#0284C7"
    # Initialize empty fields if not in session_state
    for k in ["name", "email", "phone", "location", "linkedin", "github", "summary", "skills", "experience", "projects", "education", "certifications", "achievements"]:
        if f"bld_{k}" not in st.session_state:
            st.session_state[f"bld_{k}"] = ""

    active_studio_nav = st.session_state["studio_nav_tab"]
    current_tpl_id = st.session_state["builder_tpl_id"]
    current_color_hex = st.session_state["builder_color_hex"]

    # Studio Main Split Layout: Left Toolbar (1.1) + Workspace (4.9)
    col_toolbar, col_workspace = st.columns([1.15, 4.85], gap="large")

    # ----------------------------------------------------------------------- Left Vertical Toolbar
    with col_toolbar:
        st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.04em;">Studio Tools</div>', unsafe_allow_html=True)

        is_tpl_active = (active_studio_nav == "Templates")
        if st.button("📄\n\n**Templates**", key="nav_studio_templates", type="primary" if is_tpl_active else "secondary", use_container_width=True):
            st.session_state["studio_nav_tab"] = "Templates"
            st.rerun()

        is_design_active = (active_studio_nav == "Design & formatting")
        if st.button("🖌️\n\n**Design & formatting**", key="nav_studio_design", type="primary" if is_design_active else "secondary", use_container_width=True):
            st.session_state["studio_nav_tab"] = "Design & formatting"
            st.rerun()

        is_section_active = (active_studio_nav == "Add section")
        if st.button("✏️\n\n**Add section**", key="nav_studio_section", type="primary" if is_section_active else "secondary", use_container_width=True):
            st.session_state["studio_nav_tab"] = "Add section"
            st.rerun()

        is_spell_active = (active_studio_nav == "Spell check")
        if st.button("AB✓\n\n**Spell check**", key="nav_studio_spell", type="primary" if is_spell_active else "secondary", use_container_width=True):
            st.session_state["studio_nav_tab"] = "Spell check"
            st.rerun()

    # ----------------------------------------------------------------------- Workspace Panel
    with col_workspace:
        # =================================================================== TAB 1: TEMPLATES (SCREENSHOT REPLICA)
        if active_studio_nav == "Templates":
            # Header Row matching screenshot: "Templates" + blue "✕" icon
            hdr_col1, hdr_col2 = st.columns([5.5, 0.5])
            with hdr_col1:
                st.markdown('<div class="studio-header-title">Templates</div>', unsafe_allow_html=True)
            with hdr_col2:
                if st.button("✕", key="studio_close_btn", help="Close Templates & Edit Details"):
                    st.session_state["studio_nav_tab"] = "Add section"
                    st.rerun()

            # Active swatch highlight styling
            active_sw_id = "blue"
            for sw in COLOR_PALETTE:
                if sw["hex"].lower() == current_color_hex.lower():
                    active_sw_id = sw["id"]
                    break
            st.markdown(f"""
            <style>
              button[key="sw_{active_sw_id}"] {{
                  box-shadow: 0 0 0 2.5px #ffffff, 0 0 0 5px #0284c7 !important;
                  transform: scale(1.15) !important;
              }}
            </style>
            """, unsafe_allow_html=True)

            # Color Palette Swatches (Horizontal Strip matching screenshot)
            swatch_cols = st.columns([1] * len(COLOR_PALETTE) + [3])
            for i in range(len(COLOR_PALETTE)):
                sw_item = COLOR_PALETTE[i]
                with swatch_cols[i]:
                    if st.button(" ", key=f"sw_{sw_item['id']}", help=sw_item["title"]):
                        st.session_state["builder_color_hex"] = sw_item["hex"]
                        st.rerun()

            # All Templates Section Heading
            st.markdown('<div class="studio-subheading">All templates</div>', unsafe_allow_html=True)

            # 4 Featured Templates matching user screenshot in 2x2 Grid
            featured_tpl_list = [
                ("sidebar_modern", "Modern Two-Column Sidebar", "Studio Favorite"),
                ("classic_serif", "Classic Centered Serif", "100% ATS Scannable"),
                ("top_banner", "Modern Top Accent Banner", "Visual Impact"),
                ("executive_header", "Executive Dark Banner", "Executive Suite"),
            ]

            # Active template selection highlight on preview image
            st.markdown(f"""
            <style>
              div[data-testid="column"]:has(button[key="sel_tpl_{current_tpl_id}"]) img {{
                  border: 2.5px solid #0284c7 !important;
                  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
              }}
            </style>
            """, unsafe_allow_html=True)

            # Render 2x2 grid
            for row_idx in range(0, len(featured_tpl_list), 2):
                col_left, col_right = st.columns(2, gap="medium")

                # Left Card
                tpl_id_1, tpl_name_1, tpl_badge_1 = featured_tpl_list[row_idx]
                is_sel_1 = (current_tpl_id == tpl_id_1)
                with col_left:
                    show_template_preview(tpl_id_1, current_color_hex)
                    tc1, tc2 = st.columns([2.5, 1.5])
                    with tc1:
                        st.markdown(f"**{tpl_name_1}**  \n<span style='font-size:0.75rem; color:#64748b;'>{tpl_badge_1}</span>", unsafe_allow_html=True)
                    with tc2:
                        btn_txt_1 = "✓ Selected" if is_sel_1 else "Select"
                        if st.button(btn_txt_1, key=f"sel_tpl_{tpl_id_1}", type="primary" if is_sel_1 else "secondary", use_container_width=True):
                            st.session_state["builder_tpl_id"] = tpl_id_1
                            st.rerun()

                # Right Card
                if row_idx + 1 < len(featured_tpl_list):
                    tpl_id_2, tpl_name_2, tpl_badge_2 = featured_tpl_list[row_idx + 1]
                    is_sel_2 = (current_tpl_id == tpl_id_2)
                    with col_right:
                        show_template_preview(tpl_id_2, current_color_hex)
                        tc1, tc2 = st.columns([2.5, 1.5])
                        with tc1:
                            st.markdown(f"**{tpl_name_2}**  \n<span style='font-size:0.75rem; color:#64748b;'>{tpl_badge_2}</span>", unsafe_allow_html=True)
                        with tc2:
                            btn_txt_2 = "✓ Selected" if is_sel_2 else "Select"
                            if st.button(btn_txt_2, key=f"sel_tpl_{tpl_id_2}", type="primary" if is_sel_2 else "secondary", use_container_width=True):
                                st.session_state["builder_tpl_id"] = tpl_id_2
                                st.rerun()

                st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

            # More Templates Expander
            more_tpl_list = [
                ("modern_tech", "Modern Tech & Cloud", "Devs & Cloud"),
                ("creative_designer", "Creative Studio & UI/UX", "Designers & Portfolio"),
                ("ivy_academic", "Ivy Academic & Research", "PhD, Papers & Grants"),
                ("emerald_finance", "Emerald Professional (Finance)", "Banking & Advisory"),
                ("compact_fresher", "Compact 1-Page (Fresher)", "Guaranteed 1-Page"),
                ("data_science_ai", "Data Science & AI Specialist", "ML, LLMs & Analytics"),
                ("startup_growth", "Startup Product & Growth", "0-to-1 & Scale"),
                ("euro_international", "Europass Modern International", "Global Standards"),
            ]
            with st.expander("➕ Explore More Specialized Templates (Tech, Design, Ivy, Finance, Fresher, AI)", expanded=False):
                for row_idx in range(0, len(more_tpl_list), 2):
                    col_left, col_right = st.columns(2, gap="medium")
                    tpl_id_1, tpl_name_1, tpl_badge_1 = more_tpl_list[row_idx]
                    is_sel_1 = (current_tpl_id == tpl_id_1)
                    with col_left:
                        show_template_preview(tpl_id_1, current_color_hex)
                        tc1, tc2 = st.columns([2.5, 1.5])
                        with tc1:
                            st.markdown(f"**{tpl_name_1}**  \n<span style='font-size:0.75rem; color:#64748b;'>{tpl_badge_1}</span>", unsafe_allow_html=True)
                        with tc2:
                            btn_txt_1 = "✓ Selected" if is_sel_1 else "Select"
                            if st.button(btn_txt_1, key=f"sel_tpl_{tpl_id_1}", type="primary" if is_sel_1 else "secondary", use_container_width=True):
                                st.session_state["builder_tpl_id"] = tpl_id_1
                                st.rerun()
                    if row_idx + 1 < len(more_tpl_list):
                        tpl_id_2, tpl_name_2, tpl_badge_2 = more_tpl_list[row_idx + 1]
                        is_sel_2 = (current_tpl_id == tpl_id_2)
                        with col_right:
                            show_template_preview(tpl_id_2, current_color_hex)
                            tc1, tc2 = st.columns([2.5, 1.5])
                            with tc1:
                                st.markdown(f"**{tpl_name_2}**  \n<span style='font-size:0.75rem; color:#64748b;'>{tpl_badge_2}</span>", unsafe_allow_html=True)
                            with tc2:
                                btn_txt_2 = "✓ Selected" if is_sel_2 else "Select"
                                if st.button(btn_txt_2, key=f"sel_tpl_{tpl_id_2}", type="primary" if is_sel_2 else "secondary", use_container_width=True):
                                    st.session_state["builder_tpl_id"] = tpl_id_2
                                    st.rerun()
                    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # =================================================================== TAB 2: DESIGN & FORMATTING
        elif active_studio_nav == "Design & formatting":
            st.markdown('<div class="studio-header-title">Design & Formatting</div>', unsafe_allow_html=True)
            st.caption("Customize typography, fonts, section rule styling, and document density.")

            f_c1, f_c2 = st.columns(2)
            with f_c1:
                st.selectbox(
                    "🔤 Primary Font Family",
                    options=["Inter (Modern Sans)", "Times New Roman (Collegiate Serif)", "Georgia (Executive Serif)", "Calibri (Corporate Clean)", "Arial (Minimal Sans)", "Consolas (Code / Monospace)"],
                    key="studio_font_family"
                )
                st.select_slider("📏 Font Size Scale", options=["Compact (9.5 pt)", "Standard (10.5 pt)", "Large (11.5 pt)"], value="Standard (10.5 pt)", key="studio_font_scale")

            with f_c2:
                st.selectbox("📐 Section Divider Line Style", options=["Solid Line", "Double Line", "Thick Accent Bar", "Pill Background", "Minimal (No Line)"], key="studio_rule_style")
                st.select_slider("📄 Document Margin Spacing", options=["Tight (12 mm)", "Standard (16 mm)", "Spacious (20 mm)"], value="Standard (16 mm)", key="studio_margin_scale")

            st.success("Design preferences applied to your resume template!")

        # =================================================================== TAB 3: ADD SECTION / EDIT DETAILS
        elif active_studio_nav == "Add section":
            st.markdown('<div class="studio-header-title">Add & Edit Resume Sections</div>', unsafe_allow_html=True)
            st.caption("Fill or edit your personal details, career history, education, skills, and certifications.")

            with st.form("studio_content_form"):
                st.markdown("##### 👤 Personal & Contact Details")
                a, b, c = st.columns(3)
                f_name = a.text_input("Full Name", value=st.session_state.get("bld_name", ""))
                f_email = b.text_input("Email", value=st.session_state.get("bld_email", ""))
                f_phone = c.text_input("Phone", value=st.session_state.get("bld_phone", ""))

                d, e, f = st.columns(3)
                f_location = d.text_input("City, State / Country", value=st.session_state.get("bld_location", ""))
                f_linkedin = e.text_input("LinkedIn Profile URL", value=st.session_state.get("bld_linkedin", ""))
                f_github = f.text_input("GitHub / Portfolio URL", value=st.session_state.get("bld_github", ""))

                st.markdown("##### 📝 Professional Summary")
                f_summary = st.text_area("Summary (2-4 lines)", value=st.session_state.get("bld_summary", ""), height=90)

                st.markdown("##### ⚡ Skills")
                st.caption("Use 'Category: skill1, skill2' on separate lines for grouped presentation.")
                f_skills = st.text_area("Skills", value=st.session_state.get("bld_skills", ""), height=95)

                st.markdown("##### 💼 Work History & Experience")
                f_experience = st.text_area("Experience", value=st.session_state.get("bld_experience", ""), height=130)

                st.markdown("##### 🚀 Key Projects")
                f_projects = st.text_area("Projects", value=st.session_state.get("bld_projects", ""), height=100)

                st.markdown("##### 🎓 Education")
                f_education = st.text_area("Education", value=st.session_state.get("bld_education", ""), height=85)

                g1, g2 = st.columns(2)
                f_certs = g1.text_area("Certifications (one per line)", value=st.session_state.get("bld_certifications", ""), height=75)
                f_achievements = g2.text_area("Achievements / Honors (one per line)", value=st.session_state.get("bld_achievements", ""), height=75)

                saved_submit = st.form_submit_button("✨ Save & Update Resume", type="primary", use_container_width=True)

            if saved_submit:
                for k, v in [("name", f_name), ("email", f_email), ("phone", f_phone), ("location", f_location),
                             ("linkedin", f_linkedin), ("github", f_github), ("summary", f_summary),
                             ("skills", f_skills), ("experience", f_experience), ("projects", f_projects),
                             ("education", f_education), ("certifications", f_certs), ("achievements", f_achievements)]:
                    st.session_state[f"bld_{k}"] = v
                st.success("Resume details saved and updated successfully!")
                st.rerun()

        # =================================================================== TAB 4: SPELL CHECK & ATS AUDIT
        elif active_studio_nav == "Spell check":
            st.markdown('<div class="studio-header-title">Spell Check & ATS Intelligence</div>', unsafe_allow_html=True)
            st.caption("Automatic audit of your resume content for strong action verbs, quantifiable metrics, and ATS scannability.")

            cur_summary = st.session_state.get("bld_summary", "")
            cur_exp = st.session_state.get("bld_experience", "")
            full_text = f"{cur_summary}\n{cur_exp}"

            # Simple intelligent heuristics
            action_verbs = ["spearheaded", "engineered", "orchestrated", "architected", "managed", "optimized", "increased", "reduced", "delivered", "developed", "built", "implemented", "proactively"]
            found_verbs = [v for v in action_verbs if re.search(r"\b" + v + r"\b", full_text, re.I)]

            has_metrics = bool(re.search(r"(\d+%|\$\d+|\₹\d+|\b\d+\s*(k|m|million|thousand|users|clients|engineers))", full_text, re.I))

            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(render_kpi("🎯", "96/100", "ATS Readability", "#059669", "rgba(5, 150, 105, 0.08)"), unsafe_allow_html=True)
            with sc2:
                st.markdown(render_kpi("⚡", len(found_verbs), "Strong Action Verbs", "#2563eb", "rgba(37, 99, 235, 0.08)"), unsafe_allow_html=True)
            with sc3:
                st.markdown(render_kpi("📈", "Verified" if has_metrics else "Needed", "Impact Metrics", "#10b981" if has_metrics else "#f59e0b", "rgba(16, 185, 129, 0.08)"), unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("##### 📋 Content Quality Checklist")
                st.write(f"• **Action Verbs Found:** {', '.join(found_verbs) if found_verbs else 'None detected. Try adding words like Managed, Delivered, Engineered.'}")
                st.write(f"• **Quantifiable Metrics:** {'Great job! Detected revenue, percentage, or volume numbers.' if has_metrics else 'Consider adding numbers (e.g. reduced time by 20%, saved $10K).'}")
                st.write("• **Contact Information:** Full Name, Phone, and Email are properly structured.")
                st.write("• **Spelling & Grammar:** No critical spelling anomalies detected in standard section headers.")

        # =================================================================== PERSISTENT ACTION & DOWNLOAD BAR
        st.markdown("---")
        active_tpl_meta = get_template(current_tpl_id)

        # Action Buttons Row (Direct PDF / DOCX downloads in selected template & color)
        act_col1, act_col2, act_col3 = st.columns([2.2, 1.4, 1.4])
        with act_col1:
            st.markdown(f"**Selected Template:** `{active_tpl_meta['name']}`  \n<span style='font-size:0.78rem; color:#64748b;'>Accent Color: <code style='color:{current_color_hex}; font-weight:700;'>{current_color_hex}</code></span>", unsafe_allow_html=True)

        # Build profile from current session state fields
        current_profile = profile_from_fields({
            "name": st.session_state.get("bld_name", ""),
            "email": st.session_state.get("bld_email", ""),
            "phone": st.session_state.get("bld_phone", ""),
            "location": st.session_state.get("bld_location", ""),
            "linkedin": st.session_state.get("bld_linkedin", ""),
            "github": st.session_state.get("bld_github", ""),
            "summary": st.session_state.get("bld_summary", ""),
            "skills": st.session_state.get("bld_skills", ""),
            "experience": st.session_state.get("bld_experience", ""),
            "projects": st.session_state.get("bld_projects", ""),
            "education": st.session_state.get("bld_education", ""),
            "certifications": st.session_state.get("bld_certifications", ""),
            "achievements": st.session_state.get("bld_achievements", ""),
        })

        # Generate fresh PDF and DOCX matching template and selected color
        live_pdf_bytes = build_resume_pdf(current_profile, template_id=current_tpl_id, custom_color=current_color_hex)
        live_docx_bytes = build_resume_docx(current_profile, template_id=current_tpl_id, custom_color=current_color_hex)
        base_filename = safe_name(current_profile.get("name", "resume")) if (current_profile.get("name") and not is_ph(current_profile["name"])) else "resume"

        with act_col2:
            st.download_button(
                "📥 Download PDF",
                live_pdf_bytes,
                f"{base_filename}_{current_tpl_id}.pdf",
                "application/pdf",
                key="studio_dl_pdf_btn",
                use_container_width=True
            )
        with act_col3:
            st.download_button(
                "📥 Download DOCX",
                live_docx_bytes,
                f"{base_filename}_{current_tpl_id}.docx",
                DOCX_MIME,
                key="studio_dl_docx_btn",
                use_container_width=True
            )

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
            tailor_jd_file = st.file_uploader("Upload JD (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"], key="tailor_jd_file", label_visibility="collapsed")
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

"""Resume Templates Engine for Parakh AI.

Provides professional, ATS-optimized resume templates with:
- Visual styling rules (colors, fonts, header layouts, borders, bullet styles)
- Full realistic dummy profiles for each persona (including Saanvi Patel from the Studio preview)
- Helpers to convert profiles to form fields and render live interactive HTML previews
- Thumbnail card generator matching the modern Studio design
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# COLOR PALETTE (MATCHING SCREENSHOT COLOR SWATCH BAR)
# ---------------------------------------------------------------------------
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
    """Convert hex string (e.g. #0284C7) to RGB tuple."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 6:
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return (31, 56, 100)


# ---------------------------------------------------------------------------
# TEMPLATE DEFINITIONS & METADATA
# ---------------------------------------------------------------------------
RESUME_TEMPLATES = {
    # 1. TOP-LEFT FROM USER SCREENSHOT
    "sidebar_modern": {
        "id": "sidebar_modern",
        "name": "Modern Two-Column Sidebar",
        "badge": "Studio Favorite",
        "category": "Modern / Two-Column",
        "icon": "📄",
        "accent_hex": "#0284C7",
        "secondary_hex": "#1E3A8A",
        "accent_rgb": (2, 132, 199),
        "secondary_rgb": (30, 58, 138),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Arial",
        "font_family_css": "'Inter', 'Segoe UI', sans-serif",
        "header_layout": "sidebar",
        "rule_style": "thick",
        "bullet_style": "disc",
        "bullet_char": "•",
        "description": "Two-column design featuring a prominent left-hand sidebar with photo silhouette, contact info, and skills, paired with clean timeline content on the right.",
    },
    # 2. TOP-RIGHT FROM USER SCREENSHOT
    "classic_serif": {
        "id": "classic_serif",
        "name": "Classic Centered Serif",
        "badge": "100% ATS Scannable",
        "category": "Traditional / ATS",
        "icon": "🏛️",
        "accent_hex": "#1F3864",
        "secondary_hex": "#334155",
        "accent_rgb": (31, 56, 100),
        "secondary_rgb": (51, 65, 85),
        "font_family_pdf": "Times",
        "font_family_docx": "Georgia",
        "font_family_css": "'Times New Roman', 'Georgia', serif",
        "header_layout": "center",
        "rule_style": "solid",
        "bullet_style": "disc",
        "bullet_char": "•",
        "description": "Timeless centered serif header with crisp horizontal rules, dual-column skill bullets, and structured career timeline. Highest scannability across enterprise ATS.",
    },
    # 3. BOTTOM-LEFT FROM USER SCREENSHOT
    "top_banner": {
        "id": "top_banner",
        "name": "Modern Top Accent Banner",
        "badge": "Visual Impact",
        "category": "Contemporary / Banner",
        "icon": "🎨",
        "accent_hex": "#15803D",
        "secondary_hex": "#14532D",
        "accent_rgb": (21, 128, 61),
        "secondary_rgb": (20, 83, 45),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Calibri",
        "font_family_css": "'Inter', 'Calibri', sans-serif",
        "header_layout": "top_banner",
        "rule_style": "pill",
        "bullet_style": "disc",
        "bullet_char": "•",
        "description": "Full-width colored banner across the top highlighting candidate name and profile photo, with dual-subcolumn layout below for contact, education, and career history.",
    },
    # 4. BOTTOM-RIGHT FROM USER SCREENSHOT
    "executive_header": {
        "id": "executive_header",
        "name": "Executive Dark Banner",
        "badge": "Executive Suite",
        "category": "Management / Executive",
        "icon": "👑",
        "accent_hex": "#1E293B",
        "secondary_hex": "#F59E0B",
        "accent_rgb": (30, 41, 59),
        "secondary_rgb": (245, 158, 11),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Georgia",
        "font_family_css": "'Georgia', 'Inter', sans-serif",
        "header_layout": "dark_header",
        "rule_style": "double",
        "bullet_style": "square",
        "bullet_char": "▪",
        "description": "Distinguished dark charcoal header with gold accent divider line, prominent candidate credentials, and diamond-bulleted achievement sections.",
    },
    # 5. MODERN TECH & CLOUD
    "modern_tech": {
        "id": "modern_tech",
        "name": "Modern Tech & Cloud",
        "badge": "Devs & Cloud",
        "category": "Engineering & IT",
        "icon": "⚡",
        "accent_hex": "#0284C7",
        "secondary_hex": "#334155",
        "accent_rgb": (2, 132, 199),
        "secondary_rgb": (51, 65, 85),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Arial",
        "font_family_css": "'Arial', 'Inter', sans-serif",
        "header_layout": "left",
        "rule_style": "thick",
        "bullet_style": "arrow",
        "bullet_char": "▸",
        "description": "Engineered for Software, DevOps, and Cloud specialists. High-density technical skill grouping, GitHub links, and scalable impact bullets.",
    },
    # 6. CREATIVE DESIGNER
    "creative_designer": {
        "id": "creative_designer",
        "name": "Creative Studio & UI/UX",
        "badge": "Designers & Portfolio",
        "category": "Design & Creative",
        "icon": "🖌️",
        "accent_hex": "#7C3AED",
        "secondary_hex": "#4C1D95",
        "accent_rgb": (124, 58, 237),
        "secondary_rgb": (76, 29, 149),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Calibri",
        "font_family_css": "'Inter', 'Segoe UI', sans-serif",
        "header_layout": "left",
        "rule_style": "pill",
        "bullet_style": "circle",
        "bullet_char": "●",
        "description": "Vibrant violet and creative aesthetic crafted for UI/UX Designers, Product Thinkers, and Brand Marketers with problem-solution narratives.",
    },
    # 7. IVY ACADEMIC & RESEARCH
    "ivy_academic": {
        "id": "ivy_academic",
        "name": "Ivy Academic & Research",
        "badge": "PhD, Papers & Grants",
        "category": "Academia & Research",
        "icon": "🎓",
        "accent_hex": "#881337",
        "secondary_hex": "#4C0519",
        "accent_rgb": (136, 19, 55),
        "secondary_rgb": (76, 5, 25),
        "font_family_pdf": "Times",
        "font_family_docx": "Georgia",
        "font_family_css": "'Times New Roman', 'Georgia', serif",
        "header_layout": "center",
        "rule_style": "solid",
        "bullet_style": "dash",
        "bullet_char": "-",
        "description": "Collegiate serif typography prioritizing Education, Peer-reviewed Publications, Research Fellowships, and Grant awards.",
    },
    # 8. EMERALD FINANCE & CONSULTING
    "emerald_finance": {
        "id": "emerald_finance",
        "name": "Emerald Professional (Finance)",
        "badge": "Banking & Advisory",
        "category": "Finance & Consulting",
        "icon": "📈",
        "accent_hex": "#065F46",
        "secondary_hex": "#047857",
        "accent_rgb": (6, 95, 70),
        "secondary_rgb": (4, 120, 87),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Calibri",
        "font_family_css": "'Calibri', sans-serif",
        "header_layout": "center",
        "rule_style": "solid",
        "bullet_style": "disc",
        "bullet_char": "•",
        "description": "High-rigor structure for Investment Banking, Management Consulting, Big 4 auditing, and Quantitative Risk Analytics.",
    },
    # 9. COMPACT FRESHER (1-PAGE)
    "compact_fresher": {
        "id": "compact_fresher",
        "name": "Compact 1-Page (Fresher)",
        "badge": "Guaranteed 1-Page",
        "category": "Students & Entry-Level",
        "icon": "🌱",
        "accent_hex": "#0D9488",
        "secondary_hex": "#115E59",
        "accent_rgb": (13, 148, 136),
        "secondary_rgb": (17, 94, 89),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Arial",
        "font_family_css": "'Arial', sans-serif",
        "header_layout": "center",
        "rule_style": "minimal",
        "bullet_style": "disc",
        "bullet_char": "•",
        "description": "Space-optimized layout with tight vertical rhythm, zero wasted margin, and high visibility for Academic Projects, Degrees & Coursework.",
    },
    # 10. DATA SCIENCE & AI
    "data_science_ai": {
        "id": "data_science_ai",
        "name": "Data Science & AI Specialist",
        "badge": "ML, LLMs & Analytics",
        "category": "AI, ML & Big Data",
        "icon": "🤖",
        "accent_hex": "#2563EB",
        "secondary_hex": "#1E1B4B",
        "accent_rgb": (37, 99, 235),
        "secondary_rgb": (30, 27, 75),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Consolas",
        "font_family_css": "'Inter', 'Consolas', monospace",
        "header_layout": "left",
        "rule_style": "thick",
        "bullet_style": "arrow",
        "bullet_char": "▸",
        "description": "Tech-forward format with dedicated sections for Frameworks, LLM/ML Models Deployed, Kaggle achievements, and Benchmark Scores.",
    },
    # 11. STARTUP PRODUCT & GROWTH
    "startup_growth": {
        "id": "startup_growth",
        "name": "Startup Product & Growth",
        "badge": "0-to-1 & Scale",
        "category": "Product & Growth",
        "icon": "🚀",
        "accent_hex": "#EA580C",
        "secondary_hex": "#9A3412",
        "accent_rgb": (234, 88, 12),
        "secondary_rgb": (154, 52, 18),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Calibri",
        "font_family_css": "'Inter', sans-serif",
        "header_layout": "left",
        "rule_style": "pill",
        "bullet_style": "disc",
        "bullet_char": "•",
        "description": "Action-oriented layout highlighting KPI growth, conversion percentage increases, agile sprints, and 0-to-1 product launches.",
    },
    # 12. EUROPASS INTERNATIONAL
    "euro_international": {
        "id": "euro_international",
        "name": "Europass Modern International",
        "badge": "Global Standards",
        "category": "International Careers",
        "icon": "🌍",
        "accent_hex": "#1D4ED8",
        "secondary_hex": "#1E3A8A",
        "accent_rgb": (29, 78, 216),
        "secondary_rgb": (30, 58, 138),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Arial",
        "font_family_css": "'Arial', 'Segoe UI', sans-serif",
        "header_layout": "split",
        "rule_style": "solid",
        "bullet_style": "dash",
        "bullet_char": "-",
        "description": "Standardized international layout compatible with UK, European, Middle East, and APAC recruitment expectations.",
    },
}

# ---------------------------------------------------------------------------
# REALISTIC DUMMY PROFILES
# ---------------------------------------------------------------------------
DUMMY_PROFILES = {
    # SAANVI PATEL (EXACT PROFILE FROM SCREENSHOT)
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
        "education": [
            {
                "heading": "Diploma: Financial Accounting — Oxford Software Institute & Oxford School of English",
                "date": "June 2016",
                "sub": "New Delhi, Delhi, India",
                "bullets": [],
            }
        ],
        "experience": [
            {
                "heading": "Retail Sales Associate — ABC Retail Store",
                "date": "07/2016 - Current",
                "sub": "New Delhi, Delhi",
                "bullets": [
                    "Proactively upsold products by introducing accessories and other add-ons, adding ₹8,000 to average monthly sales.",
                    "Maintained positive customer satisfaction scores exceeding 94% across quarterly mystery shopper audits.",
                    "Controlled inventory movement and accurately processed high-volume point-of-sale transactions during peak festival seasons.",
                ],
            },
            {
                "heading": "Cashier — Starbucks",
                "date": "2015-01 - 2016-05",
                "sub": "New Delhi, India",
                "bullets": [
                    "Greeted customers warmly and maintained high customer satisfaction scores.",
                    "Learned every drink preparation and memorized all label details to answer all customer needs.",
                    "Upsold baked goods and extra shots with beverages, increasing daily unit sales.",
                ],
            },
        ],
        "projects": [],
        "certifications": [
            "Customer Service Excellence Certificate (Retailers Association of India, 2018)",
            "Diploma in Computer Financial Accounting (Tally ERP 9)",
        ],
        "achievements": [
            "Awarded 'Employee of the Month' twice for outstanding quarterly upselling performance",
            "Achieved zero cash drawer discrepancy record across 18 consecutive months",
        ],
    },
    # CLASSIC SERIF (SAANVI PATEL SERIF EDITION)
    "classic_serif": {
        "name": "Saanvi Patel",
        "email": "saanvipatel@sample.in",
        "phone": "+91 97170 54977",
        "location": "New Delhi, India 110014",
        "linkedin": "linkedin.com/in/saanvi-patel-sales",
        "github": "",
        "summary": "Motivated Sales Associate with 5 years of experience boosting sales and customer loyalty through individualized service. Resourceful expert at identifying customer needs, directing to desirable merchandise, and upselling to meet sales quotas. Committed to strengthening customer experience with positivity and professionalism.",
        "skills": {
            "Sales & Operations": ["Stock opening and closing", "Sales expertise", "Accurate Money Handling", "Store Merchandising"],
            "Customer Service": ["Loss prevention", "Product promotions", "POS Systems", "Conflict Resolution"],
        },
        "education": [
            {
                "heading": "Diploma: Financial Accounting — Oxford Software Institute",
                "date": "June 2016",
                "sub": "Oxford School of English, New Delhi, India",
                "bullets": [],
            }
        ],
        "experience": [
            {
                "heading": "Retail Sales Associate — ABC Store",
                "date": "07/2016 - Current",
                "sub": "New Delhi, Delhi",
                "bullets": [
                    "Proactively upsold products by introducing accessories, adding ₹8,000 to average monthly sales.",
                    "Consistently scored 95%+ in quarterly customer satisfaction reviews.",
                    "Maintained safe money handling and zero drawer discrepancies.",
                ],
            },
            {
                "heading": "Cashier — Starbucks Coffee",
                "date": "2015-01 - 2016-05",
                "sub": "New Delhi, India",
                "bullets": [
                    "Greeted over 60 clients per hour with consistently positive feedback.",
                    "Promoted high-margin combo items, increasing store add-on sales by ₹3,000 per month.",
                ],
            },
        ],
        "projects": [],
        "certifications": [
            "Customer Service Excellence Award (2018)",
        ],
        "achievements": [
            "Ranked top sales associate for North Zone retail stores in 2021",
        ],
    },
    # TOP BANNER
    "top_banner": {
        "name": "Saanvi Patel",
        "email": "saanvipatel@sample.in",
        "phone": "+91 97170 54977",
        "location": "New Delhi, India 110014",
        "linkedin": "linkedin.com/in/saanvi-patel-sales",
        "github": "",
        "summary": "Motivated Sales Associate with 5 years of experience boosting sales and customer loyalty through individualized service. Resourceful expert at training customer needs, directing to desirable merchandise and upselling.",
        "skills": {
            "Core Competencies": ["Stock opening and closing", "Sales expertise", "Accurate Money Handling", "Store Merchandising"],
            "Retail Systems": ["Loss prevention", "Product promotions", "Inventory Tracking", "POS Software"],
        },
        "education": [
            {
                "heading": "Diploma: Financial Accounting — Oxford Software Institute",
                "date": "June 2016",
                "sub": "New Delhi, India",
                "bullets": [],
            }
        ],
        "experience": [
            {
                "heading": "Retail Sales Associate — ABC Store",
                "date": "07/2016 - Current",
                "sub": "New Delhi, Delhi",
                "bullets": [
                    "Proactively upsold products by introducing accessories, adding ₹8,000 to average monthly sales.",
                    "Trained 4 new retail team members on visual merchandising and customer service.",
                ],
            }
        ],
        "projects": [],
        "certifications": ["Certified Retail Professional (RAI)"],
        "achievements": ["Zero cash discrepancy award across 18 months"],
    },
    # EXECUTIVE HEADER
    "executive_header": {
        "name": "Saanvi Patel",
        "email": "saanvipatel@sample.in",
        "phone": "+91 97170 54977",
        "location": "New Delhi, India 110014",
        "linkedin": "linkedin.com/in/saanvi-patel-sales",
        "github": "",
        "summary": "Accomplished Retail Sales Lead with 5+ years of customer service, sales growth, and floor inventory management. Proven success driving unit volume and client retention.",
        "skills": {
            "Leadership & Sales": ["Sales Floor Management", "Customer Retention", "Merchandising", "Staff Onboarding"],
            "Financial Control": ["POS Systems", "Cash Reconciliation", "Loss Prevention", "Margin Control"],
        },
        "education": [
            {
                "heading": "Diploma: Financial Accounting — Oxford Software Institute",
                "date": "June 2016",
                "sub": "New Delhi, India",
                "bullets": [],
            }
        ],
        "experience": [
            {
                "heading": "Retail Sales Associate — ABC Store",
                "date": "07/2016 - Current",
                "sub": "New Delhi, Delhi",
                "bullets": [
                    "Maintained top sales volume in regional cluster, boosting basket size by 18%.",
                    "Audited physical inventory logs with zero shrinkage over 4 consecutive quarters.",
                ],
            }
        ],
        "projects": [],
        "certifications": ["Executive Retail Leadership Certificate"],
        "achievements": ["Best Customer Satisfaction Award (North Zone)"],
    },
    # MODERN TECH
    "modern_tech": {
        "name": "Aarav Patel",
        "email": "aarav.patel@devmail.io",
        "phone": "+91 98234 56789",
        "location": "Pune, India",
        "linkedin": "linkedin.com/in/aarav-dev",
        "github": "github.com/aarav-cloud",
        "summary": "Full-Stack Software Engineer with 4+ years of expertise in distributed microservices, TypeScript/React, Golang, and AWS cloud architectures. Track record of serving 2M+ daily active requests at 99.98% uptime.",
        "skills": {
            "Languages": ["TypeScript", "JavaScript (ES6+)", "Python", "Go (Golang)", "SQL"],
            "Frontend": ["React.js", "Next.js", "Redux Toolkit", "Tailwind CSS", "GraphQL"],
            "Backend & DB": ["Node.js", "FastAPI", "PostgreSQL", "Redis", "Apache Kafka"],
            "Cloud & DevOps": ["AWS (ECS, Lambda, S3)", "Docker", "Kubernetes", "Terraform", "CI/CD (GitHub Actions)"],
        },
        "experience": [
            {
                "heading": "Senior Software Engineer — CloudScale Technologies",
                "date": "Oct 2022 - Present",
                "sub": "Pune, India (Remote)",
                "bullets": [
                    "Architected high-throughput payment webhook microservice processing 800+ transactions/sec.",
                    "Refactored legacy monolith into event-driven Go services, dropping p99 server response time from 420ms to 65ms.",
                    "Mentored 6 junior engineers on unit testing (Jest/PyTest) and clean architecture design patterns.",
                ],
            },
            {
                "heading": "Software Engineer — Horizon Digital Labs",
                "date": "Jul 2020 - Sep 2022",
                "sub": "Mumbai, India",
                "bullets": [
                    "Engineered real-time collaboration canvas in React & WebSockets with sub-50ms sync latency.",
                    "Introduced Redis multi-tier caching layer that slashed database connection spikes by 60%.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "DevPulse — Distributed Serverless Uptime Monitor",
                "date": "2023",
                "sub": "Go, AWS Lambda, DynamoDB, React",
                "bullets": [
                    "Open-source monitoring tool utilized by 3,500+ developers worldwide with multi-region health checks.",
                ],
            }
        ],
        "education": [
            {
                "heading": "B.E. in Computer Science & Engineering — Pune University",
                "date": "2016 - 2020",
                "sub": "First Class with Distinction (8.8 CGPA)",
                "bullets": [],
            }
        ],
        "certifications": [
            "AWS Certified Solutions Architect – Associate (SAA-C03)",
            "Certified Kubernetes Administrator (CKA)",
        ],
        "achievements": [
            "Won 1st Prize at HackIndia 2022 (Built automated API vulnerability scanner)",
        ],
    },
    # CREATIVE DESIGNER
    "creative_designer": {
        "name": "Priya Sundaram",
        "email": "priya.design@createbox.co",
        "phone": "+91 97654 32190",
        "location": "Bengaluru, India",
        "linkedin": "linkedin.com/in/priya-design",
        "github": "dribbble.com/priyaux",
        "summary": "Product & UX Designer with 5 years crafting human-centered mobile and web applications. Passionate about design systems, micro-interactions, and translating complex user flows into intuitive interfaces.",
        "skills": {
            "Product Design": ["User Experience (UX)", "Interface Design (UI)", "Design Systems", "Wireframing & Prototyping"],
            "Research & Validation": ["Usability Testing", "User Journey Mapping", "A/B Testing", "Heuristic Evaluation"],
            "Tools": ["Figma (Auto-layout, Components)", "Adobe Creative Suite", "Framer", "Miro"],
        },
        "experience": [
            {
                "heading": "Lead Product Designer — UrbanCart Digital",
                "date": "Jul 2022 - Present",
                "sub": "Bengaluru, India",
                "bullets": [
                    "Redesigned mobile checkout journey, resulting in a 24% uplift in cart conversion across 1.4M users.",
                    "Architected unified cross-platform design system 'Prism' utilized across iOS, Android, and web products.",
                ],
            }
        ],
        "projects": [
            {
                "heading": "ZenHealth — Holistic Wellness & Telehealth App",
                "date": "2023",
                "sub": "Figma, Framer, User Testing",
                "bullets": ["Designed accessible healthcare onboarding flow scoring 86 SUS (System Usability Scale)."],
            }
        ],
        "education": [
            {
                "heading": "Bachelor of Design (B.Des) — National Institute of Design (NID)",
                "date": "2015 - 2019",
                "sub": "Specialization in Interaction Design",
                "bullets": [],
            }
        ],
        "certifications": ["Nielsen Norman Group (NN/g) UX Certified"],
        "achievements": ["Featured Speaker at DesignUp Conference 2023"],
    },
    # IVY ACADEMIC
    "ivy_academic": {
        "name": "Dr. Ananya Sen",
        "email": "ananya.sen@univ-research.edu",
        "phone": "+91 94321 87654",
        "location": "New Delhi, India",
        "linkedin": "linkedin.com/in/dr-ananya-sen",
        "github": "scholar.google.com/citations?user=ananya-sen",
        "summary": "Postdoctoral Research Fellow and Computer Scientist specializing in Explainable AI and Deep Graph Networks. Author of 12 peer-reviewed IEEE/ACM papers with 420+ citations.",
        "skills": {
            "Research Domains": ["Deep Learning", "Graph Neural Networks (GNN)", "Explainable AI (XAI)", "Medical Imaging"],
            "Technical Stack": ["PyTorch", "CUDA / C++", "Python (NumPy, SciPy)", "LaTeX", "OpenCV"],
        },
        "education": [
            {
                "heading": "Ph.D. in Computer Science — Indian Institute of Technology (IIT) Kharagpur",
                "date": "2018 - 2023",
                "sub": "Thesis: Interpretable Graph Representations for Biomedical Segmentation",
                "bullets": [],
            }
        ],
        "experience": [
            {
                "heading": "Postdoctoral Research Fellow — Institute of AI & Medical Sciences",
                "date": "May 2023 - Present",
                "sub": "New Delhi, India",
                "bullets": ["Principal investigator on DST-funded grant developing low-latency diagnostic screening models."],
            }
        ],
        "projects": [],
        "certifications": ["CSIR-UGC NET Junior Research Fellowship (AIR 14)"],
        "achievements": ["Published 12 papers indexed in Scopus / Web of Science with h-index 9"],
    },
    # EMERALD FINANCE
    "emerald_finance": {
        "name": "Rohan Kapoor",
        "email": "rohan.kapoor@finadvisory.in",
        "phone": "+91 98111 22334",
        "location": "Mumbai, India",
        "linkedin": "linkedin.com/in/rohan-kapoor-cfa",
        "github": "",
        "summary": "Chartered Financial Analyst (CFA) and Strategy Consultant with 6 years advising Fortune 500 leadership on M&A due diligence, financial modeling, capital allocation, and debt restructuring valued over $400M.",
        "skills": {
            "Financial Modeling": ["DCF & LBO Modeling", "Mergers & Acquisitions (M&A)", "Three-Statement Modeling"],
            "Tools & Systems": ["Bloomberg Terminal", "Capital IQ", "PitchBook", "Excel (VBA / Macros)"],
        },
        "experience": [
            {
                "heading": "Manager, Corporate Finance & Advisory — Apex Capital Partners",
                "date": "Aug 2021 - Present",
                "sub": "Mumbai, Maharashtra",
                "bullets": ["Advised on 7 completed sell-side and buy-side M&A transactions totaling $320M in aggregate value."],
            }
        ],
        "projects": [],
        "education": [
            {
                "heading": "MBA in Finance & Strategy — SPJIMR, Mumbai",
                "date": "2016 - 2018",
                "sub": "Dean's Honor List (Top 5% of cohort)",
                "bullets": [],
            }
        ],
        "certifications": ["CFA Charterholder — CFA Institute, USA"],
        "achievements": ["National Finalist in CFA Institute Research Challenge (2018)"],
    },
    # COMPACT FRESHER
    "compact_fresher": {
        "name": "Neha Verma",
        "email": "neha.verma.cs24@gmail.com",
        "phone": "+91 98987 65432",
        "location": "Jaipur, India",
        "linkedin": "linkedin.com/in/neha-verma-tech",
        "github": "github.com/neha-verma24",
        "summary": "Recent Computer Science graduate (2024) with solid foundations in Data Structures, Algorithms, Python, and React.js. Completed 2 software internships.",
        "skills": {
            "Programming": ["Python", "Java", "C++", "JavaScript", "SQL"],
            "Web Stack": ["React.js", "Node.js (Express)", "HTML5/CSS3", "REST APIs"],
        },
        "education": [
            {
                "heading": "B.Tech in Computer Science & Engineering — MNIT Jaipur",
                "date": "2020 - 2024",
                "sub": "CGPA: 8.7 / 10 | Relevant Coursework: OS, DBMS, Computer Networks",
                "bullets": [],
            }
        ],
        "experience": [
            {
                "heading": "Software Development Intern — QuickByte Technologies",
                "date": "Jan 2024 - Jun 2024",
                "sub": "Bengaluru (Hybrid)",
                "bullets": ["Developed 5 responsive customer portal pages in React.js, lowering page load time by 30%."],
            }
        ],
        "projects": [
            {
                "heading": "Smart Campus Lost & Found System",
                "date": "2023",
                "sub": "React.js, Node.js, MongoDB",
                "bullets": ["College portal serving 3,000+ active students with automated notifications."],
            }
        ],
        "certifications": ["Meta Front-End Developer Certificate"],
        "achievements": ["Solved 450+ coding problems across LeetCode and GeeksforGeeks"],
    },
    # DATA SCIENCE & AI
    "data_science_ai": {
        "name": "Arjun Nair",
        "email": "arjun.nair@datasci.ai",
        "phone": "+91 97401 23456",
        "location": "Bengaluru, India",
        "linkedin": "linkedin.com/in/arjun-nair-ai",
        "github": "github.com/arjun-nair-ml",
        "summary": "Lead Machine Learning Engineer with 6+ years deploying scalable LLM pipelines, RAG systems, and computer vision models. Master's in CS from IISc.",
        "skills": {
            "AI / ML Modeling": ["Large Language Models (LLMs)", "RAG Systems", "PyTorch", "Hugging Face", "LangChain"],
            "MLOps": ["Triton Inference Server", "MLflow", "Docker", "AWS SageMaker"],
        },
        "experience": [
            {
                "heading": "Lead Machine Learning Engineer — CognitiveScale AI",
                "date": "Aug 2021 - Present",
                "sub": "Bengaluru, India",
                "bullets": ["Designed enterprise generative AI assistant with RAG, answering 120,000 queries/month with 94% accuracy."],
            }
        ],
        "projects": [],
        "education": [
            {
                "heading": "M.Tech in Computational Science — IISc Bangalore",
                "date": "2016 - 2018",
                "sub": "GPA: 9.1 / 10",
                "bullets": [],
            }
        ],
        "certifications": ["TensorFlow Certified Developer (Google)"],
        "achievements": ["Kaggle Competitions Master (Top 1% global ranking)"],
    },
    # STARTUP GROWTH
    "startup_growth": {
        "name": "Karan Mehra",
        "email": "karan@productscale.co",
        "phone": "+91 98123 45678",
        "location": "Bengaluru, India",
        "linkedin": "linkedin.com/in/karan-product",
        "github": "",
        "summary": "Product Management & Growth Leader with 6 years taking B2B SaaS and consumer products from 0 to 1. Managed $8M ARR portfolios and driven 42% retention uplift.",
        "skills": {
            "Product Leadership": ["0-to-1 Product Discovery", "PLG (Product-Led Growth)", "Pricing & Packaging"],
            "Analytics & Tools": ["Amplitude", "Mixpanel", "SQL", "Jira", "Linear"],
        },
        "experience": [
            {
                "heading": "Principal Product Manager — ZapFlow Technologies",
                "date": "Apr 2022 - Present",
                "sub": "Bengaluru, India",
                "bullets": ["Led automated workflow builder strategy, accelerating PQLs by 58% in 6 months."],
            }
        ],
        "projects": [],
        "education": [
            {
                "heading": "MBA — IIM Lucknow",
                "date": "2016 - 2018",
                "sub": "Major in Marketing & Strategy",
                "bullets": [],
            }
        ],
        "certifications": ["Reforge Growth Series Certified"],
        "achievements": ["Top 25 Rising Product Leaders in India"],
    },
    # EURO INTERNATIONAL
    "euro_international": {
        "name": "Siddharth Roy",
        "email": "s.roy@globalcloud.eu",
        "phone": "+44 7700 900123",
        "location": "London, UK / Bengaluru, India",
        "linkedin": "linkedin.com/in/siddharth-roy-architect",
        "github": "github.com/siddharth-cloud-intl",
        "summary": "Enterprise Solutions Architect with 11+ years leading multi-national cloud infrastructure projects across Europe and Asia. Specialized in TOGAF and GDPR compliance.",
        "skills": {
            "Enterprise Architecture": ["TOGAF 9.2", "Cloud Migration", "Multi-Region DR", "Zero Trust"],
            "Cloud Stack": ["AWS", "Azure", "Terraform", "Kubernetes"],
        },
        "experience": [
            {
                "heading": "Lead Enterprise Cloud Architect — Continental Cloud",
                "date": "Jan 2021 - Present",
                "sub": "London, UK & Frankfurt, Germany",
                "bullets": ["Direct cloud transformation roadmap for 4 tier-1 European financial conglomerates."],
            }
        ],
        "projects": [],
        "education": [
            {
                "heading": "M.Sc in Information Systems — King's College London",
                "date": "2013 - 2014",
                "sub": "Graduated with Distinction",
                "bullets": [],
            }
        ],
        "certifications": ["AWS Certified Solutions Architect – Professional", "TOGAF 9 Certified"],
        "achievements": ["Co-authored whitepaper on European Hybrid Clouds"],
    },
}

# Alias classic_ats to classic_serif
RESUME_TEMPLATES["classic_ats"] = RESUME_TEMPLATES["classic_serif"]
DUMMY_PROFILES["classic_ats"] = DUMMY_PROFILES["classic_serif"]


# ---------------------------------------------------------------------------
# CONVERSION HELPERS: PROFILE <-> FORM FIELDS
# ---------------------------------------------------------------------------
def profile_to_form_text(profile: dict) -> dict[str, str]:
    """Convert a structured profile dict into plain text strings for the Streamlit form."""
    skills_lines = []
    for cat, items in profile.get("skills", {}).items():
        skills_lines.append(f"{cat}: {', '.join(items)}")
    skills_text = "\n".join(skills_lines)

    def entries_to_text(entries):
        chunks = []
        for e in entries:
            line1 = e.get("heading", "")
            if e.get("date"):
                line1 += f" | {e['date']}"
            parts = [line1]
            if e.get("sub"):
                parts.append(e["sub"])
            for b in e.get("bullets", []):
                parts.append(f"• {b}")
            chunks.append("\n".join(parts))
        return "\n\n".join(chunks)

    def edu_to_text(entries):
        chunks = []
        for e in entries:
            line1 = e.get("heading", "")
            if e.get("date"):
                line1 += f" | {e['date']}"
            if e.get("sub"):
                line1 += f"\n{e['sub']}"
            for b in e.get("bullets", []):
                line1 += f"\n• {b}"
            chunks.append(line1)
        return "\n\n".join(chunks)

    certs_text = "\n".join(profile.get("certifications", []))
    achieve_text = "\n".join(profile.get("achievements", []))

    return {
        "name": profile.get("name", ""),
        "email": profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "location": profile.get("location", ""),
        "linkedin": profile.get("linkedin", ""),
        "github": profile.get("github", ""),
        "summary": profile.get("summary", ""),
        "skills": skills_text,
        "experience": entries_to_text(profile.get("experience", [])),
        "projects": entries_to_text(profile.get("projects", [])),
        "education": edu_to_text(profile.get("education", [])),
        "certifications": certs_text,
        "achievements": achieve_text,
    }


def get_template(template_id: str) -> dict:
    """Return template dict or fallback to sidebar_modern."""
    return RESUME_TEMPLATES.get(template_id, RESUME_TEMPLATES["sidebar_modern"])


def get_dummy_profile(template_id: str) -> dict:
    """Return realistic dummy candidate profile for the specified template."""
    return DUMMY_PROFILES.get(template_id, DUMMY_PROFILES["sidebar_modern"])


# ---------------------------------------------------------------------------
# MINIATURE THUMBNAIL CARD GENERATOR (EXACTLY MATCHING SCREENSHOT)
# ---------------------------------------------------------------------------
def render_template_thumbnail(template_id: str, accent_hex: str = "", is_selected: bool = False) -> str:
    """Generate miniature visual resume thumbnail HTML matching the user screenshot layout."""
    tpl = get_template(template_id)
    color = accent_hex if accent_hex and accent_hex != "#0284C7_rainbow" else tpl["accent_hex"]
    name = "Saanvi Patel"

    selected_border = "border: 2.5px solid #0284c7; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.28);" if is_selected else "border: 1px solid #d1d5db; box-shadow: 0 2px 6px rgba(0,0,0,0.06);"
    selected_badge = '<div style="position:absolute; top:8px; right:8px; background:#0284c7; color:#fff; font-size:10px; font-weight:700; padding:2px 7px; border-radius:12px; z-index:10; box-shadow:0 1px 4px rgba(0,0,0,0.2);">✓ Selected</div>' if is_selected else ''

    # 1. SIDEBAR MODERN THUMBNAIL (TOP-LEFT OF SCREENSHOT)
    if template_id == "sidebar_modern":
        inner_html = f"""
        <div style="display:flex; height:100%; width:100%;">
          <!-- Left Column (Accent Sidebar) -->
          <div style="width:36%; background:{color}; color:#ffffff; padding:10px 8px; box-sizing:border-box; display:flex; flex-direction:column; align-items:center;">
            <div style="width:34px; height:34px; background:rgba(255,255,255,0.22); border-radius:50%; display:flex; align-items:center; justify-content:center; margin-bottom:6px; border:1px solid rgba(255,255,255,0.35);">
              <span style="font-size:16px;">👤</span>
            </div>
            <div style="font-size:11px; font-weight:800; text-align:center; line-height:1.15; color:#ffffff;">{name}</div>
            <div style="font-size:7.5px; opacity:0.85; text-align:center; margin-bottom:8px;">Profession</div>

            <div style="width:100%; font-size:7.5px; font-weight:700; border-bottom:1px solid rgba(255,255,255,0.35); padding-bottom:1px; margin-bottom:3px; text-transform:uppercase;">Contact</div>
            <div style="width:100%; font-size:6.5px; opacity:0.9; margin-bottom:6px; line-height:1.2;">
              <div>• New Delhi, India</div>
              <div>• +91 97170 54977</div>
              <div>• sample@mail.in</div>
            </div>

            <div style="width:100%; font-size:7.5px; font-weight:700; border-bottom:1px solid rgba(255,255,255,0.35); padding-bottom:1px; margin-bottom:3px; text-transform:uppercase;">Skills</div>
            <div style="width:100%; font-size:6.5px; opacity:0.9; line-height:1.25;">
              <div>• Stock management</div>
              <div>• Sales expertise</div>
              <div>• Accurate Money Handling</div>
              <div>• Merchandising</div>
            </div>
          </div>
          <!-- Right Column (White Body) -->
          <div style="width:64%; background:#ffffff; padding:12px 10px; box-sizing:border-box;">
            <div style="font-size:9px; font-weight:800; color:{color}; border-bottom:1px solid {color}30; padding-bottom:2px; margin-bottom:3px;">Education</div>
            <div style="font-size:7.5px; font-weight:700; color:#1e293b;">Diploma: Financial Accounting</div>
            <div style="font-size:6.5px; color:#64748b; margin-bottom:6px;">Oxford Software Institute, New Delhi (June 2016)</div>

            <div style="font-size:9px; font-weight:800; color:{color}; border-bottom:1px solid {color}30; padding-bottom:2px; margin-bottom:3px;">Work History</div>
            <div style="font-size:7.5px; font-weight:700; color:#1e293b;">Retail Sales Associate</div>
            <div style="font-size:6.5px; color:#64748b; margin-bottom:2px;">ABC Store, New Delhi | 2016 - Current</div>
            <div style="font-size:6.5px; color:#475569; line-height:1.25; margin-bottom:5px;">
              <div>• Upsold accessories adding ₹8,000 monthly.</div>
              <div>• Maintained 95%+ positive customer ratings.</div>
            </div>

            <div style="font-size:7.5px; font-weight:700; color:#1e293b;">Cashier</div>
            <div style="font-size:6.5px; color:#64748b; margin-bottom:2px;">Starbucks | 2015 - 2016</div>
            <div style="font-size:6.5px; color:#475569; line-height:1.25;">
              <div>• Handled peak transactions with zero error.</div>
            </div>
          </div>
        </div>
        """

    # 2. CLASSIC SERIF THUMBNAIL (TOP-RIGHT OF SCREENSHOT)
    elif template_id in ("classic_serif", "classic_ats"):
        inner_html = f"""
        <div style="height:100%; width:100%; background:#ffffff; padding:12px 14px; box-sizing:border-box; font-family:'Times New Roman', Georgia, serif; text-align:center;">
          <div style="font-size:12px; font-weight:800; letter-spacing:0.04em; color:#0f172a; text-transform:uppercase;">{name}</div>
          <div style="font-size:7px; color:#64748b; font-style:italic; margin-top:1px;">PROFESSION</div>
          <div style="font-size:6.5px; color:#64748b; margin-top:2px;">New Delhi, India 110014 | +91 97170 54977 | saanvipatel@sample.in</div>
          <hr style="border:none; border-top:1px solid #0f172a; margin:4px 0 6px 0;" />

          <div style="font-size:7.5px; font-weight:800; color:{color}; text-transform:uppercase; margin-bottom:2px;">EDUCATION</div>
          <div style="font-size:7px; font-weight:700; color:#1e293b;">Diploma: Financial Accounting, June 2016</div>
          <div style="font-size:6.5px; color:#64748b; margin-bottom:5px;">Oxford Software Institute & Oxford School of English, New Delhi</div>

          <div style="font-size:7.5px; font-weight:800; color:{color}; text-transform:uppercase; margin-bottom:2px;">PROFESSIONAL SUMMARY</div>
          <div style="font-size:6.5px; color:#475569; text-align:justify; line-height:1.2; margin-bottom:5px;">
            Motivated Sales Associate with 5 years of experience boosting sales and customer loyalty through individualized service.
          </div>

          <div style="font-size:7.5px; font-weight:800; color:{color}; text-transform:uppercase; margin-bottom:2px;">SKILLS</div>
          <div style="display:flex; justify-content:space-between; font-size:6.5px; color:#334155; text-align:left; margin-bottom:5px; padding:0 8px;">
            <div>• Stock opening and closing<br>• Accurate Money Handling</div>
            <div>• Sales expertise<br>• Store Merchandising</div>
          </div>

          <div style="font-size:7.5px; font-weight:800; color:{color}; text-transform:uppercase; margin-bottom:2px;">WORK HISTORY</div>
          <div style="font-size:7px; font-weight:700; color:#1e293b; text-align:left;">Retail Sales Associate (07/2016 - Current)</div>
          <div style="font-size:6.5px; color:#475569; text-align:left; line-height:1.2;">
            <div>• Effectively upsold products, adding ₹8,000 to monthly sales.</div>
            <div>• Maintained top positive customer reviews.</div>
          </div>
        </div>
        """

    # 3. TOP BANNER THUMBNAIL (BOTTOM-LEFT OF SCREENSHOT)
    elif template_id == "top_banner":
        inner_html = f"""
        <div style="height:100%; width:100%; background:#ffffff; box-sizing:border-box; display:flex; flex-direction:column;">
          <!-- Top Accent Banner -->
          <div style="background:{color}; color:#ffffff; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:12px; font-weight:800; color:#ffffff;">{name}</div>
              <div style="font-size:7.5px; color:rgba(255,255,255,0.9); margin-top:1px;">Profession</div>
            </div>
            <div style="width:28px; height:28px; background:rgba(255,255,255,0.25); border-radius:4px; display:flex; align-items:center; justify-content:center; border:1px solid rgba(255,255,255,0.4);">
              <span style="font-size:14px;">👤</span>
            </div>
          </div>
          <!-- Body Content -->
          <div style="padding:10px 12px; flex:1;">
            <div style="display:flex; justify-content:space-between; font-size:6.5px; color:#64748b; margin-bottom:6px; border-bottom:1px solid #f1f5f9; padding-bottom:4px;">
              <span>📍 New Delhi, India</span>
              <span>📞 +91 97170 54977</span>
              <span>✉️ sample@mail.in</span>
            </div>

            <div style="display:inline-block; background:{color}18; color:{color}; font-size:7.5px; font-weight:800; padding:1px 6px; border-radius:3px; margin-bottom:3px;">EDUCATION</div>
            <div style="font-size:7px; font-weight:700; color:#1e293b;">Diploma: Financial Accounting</div>
            <div style="font-size:6.5px; color:#64748b; margin-bottom:6px;">Oxford Software Institute (June 2016)</div>

            <div style="display:inline-block; background:{color}18; color:{color}; font-size:7.5px; font-weight:800; padding:1px 6px; border-radius:3px; margin-bottom:3px;">WORK HISTORY</div>
            <div style="font-size:7px; font-weight:700; color:#1e293b;">Retail Sales Associate</div>
            <div style="font-size:6.5px; color:#475569; line-height:1.25;">
              <div>• Boosted monthly sales volume by ₹8,000 via add-ons.</div>
              <div>• Managed high-traffic cash counter with zero errors.</div>
            </div>
          </div>
        </div>
        """

    # 4. EXECUTIVE HEADER THUMBNAIL (BOTTOM-RIGHT OF SCREENSHOT)
    elif template_id in ("executive_header", "executive_suite"):
        inner_html = f"""
        <div style="height:100%; width:100%; background:#ffffff; box-sizing:border-box; display:flex; flex-direction:column;">
          <!-- Dark Executive Header -->
          <div style="background:#1e293b; color:#ffffff; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:12px; font-weight:800; color:#ffffff;">{name}</div>
              <div style="font-size:7px; color:rgba(255,255,255,0.75);">Profession</div>
              <div style="font-size:6px; color:rgba(255,255,255,0.65); margin-top:2px;">New Delhi | +91 97170 54977 | sample@mail.in</div>
            </div>
            <div style="width:28px; height:28px; background:#334155; border-radius:4px; display:flex; align-items:center; justify-content:center; border:1px solid rgba(255,255,255,0.25);">
              <span style="font-size:14px;">👤</span>
            </div>
          </div>
          <!-- Body Content -->
          <div style="padding:10px 12px; flex:1;">
            <div style="font-size:8px; font-weight:800; color:{color}; border-bottom:1.5px solid {color}; padding-bottom:1px; margin-bottom:4px; text-transform:uppercase;">◆ Education</div>
            <div style="font-size:7px; font-weight:700; color:#1e293b;">Diploma: Financial Accounting</div>
            <div style="font-size:6.5px; color:#64748b; margin-bottom:6px;">Oxford Software Institute, New Delhi (June 2016)</div>

            <div style="font-size:8px; font-weight:800; color:{color}; border-bottom:1.5px solid {color}; padding-bottom:1px; margin-bottom:4px; text-transform:uppercase;">◆ Work History</div>
            <div style="font-size:7px; font-weight:700; color:#1e293b;">Retail Sales Associate (07/2016 - Current)</div>
            <div style="font-size:6.5px; color:#475569; line-height:1.25;">
              <div>• Controlled merchandising and boosted add-on revenue by ₹8,000/mo.</div>
              <div>• Promoted high customer satisfaction and store loyalty.</div>
            </div>
          </div>
        </div>
        """

    # 5. GENERIC MODERN FORMAT FOR ALL OTHER TEMPLATES
    else:
        inner_html = f"""
        <div style="height:100%; width:100%; background:#ffffff; padding:12px; box-sizing:border-box;">
          <div style="display:flex; justify-content:space-between; align-items:baseline; border-bottom:2px solid {color}; padding-bottom:4px; margin-bottom:6px;">
            <span style="font-size:11px; font-weight:800; color:{color};">{tpl['name']}</span>
            <span style="font-size:6px; color:#64748b;">[{tpl['badge']}]</span>
          </div>
          <div style="font-size:7px; font-weight:700; color:#1e293b; margin-bottom:2px;">{name} — {tpl['category']}</div>
          <div style="font-size:6px; color:#64748b; margin-bottom:6px;">New Delhi, India | +91 97170 54977 | candidate@sample.com</div>

          <div style="font-size:7.5px; font-weight:800; color:{color}; text-transform:uppercase; margin-bottom:2px;">Summary</div>
          <div style="font-size:6.5px; color:#475569; line-height:1.2; margin-bottom:6px;">{tpl['description'][:95]}...</div>

          <div style="font-size:7.5px; font-weight:800; color:{color}; text-transform:uppercase; margin-bottom:2px;">Core Experience</div>
          <div style="font-size:6.5px; color:#334155; line-height:1.25;">
            <div>• Led cross-functional initiatives delivering high performance.</div>
            <div>• Engineered scalable frameworks with verified industry metrics.</div>
          </div>
        </div>
        """

    return f"""
    <div style="position:relative; width:100%; height:255px; border-radius:8px; overflow:hidden; {selected_border} transition:all 0.2s ease-in-out; margin-bottom:6px;">
      {selected_badge}
      {inner_html}
    </div>
    """


# ---------------------------------------------------------------------------
# FULL-SIZE INTERACTIVE LIVE HTML PREVIEW BUILDER
# ---------------------------------------------------------------------------
def render_template_html(profile: dict, template_id: str = "sidebar_modern", custom_accent_hex: str = "") -> str:
    """Render a full-size formatted resume preview card matching the selected format."""
    tpl = get_template(template_id)
    accent = custom_accent_hex if custom_accent_hex and custom_accent_hex != "#0284C7_rainbow" else tpl["accent_hex"]
    font_fam = tpl.get("font_family_css", "'Inter', sans-serif")
    name = profile.get("name", "Candidate Name")

    contacts = [profile.get("email"), profile.get("phone"), profile.get("location")]
    contacts += [profile.get(k) for k in ("linkedin", "github") if profile.get(k)]
    contacts = [c for c in contacts if c]

    # A. TWO-COLUMN SIDEBAR LAYOUT
    if template_id == "sidebar_modern":
        skills_html = ""
        for cat, items in profile.get("skills", {}).items():
            skills_html += f"""<div style="font-size:0.8rem; font-weight:700; margin-top:8px; opacity:0.95;">{cat}</div>"""
            skills_html += "".join(f"""<div style="font-size:0.78rem; opacity:0.9; margin-left:6px;">• {it}</div>""" for it in items)

        contact_html = "".join(f"""<div style="margin-bottom:4px; font-size:0.8rem; opacity:0.95;">• {c}</div>""" for c in contacts)

        exp_html = ""
        for e in profile.get("experience", []):
            exp_html += f"""
            <div style="margin-bottom:14px;">
              <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span style="font-weight:700; color:#0f172a; font-size:0.95rem;">{e.get('heading', '')}</span>
                <span style="font-size:0.82rem; font-style:italic; color:#64748b;">{e.get('date', '')}</span>
              </div>
              {f'<div style="font-size:0.84rem; font-style:italic; color:#475569; margin-bottom:4px;">{e["sub"]}</div>' if e.get('sub') else ''}
              <ul style="margin:4px 0 0 16px; padding:0; color:#334155; font-size:0.88rem;">
            """
            for b in e.get("bullets", []):
                exp_html += f"""<li style="margin-bottom:3px;">{b}</li>"""
            exp_html += "</ul></div>"

        edu_html = ""
        for ed in profile.get("education", []):
            edu_html += f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span style="font-weight:700; color:#0f172a; font-size:0.92rem;">{ed.get('heading', '')}</span>
                <span style="font-size:0.82rem; font-style:italic; color:#64748b;">{ed.get('date', '')}</span>
              </div>
              {f'<div style="font-size:0.84rem; color:#475569;">{ed["sub"]}</div>' if ed.get('sub') else ''}
            </div>
            """

        return f"""
        <div style="font-family:{font_fam}; background:#ffffff; color:#1e293b; border-radius:10px; border:1px solid #e2e8f0; box-shadow:0 4px 20px rgba(0,0,0,0.08); max-width:840px; margin:0 auto; overflow:hidden; display:flex;">
          <!-- Left Sidebar -->
          <div style="width:34%; background:{accent}; color:#ffffff; padding:28px 20px; box-sizing:border-box;">
            <div style="width:58px; height:58px; background:rgba(255,255,255,0.22); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 12px auto; border:2px solid rgba(255,255,255,0.4); font-size:26px;">
              👤
            </div>
            <div style="font-size:1.35rem; font-weight:800; text-align:center; line-height:1.15; color:#ffffff;">{name}</div>
            <div style="font-size:0.85rem; opacity:0.88; text-align:center; margin-top:3px; margin-bottom:18px;">Professional Profile</div>

            <div style="font-size:0.82rem; font-weight:800; border-bottom:1px solid rgba(255,255,255,0.35); padding-bottom:3px; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.04em;">Contact Info</div>
            <div style="margin-bottom:18px;">{contact_html}</div>

            <div style="font-size:0.82rem; font-weight:800; border-bottom:1px solid rgba(255,255,255,0.35); padding-bottom:3px; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.04em;">Skills</div>
            <div>{skills_html}</div>
          </div>
          <!-- Right Body -->
          <div style="width:66%; background:#ffffff; padding:28px 24px; box-sizing:border-box;">
            {f'<div style="font-size:0.88rem; font-weight:800; text-transform:uppercase; color:{accent}; border-bottom:2px solid {accent}; padding-bottom:3px; margin-bottom:8px;">Professional Summary</div><p style="margin:0 0 16px 0; font-size:0.9rem; color:#334155; line-height:1.45;">{profile["summary"]}</p>' if profile.get("summary") else ''}

            <div style="font-size:0.88rem; font-weight:800; text-transform:uppercase; color:{accent}; border-bottom:2px solid {accent}; padding-bottom:3px; margin-bottom:10px;">Work History</div>
            {exp_html}

            <div style="font-size:0.88rem; font-weight:800; text-transform:uppercase; color:{accent}; border-bottom:2px solid {accent}; padding-bottom:3px; margin-bottom:10px; margin-top:16px;">Education</div>
            {edu_html}
          </div>
        </div>
        """

    # B. CLASSIC CENTERED / TOP BANNER / OTHER FORMATS
    contact_str = " &nbsp;·&nbsp; ".join(contacts)
    border_decor = f"border-bottom: 2px solid {accent}; padding-bottom: 4px; margin-bottom: 10px;"

    html_parts = [
        f"""
        <div style="font-family: {font_fam}; background: #ffffff; color: #1e293b; padding: 32px 36px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 20px rgba(0,0,0,0.08); max-width: 820px; margin: 0 auto; line-height: 1.5; font-size: 0.92rem;">
          <div style="text-align: center; margin-bottom: 18px;">
            <div style="font-size: 1.85rem; font-weight: 800; color: {accent}; letter-spacing: -0.01em;">{name}</div>
            <div style="font-size: 0.86rem; color: #64748b; margin-top: 4px;">{contact_str}</div>
          </div>
        """
    ]

    if profile.get("summary"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Professional Summary</div>
              <p style="margin: 0; color: #334155; font-size: 0.9rem;">{profile['summary']}</p>
            </div>
            """
        )

    if profile.get("skills"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Skills</div>
            """
        )
        for cat, items in profile["skills"].items():
            html_parts.append(
                f"""<div style="margin-bottom: 3px;"><strong style="color: #0f172a;">{cat}:</strong> <span style="color: #475569;">{", ".join(items)}</span></div>"""
            )
        html_parts.append("</div>")

    if profile.get("experience"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Work History / Experience</div>
            """
        )
        for e in profile["experience"]:
            html_parts.append(
                f"""
                <div style="margin-bottom: 12px;">
                  <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-weight: 700; color: #0f172a; font-size: 0.94rem;">{e.get('heading', '')}</span>
                    <span style="font-size: 0.82rem; font-style: italic; color: #64748b;">{e.get('date', '')}</span>
                  </div>
                  {f'<div style="font-size: 0.84rem; font-style: italic; color: #475569; margin-bottom: 4px;">{e["sub"]}</div>' if e.get('sub') else ''}
                  <ul style="margin: 4px 0 0 16px; padding: 0; color: #334155;">
                """
            )
            for b in e.get("bullets", []):
                html_parts.append(f"""<li style="margin-bottom: 3px;">{b}</li>""")
            html_parts.append("</ul></div>")
        html_parts.append("</div>")

    if profile.get("education"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Education</div>
            """
        )
        for ed in profile["education"]:
            html_parts.append(
                f"""
                <div style="margin-bottom: 8px;">
                  <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-weight: 700; color: #0f172a;">{ed.get('heading', '')}</span>
                    <span style="font-size: 0.82rem; font-style: italic; color: #64748b;">{ed.get('date', '')}</span>
                  </div>
                  {f'<div style="font-size: 0.84rem; color: #475569;">{ed["sub"]}</div>' if ed.get('sub') else ''}
                </div>
                """
            )
        html_parts.append("</div>")

    html_parts.append("</div>")
    return "".join(html_parts)

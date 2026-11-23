"""Resume Templates Engine for Parakh AI.

Provides 10+ professional, ATS-optimized resume templates with:
- Visual styling rules (colors, fonts, header layouts, borders, bullet styles)
- Full realistic dummy profiles for each persona
- Helpers to convert profiles to form fields and render live interactive HTML previews.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# TEMPLATE DEFINITIONS & METADATA
# ---------------------------------------------------------------------------
RESUME_TEMPLATES = {
    "classic_ats": {
        "id": "classic_ats",
        "name": "Classic ATS Standard",
        "badge": "100% ATS Scannable",
        "category": "Universal / Corporate",
        "icon": "🏛️",
        "accent_hex": "#1F3864",
        "secondary_hex": "#4B5563",
        "accent_rgb": (31, 56, 100),
        "secondary_rgb": (75, 85, 99),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Calibri",
        "font_family_css": "'Calibri', 'Inter', sans-serif",
        "header_layout": "center",
        "rule_style": "solid",
        "bullet_style": "disc",
        "bullet_char": "•",
        "description": "Standard corporate single-column format with navy headers and strict ATS-first scannability. Works with every HR screening system.",
    },
    "modern_tech": {
        "id": "modern_tech",
        "name": "Modern Tech & Cloud",
        "badge": "Popular for Developers",
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
        "description": "Clean modern layout designed for Software, DevOps, and Cloud engineers. Highlights tech stacks, GitHub/portfolio links, and scalable impact.",
    },
    "executive_suite": {
        "id": "executive_suite",
        "name": "Executive Leadership & VP",
        "badge": "Director & VP Roles",
        "category": "Management & Strategy",
        "icon": "👑",
        "accent_hex": "#1E293B",
        "secondary_hex": "#B45309",
        "accent_rgb": (30, 41, 59),
        "secondary_rgb": (180, 83, 9),
        "font_family_pdf": "Helvetica",
        "font_family_docx": "Georgia",
        "font_family_css": "'Georgia', serif",
        "header_layout": "split",
        "rule_style": "double",
        "bullet_style": "square",
        "bullet_char": "▪",
        "description": "High-authority presentation for CXOs, VPs, and Engineering Directors. Features executive summary prominence and strategic business metrics.",
    },
    "creative_designer": {
        "id": "creative_designer",
        "name": "Creative Studio & UI/UX",
        "badge": "Designers & Product",
        "category": "Design & Creative",
        "icon": "🎨",
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
        "description": "Vibrant violet aesthetic crafted for UI/UX Designers, Creative Leads, and Product Thinkers with problem-solution-impact narratives.",
    },
    "ivy_academic": {
        "id": "ivy_academic",
        "name": "Ivy Academic & Research",
        "badge": "PhD, R&D & Papers",
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
        "description": "Traditional collegiate serif typography. Places Education, Research Publications, Peer Reviews, and Grant funding front and center.",
    },
    "emerald_finance": {
        "id": "emerald_finance",
        "name": "Emerald Professional (Finance)",
        "badge": "Consulting & Banking",
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
        "description": "Structured high-rigor layout tailored for Investment Banking, Management Consulting, Big 4 auditing, and Financial Risk Analytics.",
    },
    "compact_fresher": {
        "id": "compact_fresher",
        "name": "Compact 1-Page (Fresher)",
        "badge": "Guaranteed 1-Page",
        "category": "Students & New Grads",
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
        "description": "Space-optimized layout with tight vertical rhythm, zero wasted margin, and immediate visibility for Academic Projects, Coursework & Degrees.",
    },
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
        "description": "Tech-forward format designed for ML Engineers and Data Scientists. Dedicated structure for Frameworks, Models Deployed, and Benchmark Scores.",
    },
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
        "description": "Action-oriented resume emphasizing KPI growth, conversion percentage increases, agile sprints, and 0-to-1 product launches.",
    },
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
        "description": "Standardized international layout compatible with UK, European, Middle East, and APAC recruitment expectations, featuring multilingual clarity.",
    },
}

# ---------------------------------------------------------------------------
# REALISTIC DUMMY PROFILES (ONE PER TEMPLATE PERSONA)
# ---------------------------------------------------------------------------
DUMMY_PROFILES = {
    "classic_ats": {
        "name": "Rahul Sharma",
        "email": "rahul.sharma@example.com",
        "phone": "+91 98765 43210",
        "location": "Bengaluru, India",
        "linkedin": "linkedin.com/in/rahul-sharma-ops",
        "github": "",
        "summary": "Results-oriented Operations & Business Analyst with 5+ years of experience streamlining enterprise workflows, reducing operational costs by 22%, and managing cross-functional stakeholder reporting.",
        "skills": {
            "Core Competencies": ["Business Analysis", "Process Automation", "Agile & Scrum", "Root Cause Analysis"],
            "Analytics & Data": ["Advanced SQL", "Tableau", "Power BI", "Excel / VBA", "Python (Pandas)"],
            "Tools & Methods": ["Jira", "Confluence", "SAP ERP", "Six Sigma Green Belt", "BPMN 2.0"],
        },
        "experience": [
            {
                "heading": "Senior Business Analyst — NexaTech Solutions",
                "date": "Jun 2022 - Present",
                "sub": "Bengaluru, Karnataka",
                "bullets": [
                    "Spearheaded supply chain analytics migration to Snowflake, decreasing query execution latency by 45%.",
                    "Authored 30+ comprehensive BRDs and functional spec documents for automated invoice matching.",
                    "Collaborated with product teams to eliminate operational bottlenecks, saving $180K annually.",
                ],
            },
            {
                "heading": "Operations Analyst — Apex Global Systems",
                "date": "Aug 2019 - May 2022",
                "sub": "Hyderabad, Telangana",
                "bullets": [
                    "Monitored and optimized weekly performance KPIs across 4 regional service fulfillment centers.",
                    "Built 12 automated Power BI executive reporting dashboards refreshed via scheduled SQL pipelines.",
                    "Awarded 'Excellence in Analytics' for identifying $65K in vendor billing discrepancies.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "Enterprise Resource Forecast Engine",
                "date": "Jan 2023 - Mar 2023",
                "sub": "Python, SQL, Tableau",
                "bullets": [
                    "Engineered predictive staffing model forecasting seasonal customer service workloads with 91% accuracy.",
                    "Reduced emergency staffing contract expenses by 28% across two fiscal quarters.",
                ],
            }
        ],
        "education": [
            {
                "heading": "Bachelor of Technology in Information Technology — NIT Karnataka",
                "date": "2015 - 2019",
                "sub": "CGPA: 8.4 / 10",
                "bullets": [],
            }
        ],
        "certifications": [
            "Certified ScrumMaster (CSM) — Scrum Alliance (2023)",
            "Six Sigma Green Belt Certified (2021)",
        ],
        "achievements": [
            "Ranked top 5% among 200+ analysts across annual APAC performance review",
            "Published internal whitepaper on Automated Data Validation Protocols",
        ],
    },
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
                    "Integrated Discord & Slack webhook alert dispatch with automated incident tracking.",
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
            "Top 2% contributor on GitHub in Go/Cloud ecosystem",
        ],
    },
    "executive_suite": {
        "name": "Vikram Malhotra",
        "email": "v.malhotra.exec@outlook.com",
        "phone": "+91 99112 23344",
        "location": "New Delhi / Gurugram, India",
        "linkedin": "linkedin.com/in/vikram-malhotra-vp",
        "github": "",
        "summary": "Transformational Engineering Leader with 14+ years of experience leading multi-disciplinary engineering organizations of 60+ members across India and North America. Scaled SaaS revenue from $4M to $25M ARR while driving enterprise modernization.",
        "skills": {
            "Executive Leadership": ["Engineering Strategy", "P&L Management", "Team Scaling (10 -> 65)", "Talent Retention", "Executive Stakeholder Alignment"],
            "Architecture & Scale": ["Enterprise Architecture", "SaaS Multi-tenancy", "Cloud Cost Governance", "ISO 27001 & SOC2 Compliance"],
            "Operational Rigor": ["Agile at Scale (SAFe)", "OKRs & KPIs", "Vendor Negotiation", "Mergers & Technical Due Diligence"],
        },
        "experience": [
            {
                "heading": "Vice President of Engineering — Crestline Enterprise Systems",
                "date": "Jan 2020 - Present",
                "sub": "Gurugram, India",
                "bullets": [
                    "Oversee 65-member global engineering & QA organization delivering core B2B banking SaaS products.",
                    "Spearheaded multi-region cloud consolidation reducing AWS annual run-rate by $420,000 without performance loss.",
                    "Achieved 94% annualized team retention by instituting transparent engineering career ladders and growth coaching.",
                ],
            },
            {
                "heading": "Director of Software Engineering — FinLogic Global",
                "date": "Mar 2015 - Dec 2019",
                "sub": "Noida, India",
                "bullets": [
                    "Led core platform engineering through acquisition transition, maintaining 99.99% contract SLAs.",
                    "Championed automated CI/CD and DevSecOps transformation, boosting release cadence from monthly to daily.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "Core Cloud Platform Modernization ($12M Scale)",
                "date": "2021 - 2023",
                "sub": "Multi-Cloud Kubernetes, Zero Trust Security",
                "bullets": [
                    "Delivered 18-month enterprise modernization on time and 8% under budget, supporting tier-1 banking clients.",
                ],
            }
        ],
        "education": [
            {
                "heading": "M.Tech in Software Systems — BITS Pilani",
                "date": "2011 - 2013",
                "sub": "Graduated with Honors",
                "bullets": [],
            },
            {
                "heading": "B.Tech in Computer Science — Delhi Technological University (DTU)",
                "date": "2006 - 2010",
                "sub": "First Division",
                "bullets": [],
            },
        ],
        "certifications": [
            "Executive Leadership Program — IIM Ahmedabad (2021)",
            "TOGAF 9.2 Enterprise Architecture Certified",
        ],
        "achievements": [
            "Recognized as 'Top Technology Leader of the Year' at India FinTech Summit 2023",
            "Keynote speaker at 4 national DevOps and Cloud Architecture summits",
        ],
    },
    "creative_designer": {
        "name": "Priya Sundaram",
        "email": "priya.design@createbox.co",
        "phone": "+91 97654 32190",
        "location": "Bengaluru, India",
        "linkedin": "linkedin.com/in/priya-design",
        "github": "dribbble.com/priyaux",
        "summary": "Product & UX Designer with 5 years crafting human-centered mobile and web applications. Passionate about design systems, micro-interactions, and translating complex user flows into intuitive, high-converting interfaces.",
        "skills": {
            "Product Design": ["User Experience (UX)", "Interface Design (UI)", "Design Systems", "Wireframing & Prototyping", "Information Architecture"],
            "Research & Validation": ["Usability Testing", "User Journey Mapping", "A/B Testing", "Heuristic Evaluation", "User Interviews"],
            "Tools & Code": ["Figma (Auto-layout, Components)", "Adobe Creative Suite", "Framer", "Miro", "HTML5/CSS3 basics"],
        },
        "experience": [
            {
                "heading": "Lead Product Designer — UrbanCart Digital",
                "date": "Jul 2022 - Present",
                "sub": "Bengaluru, India",
                "bullets": [
                    "Redesigned mobile checkout journey, resulting in a 24% uplift in cart conversion across 1.4M users.",
                    "Architected unified cross-platform design system 'Prism' utilized across iOS, Android, and web products.",
                    "Facilitated design thinking workshops with PMs and engineering leads to align product sprint roadmaps.",
                ],
            },
            {
                "heading": "UX/UI Designer — PixelCraft Agency",
                "date": "Aug 2019 - Jun 2022",
                "sub": "Chennai, India",
                "bullets": [
                    "Delivered end-to-end design solutions for 8 SaaS and consumer tech clients from discovery to design handoff.",
                    "Conducted 45+ usability interviews that directly informed product pivots for a seed-funded fintech startup.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "ZenHealth — Holistic Wellness & Telehealth App",
                "date": "2023",
                "sub": "Figma, Framer, User Testing (50+ participants)",
                "bullets": [
                    "Designed accessible healthcare onboarding flow scoring 86 SUS (System Usability Scale).",
                    "Featured on Behance Curated Interaction Design Gallery.",
                ],
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
        "certifications": [
            "Interaction Design Foundation (IxDF) Certified UX Master",
            "Nielsen Norman Group (NN/g) UX Certified",
        ],
        "achievements": [
            "Featured Speaker at DesignUp Conference 2023 on 'Scalable Design Tokens in Figma'",
            "Winner of UX India Student Design Award (2019)",
        ],
    },
    "ivy_academic": {
        "name": "Dr. Ananya Sen",
        "email": "ananya.sen@univ-research.edu",
        "phone": "+91 94321 87654",
        "location": "Kolkata / Delhi, India",
        "linkedin": "linkedin.com/in/dr-ananya-sen",
        "github": "scholar.google.com/citations?user=ananya-sen",
        "summary": "Postdoctoral Research Fellow and Computer Scientist specializing in Explainable AI, Deep Graph Networks, and Computer Vision. Author of 12 peer-reviewed IEEE/ACM papers with 420+ citations. Recipient of National Science Fellowship.",
        "skills": {
            "Research Domains": ["Deep Learning", "Graph Neural Networks (GNN)", "Explainable AI (XAI)", "Medical Imaging Analysis"],
            "Technical Stack": ["PyTorch", "TensorFlow", "CUDA / C++", "Python (NumPy, SciPy)", "LaTeX", "OpenCV"],
            "Methodology": ["Statistical Hypothesis Testing", "Grant Proposal Writing", "Peer Reviewing", "Curriculum Development"],
        },
        "education": [
            {
                "heading": "Ph.D. in Computer Science — Indian Institute of Technology (IIT) Kharagpur",
                "date": "2018 - 2023",
                "sub": "Thesis: Interpretable Graph Representations for Biomedical Image Segmentation",
                "bullets": ["Awarded Best Doctoral Dissertation Award in Computational Sciences."],
            },
            {
                "heading": "M.Tech in Computer Science — Jadavpur University",
                "date": "2016 - 2018",
                "sub": "First Class with Distinction (Gold Medalist)",
                "bullets": [],
            },
        ],
        "experience": [
            {
                "heading": "Postdoctoral Research Fellow — Institute of AI & Medical Sciences",
                "date": "May 2023 - Present",
                "sub": "New Delhi, India",
                "bullets": [
                    "Principal investigator on DST-funded grant ($60,000) developing low-latency diagnostic screening models.",
                    "Supervise 4 doctoral candidates and organize weekly departmental seminar series in machine learning.",
                ],
            },
            {
                "heading": "Graduate Teaching & Research Assistant — IIT Kharagpur",
                "date": "Jul 2018 - Apr 2023",
                "sub": "Kharagpur, West Bengal",
                "bullets": [
                    "Taught 'Advanced Deep Learning' and 'Data Structures' to batches of 140+ undergraduate engineering students.",
                    "Reviewed 25+ manuscripts for IEEE Transactions on Neural Networks and Learning Systems (TNNLS).",
                ],
            },
        ],
        "projects": [
            {
                "heading": "Explainable Histopathology Classification Network",
                "date": "2022 - 2023",
                "sub": "PyTorch, CUDA, Published in IEEE TMI",
                "bullets": [
                    "Developed novel attention-guided graph framework that achieved 96.4% sensitivity on multiclass tumor datasets.",
                ],
            }
        ],
        "certifications": [
            "National Eligibility Test (CSIR-UGC NET) — JRF (All India Rank 14)",
        ],
        "achievements": [
            "Selected for prestigious Young Scientist Travel Grant to CVPR",
            "Published 12 papers indexed in Scopus / Web of Science with h-index 9",
        ],
    },
    "emerald_finance": {
        "name": "Rohan Kapoor",
        "email": "rohan.kapoor@finadvisory.in",
        "phone": "+91 98111 22334",
        "location": "Mumbai, India",
        "linkedin": "linkedin.com/in/rohan-kapoor-cfa",
        "github": "",
        "summary": "Chartered Financial Analyst (CFA) and Strategy Consultant with 6 years advising Fortune 500 leadership on M&A due diligence, financial modeling, capital allocation, and debt restructuring valued over $400M.",
        "skills": {
            "Financial Modeling": ["DCF & LBO Modeling", "Mergers & Acquisitions (M&A)", "Three-Statement Modeling", "Company Valuation"],
            "Corporate Strategy": ["Due Diligence", "Market Entry Sizing", "Synergy Assessment", "Commercial Due Diligence"],
            "Tools & Systems": ["Bloomberg Terminal", "Capital IQ", "PitchBook", "Excel (VBA / Macros)", "Power BI"],
        },
        "experience": [
            {
                "heading": "Manager, Corporate Finance & Advisory — Apex Capital Partners",
                "date": "Aug 2021 - Present",
                "sub": "Mumbai, Maharashtra",
                "bullets": [
                    "Advised on 7 completed sell-side and buy-side M&A transactions with aggregate transaction value of $320M.",
                    "Engineered complex dynamic leveraged buyout (LBO) financial models evaluating debt service capacity across stress scenarios.",
                    "Authored Confidential Information Memorandums (CIM) presented directly to sovereign wealth and PE funds.",
                ],
            },
            {
                "heading": "Senior Associate, Strategy Consulting — Global Strategy Group",
                "date": "Jul 2018 - Jul 2021",
                "sub": "Gurugram, India",
                "bullets": [
                    "Conducted commercial due diligence and market sizing for renewable energy and SaaS portfolio investments.",
                    "Identified cost-saving levers delivering $18M recurring EBITDA improvement for an industrial manufacturing client.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "Cross-Border FinTech Valuation & Synergies Analysis",
                "date": "2023",
                "sub": "Capital IQ, Dynamic Discounted Cash Flow Modeling",
                "bullets": [
                    "Modeled combined post-merger balance sheet and calculated $42M present value of technology platform synergies.",
                ],
            }
        ],
        "education": [
            {
                "heading": "MBA in Finance & Strategy — SPJIMR, Mumbai",
                "date": "2016 - 2018",
                "sub": "Dean's Honor List (Top 5% of graduating cohort)",
                "bullets": [],
            },
            {
                "heading": "B.Com (Honours) — Shri Ram College of Commerce (SRCC), Delhi",
                "date": "2013 - 2016",
                "sub": "First Division with Distinction",
                "bullets": [],
            },
        ],
        "certifications": [
            "CFA Charterholder — CFA Institute, USA (Chartered in 2021)",
            "Financial Risk Manager (FRM Level 1 Passed)",
        ],
        "achievements": [
            "National Finalist in CFA Institute Research Challenge (2018)",
            "Fast-tracked to Advisory Manager within 24 months based on deal velocity",
        ],
    },
    "compact_fresher": {
        "name": "Neha Verma",
        "email": "neha.verma.cs24@gmail.com",
        "phone": "+91 98987 65432",
        "location": "Jaipur / Bengaluru, India",
        "linkedin": "linkedin.com/in/neha-verma-tech",
        "github": "github.com/neha-verma24",
        "summary": "Recent Computer Science & Engineering graduate (2024) with strong foundations in Data Structures, Algorithms, Python, and React.js. Completed 2 software internships and built 4 production-grade web applications.",
        "skills": {
            "Programming": ["Python", "Java", "C++", "JavaScript", "SQL"],
            "Web Technologies": ["React.js", "HTML5", "CSS3", "Node.js (Express)", "REST APIs"],
            "Database & Tools": ["MySQL", "MongoDB", "Git & GitHub", "VS Code", "Postman", "Linux"],
            "Core CS": ["Data Structures & Algorithms", "Object-Oriented Programming (OOP)", "Database Management (DBMS)"],
        },
        "education": [
            {
                "heading": "B.Tech in Computer Science & Engineering — Malaviya National Institute of Technology (MNIT)",
                "date": "2020 - 2024",
                "sub": "CGPA: 8.7 / 10 | Relevant Coursework: Operating Systems, Computer Networks, Cloud Basics",
                "bullets": [],
            }
        ],
        "experience": [
            {
                "heading": "Software Development Intern — QuickByte Technologies",
                "date": "Jan 2024 - Jun 2024",
                "sub": "Bengaluru (Hybrid)",
                "bullets": [
                    "Developed 5 responsive customer portal pages in React.js, reducing average page load time by 30%.",
                    "Integrated JWT token-based authentication and role-based access control (RBAC) across 8 REST endpoints.",
                    "Wrote automated unit test suites using Jest, raising backend code coverage from 62% to 84%.",
                ],
            }
        ],
        "projects": [
            {
                "heading": "Smart Campus Lost & Found System",
                "date": "Aug 2023 - Nov 2023",
                "sub": "React.js, Node.js, Express, MongoDB",
                "bullets": [
                    "Created college-wide portal serving 3,000+ active students with automated image matching and email notifications.",
                    "Implemented responsive mobile-friendly UI with zero external UI library overhead.",
                ],
            },
            {
                "heading": "Algorithmic Pathfinding Visualizer",
                "date": "May 2023",
                "sub": "JavaScript, HTML5 Canvas",
                "bullets": [
                    "Interactive visualization tool demonstrating Dijkstra's, A*, and BFS pathfinding algorithms with custom grid walls.",
                ],
            },
        ],
        "certifications": [
            "Meta Front-End Developer Professional Certificate (Coursera, 2023)",
            "Problem Solving (Advanced) Certificate — HackerRank",
        ],
        "achievements": [
            "Solved 450+ coding problems across LeetCode and GeeksforGeeks",
            "Finalist in Smart India Hackathon (SIH 2023) — College Team Lead",
        ],
    },
    "data_science_ai": {
        "name": "Arjun Nair",
        "email": "arjun.nair@datasci.ai",
        "phone": "+91 97401 23456",
        "location": "Bengaluru, India",
        "linkedin": "linkedin.com/in/arjun-nair-ai",
        "github": "github.com/arjun-nair-ml",
        "summary": "Lead Machine Learning Engineer & Data Scientist with 6+ years deploying scalable LLM pipelines, RAG systems, and computer vision models. Master's in CS from IISc with experience serving 50M+ automated inferences per month.",
        "skills": {
            "AI / ML Modeling": ["Large Language Models (LLMs)", "RAG Systems", "PyTorch", "Hugging Face", "LangChain", "LlamaIndex"],
            "MLOps & Deployment": ["Triton Inference Server", "MLflow", "Docker", "Kubeflow", "AWS SageMaker", "ONNX"],
            "Data & Analytics": ["Python (NumPy, SciPy, Pandas)", "SQL", "Spark / PySpark", "Vector Databases (Milvus, Pinecone, FAISS)"],
            "Specialized": ["Fine-tuning (LoRA, QLoRA)", "Prompt Engineering", "Semantic Search", "Time Series Forecasting"],
        },
        "experience": [
            {
                "heading": "Lead Machine Learning Engineer — CognitiveScale AI",
                "date": "Aug 2021 - Present",
                "sub": "Bengaluru, India",
                "bullets": [
                    "Designed enterprise generative AI assistant with multi-document RAG, answering 120,000 queries/month with 94% factual accuracy.",
                    "Fine-tuned open-source 7B and 13B parameter LLMs using QLoRA, cutting API operational expenses by $18,000/month.",
                    "Built automated MLOps evaluation harness testing embeddings drift, hallucination metrics, and response latencies.",
                ],
            },
            {
                "heading": "Data Scientist — QuantIQ Analytics",
                "date": "Jul 2018 - Jul 2021",
                "sub": "Hyderabad, India",
                "bullets": [
                    "Engineered deep learning fraud detection classifier on 40M financial records, mitigating $2.4M in unauthorized card charges.",
                    "Deployed distributed XGBoost risk models on AWS SageMaker with automated weekly data drift retraining.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "NeuroSearch — Open-Source Hybrid Vector Search Engine",
                "date": "2023",
                "sub": "Python, FAISS, BM25, FastAPI",
                "bullets": [
                    "Blended dense vector semantic embeddings with sparse BM25 keyword search, improving retrieval recall by 19%.",
                ],
            }
        ],
        "education": [
            {
                "heading": "M.Tech in Computational Science — Indian Institute of Science (IISc), Bangalore",
                "date": "2016 - 2018",
                "sub": "GPA: 9.1 / 10 | Focus: High Performance Machine Learning",
                "bullets": [],
            },
            {
                "heading": "B.Tech in Computer Engineering — NIT Calicut",
                "date": "2012 - 2016",
                "sub": "Graduated First Class with Honors",
                "bullets": [],
            },
        ],
        "certifications": [
            "TensorFlow Certified Professional Developer (Google)",
            "DeepLearning.AI Deep Learning Specialization",
        ],
        "achievements": [
            "Kaggle Competitions Master (Top 1% global ranking, 2 Gold Medals)",
            "Co-authored research paper on 'Quantized Embeddings in Domain RAG' (EMNLP Workshop)",
        ],
    },
    "startup_growth": {
        "name": "Karan Mehra",
        "email": "karan@productscale.co",
        "phone": "+91 98123 45678",
        "location": "Bengaluru / Gurugram, India",
        "linkedin": "linkedin.com/in/karan-product",
        "github": "",
        "summary": "Product Management & Growth Leader with 6 years taking B2B SaaS and consumer products from 0 to 1 and 1 to 10. Managed $8M ARR portfolios, driven 42% retention improvements, and spearheaded agile development across 3 pods.",
        "skills": {
            "Product Leadership": ["0-to-1 Product Discovery", "User Journey Optimization", "PLG (Product-Led Growth)", "Pricing & Packaging"],
            "Execution & Analytics": ["A/B Testing & Experimentation", "Amplitude", "Mixpanel", "SQL", "Google Analytics 4", "Hotjar"],
            "Processes & Tools": ["Scrum & Kanban", "PRDs & User Stories", "Jira", "Notion", "Linear", "Figma wireframing"],
        },
        "experience": [
            {
                "heading": "Principal Product Manager — ZapFlow Technologies",
                "date": "Apr 2022 - Present",
                "sub": "Bengaluru, India",
                "bullets": [
                    "Led product strategy for automated workflow builder, accelerating product-qualified leads (PQLs) by 58% in 6 months.",
                    "Instituted continuous experimentation framework launching 24 growth A/B experiments that unlocked $1.8M ARR.",
                    "Collaborated closely with enterprise sales leadership to close 14 six-figure ACV client deals.",
                ],
            },
            {
                "heading": "Senior Product Manager — GrowthHub SaaS",
                "date": "Jan 2019 - Mar 2022",
                "sub": "Gurugram, India",
                "bullets": [
                    "Revamped self-serve onboarding experience, boosting day-30 trial-to-paid conversion from 4.2% to 8.6%.",
                    "Managed cross-functional agile squad of 11 engineers, 2 designers, and 1 product marketer.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "Zero-to-One AI Marketing Assistant Launch",
                "date": "2023",
                "sub": "Generative AI, Agile Product Discovery",
                "bullets": [
                    "Conducted 60 customer discovery interviews, validated product-market fit, and hit $400K ARR in 90 days post-launch.",
                ],
            }
        ],
        "education": [
            {
                "heading": "Post Graduate Diploma in Management (MBA) — IIM Lucknow",
                "date": "2016 - 2018",
                "sub": "Major in Marketing & Strategy",
                "bullets": [],
            },
            {
                "heading": "B.Tech in Mechanical Engineering — IIT Roorkee",
                "date": "2012 - 2016",
                "sub": "Graduated First Class",
                "bullets": [],
            },
        ],
        "certifications": [
            "Reforge Certified Growth Series & Product Strategy",
            "Certified Scrum Product Owner (CSPO)",
        ],
        "achievements": [
            "Ranked among 'Top 25 Rising Product Leaders in India' by ProductGeeks",
            "Speaker on 'Product-Led Growth Metrics that Matter' at SaaSBoomi 2023",
        ],
    },
    "euro_international": {
        "name": "Siddharth Roy",
        "email": "s.roy@globalcloud.eu",
        "phone": "+44 7700 900123 / +91 99000 11223",
        "location": "London, UK / Bengaluru, India",
        "linkedin": "linkedin.com/in/siddharth-roy-architect",
        "github": "github.com/siddharth-cloud-intl",
        "summary": "Enterprise Solutions Architect with 11+ years leading multi-national cloud infrastructure projects across Europe and Asia. Specialized in TOGAF architecture frameworks, multi-region compliance (GDPR), and scalable migration.",
        "skills": {
            "Enterprise Architecture": ["TOGAF 9.2", "Cloud Migration", "Multi-Region Disaster Recovery", "Zero Trust Architecture"],
            "Cloud & Infrastructure": ["AWS (Well-Architected Framework)", "Microsoft Azure", "Terraform", "Kubernetes", "Cisco Networking"],
            "Compliance & Governance": ["GDPR / Data Sovereignty", "ISO/IEC 27001", "SOC 2 Type II", "FinOps Cloud Cost Allocation"],
            "Languages": ["English (Native / Fluent)", "German (B2 Professional)", "Hindi (Native)"],
        },
        "experience": [
            {
                "heading": "Lead Enterprise Cloud Architect — Continental Cloud Solutions",
                "date": "Jan 2021 - Present",
                "sub": "London, United Kingdom & Frankfurt, Germany",
                "bullets": [
                    "Direct cloud transformation roadmap for 4 tier-1 European financial and retail conglomerates with $20M+ cloud spend.",
                    "Engineered GDPR-compliant sovereign data storage architecture across AWS Frankfurt and Zurich regions.",
                    "Decreased critical incident MTTR by 52% via infrastructure-as-code automation and distributed Datadog observability.",
                ],
            },
            {
                "heading": "Senior Infrastructure Architect — Tata Consultancy Services (TCS)",
                "date": "Sep 2014 - Dec 2020",
                "sub": "Bengaluru, India & Amsterdam, Netherlands",
                "bullets": [
                    "Managed migration of 220+ legacy on-premise application servers into Azure cloud environment with zero planned outage.",
                    "Authored technical RFPs that secured £8.5M multi-year managed cloud infrastructure partnership.",
                ],
            },
        ],
        "projects": [
            {
                "heading": "Global Zero-Trust Multi-Cloud Mesh",
                "date": "2022 - 2023",
                "sub": "Terraform, AWS, Azure, HashiCorp Vault",
                "bullets": [
                    "Established encrypted software-defined mesh linking 14 international offices with unified identity access.",
                ],
            }
        ],
        "education": [
            {
                "heading": "M.Sc in Information Systems & Cloud Security — King's College London",
                "date": "2013 - 2014",
                "sub": "Graduated with Distinction",
                "bullets": [],
            },
            {
                "heading": "B.E. in Electronics & Telecommunications — Mumbai University",
                "date": "2008 - 2012",
                "sub": "First Class with Distinction",
                "bullets": [],
            },
        ],
        "certifications": [
            "AWS Certified Solutions Architect – Professional (SAP-C02)",
            "TOGAF 9 Certified Enterprise Architect (The Open Group)",
            "Certified Information Systems Security Professional (CISSP)",
        ],
        "achievements": [
            "Co-authored whitepaper on 'Data Sovereignty in European Hybrid Clouds'",
            "Elected Member of British Computer Society (MBCS)",
        ],
    },
}


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
    """Return template dict or fallback to classic_ats."""
    return RESUME_TEMPLATES.get(template_id, RESUME_TEMPLATES["classic_ats"])


def get_dummy_profile(template_id: str) -> dict:
    """Return realistic dummy candidate profile for the specified template."""
    return DUMMY_PROFILES.get(template_id, DUMMY_PROFILES["classic_ats"])


# ---------------------------------------------------------------------------
# INTERACTIVE LIVE HTML PREVIEW BUILDER (FOR STREAMLIT UI)
# ---------------------------------------------------------------------------
def render_template_html(profile: dict, template_id: str = "classic_ats") -> str:
    """Render a live, beautiful HTML/CSS preview card of the resume inside Streamlit."""
    tpl = get_template(template_id)
    accent = tpl["accent_hex"]
    font_fam = tpl.get("font_family_css", "'Inter', sans-serif")
    align = tpl.get("header_layout", "center")
    bullet_char = tpl.get("bullet_char", "•")

    # Header Contacts
    contacts = [profile.get("email"), profile.get("phone"), profile.get("location")]
    contacts += [profile.get(k) for k in ("linkedin", "github") if profile.get(k)]
    contacts = [c for c in contacts if c]
    contact_str = " &nbsp;·&nbsp; ".join(contacts)

    header_align_css = "text-align: center;" if align == "center" else "text-align: left;"
    border_decor = f"border-bottom: 2px solid {accent}; padding-bottom: 4px; margin-bottom: 10px;"

    html_parts = [
        f"""
        <div style="font-family: {font_fam}; background: #ffffff; color: #1e293b; padding: 28px 32px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 16px rgba(0,0,0,0.06); max-width: 820px; margin: 0 auto; line-height: 1.5; font-size: 0.92rem;">
          <div style="{header_align_css} margin-bottom: 18px;">
            <div style="font-size: 1.75rem; font-weight: 800; color: {accent}; letter-spacing: -0.02em;">{profile.get('name', 'Candidate Name')}</div>
            <div style="font-size: 0.86rem; color: #64748b; margin-top: 4px;">{contact_str}</div>
          </div>
        """
    ]

    # Summary
    if profile.get("summary"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Professional Summary</div>
              <p style="margin: 0; color: #334155; font-size: 0.9rem;">{profile['summary']}</p>
            </div>
            """
        )

    # Skills
    if profile.get("skills"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Technical Skills</div>
            """
        )
        for cat, items in profile["skills"].items():
            html_parts.append(
                f"""<div style="margin-bottom: 3px;"><strong style="color: #0f172a;">{cat}:</strong> <span style="color: #475569;">{", ".join(items)}</span></div>"""
            )
        html_parts.append("</div>")

    # Experience
    if profile.get("experience"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Professional Experience</div>
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

    # Projects
    if profile.get("projects"):
        html_parts.append(
            f"""
            <div style="margin-bottom: 16px;">
              <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Key Projects</div>
            """
        )
        for p in profile["projects"]:
            html_parts.append(
                f"""
                <div style="margin-bottom: 10px;">
                  <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-weight: 700; color: #0f172a; font-size: 0.94rem;">{p.get('heading', '')}</span>
                    <span style="font-size: 0.82rem; font-style: italic; color: #64748b;">{p.get('date', '')}</span>
                  </div>
                  {f'<div style="font-size: 0.84rem; font-style: italic; color: #475569; margin-bottom: 3px;">{p["sub"]}</div>' if p.get('sub') else ''}
                  <ul style="margin: 4px 0 0 16px; padding: 0; color: #334155;">
                """
            )
            for b in p.get("bullets", []):
                html_parts.append(f"""<li style="margin-bottom: 2px;">{b}</li>""")
            html_parts.append("</ul></div>")
        html_parts.append("</div>")

    # Education
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
                  {f'<div style="font-size: 0.84rem; font-style: italic; color: #475569;">{ed["sub"]}</div>' if ed.get('sub') else ''}
                </div>
                """
            )
        html_parts.append("</div>")

    # Certifications & Achievements
    if profile.get("certifications") or profile.get("achievements"):
        html_parts.append(f"""<div style="margin-bottom: 10px;">""")
        if profile.get("certifications"):
            html_parts.append(
                f"""
                <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Certifications</div>
                <ul style="margin: 4px 0 12px 16px; padding: 0; color: #334155;">
                """
            )
            for c in profile["certifications"]:
                html_parts.append(f"""<li style="margin-bottom: 2px;">{c}</li>""")
            html_parts.append("</ul>")

        if profile.get("achievements"):
            html_parts.append(
                f"""
                <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; color: {accent}; {border_decor}">Key Achievements & Honors</div>
                <ul style="margin: 4px 0 12px 16px; padding: 0; color: #334155;">
                """
            )
            for a in profile["achievements"]:
                html_parts.append(f"""<li style="margin-bottom: 2px;">{a}</li>""")
            html_parts.append("</ul>")
        html_parts.append("</div>")

    html_parts.append("</div>")
    return "".join(html_parts)

# AI Resume Analyzer

A Python project that

1. **analyses** resumes (PDF / DOCX / TXT) against a job description,
2. **shortlists** candidates automatically (Shortlisted / On Hold / Rejected),
3. **scans for AI-written text** (flags resumes that look chatbot-generated, with the reasons),
4. **checks the format** - if a resume is not in the required format it lists exactly what is wrong and how to fix it,
5. **builds a resume in the required format** (DOCX + PDF) from the candidate's own content.

It has a Streamlit web app (`app.py`, three tabs: **Analyze & Shortlist**, **AI Resume Check**, **Build Resume**) and two
command-line tools: `cli.py` (full analysis) and `ai_check.py` (AI-written check only).

---

## Setup (Windows - VS Code terminal)

```bat
cd path\to\resume_analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Always activate the virtual environment first (you should see `(venv)` in the terminal).
Run the web app with `streamlit run app.py` - not `python app.py`.
Mac / Linux: `source venv/bin/activate` instead of `venv\Scripts\activate`.

## Try it with the sample data

```bat
python sample_data\make_samples.py
python cli.py --jd sample_data\job_description.txt --resumes sample_data\resumes
```

This writes to `output/`: `shortlist.csv`, `analysis_report.pdf` and `formatted_resumes/`.

In the web app, click **Load sample job description**, upload the files from `sample_data/resumes/`
and press **Analyze resumes**.

## CLI options

| Option | Meaning |
|---|---|
| `--jd FILE` | job description (.txt / .pdf / .docx) |
| `--resumes ...` | resume files and/or folders |
| `--threshold 60` | shortlist cut-off in % (default 60) |
| `--must-have "Python,SQL"` | candidates missing any of these cannot be shortlisted |
| `--out output` | output folder |
| `--ai-hold` | move resumes marked "Likely" AI-written from Shortlisted to On Hold |
| `--all-formatted` | build a formatted resume for everyone (default: only non-compliant ones) |

## How it works

| Module | Job |
|---|---|
| `resume_parser.py` | text extraction (pdfplumber, python-docx), name / email / phone / links, section detection, skill detection with aliases and typo tolerance (`rapidfuzz` if available, otherwise `difflib`), experience estimation from date ranges |
| `format_checker.py` | checks the resume against the required format and returns a score, issues (critical / major / minor) and fixes |
| `ai_detector.py` | AI-written text scan (heuristic indicator 0-100 with reasons and the most AI-sounding lines) |
| `ai_check.py` | command-line tool for the AI check only |
| `matcher.py` | JD parsing, skill / experience scoring, shortlist decision |
| `textsim.py` | TF-IDF + cosine similarity in plain Python (no scikit-learn / numpy needed) |
| `resume_builder.py` | builds the required-format resume (DOCX + PDF) |
| `report_generator.py` | PDF analysis report |
| `analyzer.py` | pipeline shared by the app and the CLI |
| `skills_db.py` | skills, aliases, section headings - extend this to support new domains |

### Score

`Overall = 45 % skill match + 25 % text similarity (TF-IDF) + 15 % experience + 15 % format score`

* **Shortlisted**: score >= cut-off, every must-have skill present, an email or phone available
* **On Hold**: within 15 points of the cut-off, or a must-have skill / contact detail is missing
* **Rejected**: below that

### AI-written resume scan

**Separate check (no job description needed):** open the **AI Resume Check** tab, upload one or more resumes or paste
the text, and press *Check for AI-written text*. You get a verdict per resume, the reasons, and the lines that sound
most AI-written. From the command line:

```bat
python ai_check.py sample_data\resumes --details
python ai_check.py resume1.pdf resume2.docx --out ai_check.csv
```

The same indicator also appears inside *Analyze & Shortlist* next to every candidate.

Every resume gets an **AI-written indicator (0-100)**: *Unlikely* (0-24), *Possible* (25-49) or *Likely* (50+),
shown in the app, the CSV, the PDF report and the CLI table, together with the reasons. It looks for:

| Signal | Example |
|---|---|
| Chatbot text left in the resume | "Certainly! Here is your resume", "Feel free to customize", `[Your Name]`, `**bold**` markdown |
| Clichéd buzzwords | spearheaded, leveraged, orchestrated, seamless, robust, results-driven, proven track record |
| Bullets of almost equal length | every bullet is 14-16 words |
| Formulaic endings | "..., resulting in / ensuring / leading to ..." in most bullets |
| A % metric in every bullet | 40 %, 25 %, 30 % - mostly round numbers |
| Generic template wording | "strong foundation in", "seeking an entry-level role", "contribute to the growth of the organization" |
| Result clauses glued on with "-ing" | "..., enhancing user experience", "..., ensuring reliable performance", "to ensure ..." |
| Vague claims with no numbers | "efficiently", "smooth performance", "intuitive interface" but no figures |
| Polished, wordy prose | very long bullets (20+ words), stacked adjectives ("clean, modern, and responsive ... intuitive ... scalable"), "Possesses hands-on knowledge ..." |
| Weak signals | generic soft-skill list, every bullet opening with a different strong verb, many em dashes |

**Sensitivity** (sidebar slider, or `--ai-sensitivity` / `--sensitivity` on the command line):
*strict* flags only obvious cases, *balanced* is the default, *sensitive* also flags lightly edited AI text but gives more
false alarms. If a resume you know is AI-written shows "Unlikely", try *sensitive*.

**Important - this is an indicator, not proof.** No tool can know for sure who wrote a text.
Edited AI text and plain well-written AI text can pass, and formal, template-based or non-native English writing
can be flagged. So the scan never rejects anyone by itself. Use it to decide whom to question in the interview
(ask the candidate to explain a project line by line). Tick **"Hold AI-written resumes for manual review"**
(CLI: `--ai-hold`) to move "Likely" resumes from Shortlisted to On Hold. A candidate whose resume is flagged also gets
a suggestion to rewrite it in their own words with real project names, tools and numbers.
Resumes with fewer than 80 words are only checked for chatbot leftovers.

### Required resume format

Single column, no tables or icons, standard headings in this order:
**Name + contact line -> Professional Summary -> Technical Skills -> Work Experience / Internships -> Projects -> Education -> Certifications / Achievements**,
with bullet points that start with action verbs and contain numbers, and a length of one page (two at most).

Format score = 100 minus penalties (critical -15, major -8, minor -4). A resume is *compliant* when the
score is at least 75 and nothing critical is missing (email, skills, education, experience/projects).

### Generated resumes never invent facts

The builder only rearranges what the candidate already wrote. Anything that is missing (summary, phone,
project details...) appears as a red `[placeholder]` for the candidate to fill in.
Scanned (image-only) PDFs cannot be read - ask for a text-based PDF or DOCX.

## Known limits / ideas to extend

* Skills are matched against the list in `skills_db.py`; add your own domain skills there.
* A JD sentence such as "Flask **or** FastAPI" counts both skills - use *must-have skills* to control what is mandatory.
* No OCR for scanned PDFs (could be added with `pytesseract`).
* If Windows blocks a compiled package ("Application Control policy has blocked this file"), the command-line version (`cli.py`) needs the fewest packages: `pdfplumber`, `python-docx`, `fpdf2`. Using Python 3.12 instead of 3.14, or turning off Smart App Control, also fixes it.
* Possible upgrades: sentence-embedding similarity (`sentence-transformers`), a database to store candidates, e-mail notifications.

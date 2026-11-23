"""Generates four sample resumes (good, badly formatted, partial, mismatched) for testing.

Run:  python sample_data/make_samples.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from docx import Document  # noqa: E402
from fpdf import FPDF  # noqa: E402

from resume_builder import build_resume_docx, build_resume_pdf, profile_from_fields  # noqa: E402

OUT = os.path.join(HERE, "resumes")
os.makedirs(OUT, exist_ok=True)

# 1) well formatted, strong match -> DOCX
good = profile_from_fields({
    "name": "Aisha Verma", "email": "aisha.verma@example.com", "phone": "+91 98765 43210",
    "linkedin": "linkedin.com/in/aishaverma", "github": "github.com/aishaverma",
    "summary": "MCA graduate with hands-on experience in Python, machine learning and NLP, "
               "looking for a Python Developer (AI/ML) role to build data-driven products.",
    "skills": "Languages: Python, SQL, Java\n"
              "ML & Data: Pandas, NumPy, Scikit-learn, Machine Learning, NLP, TF-IDF\n"
              "Backend & Tools: Flask, REST API, MySQL, Git, GitHub, Docker, Data Structures, OOP",
    "experience": "Python Developer Intern | DataWorks Pvt Ltd | Jun 2025 - Dec 2025\n"
                  "- Built a Flask REST API serving a text-classification model used by 3 internal teams\n"
                  "- Cleaned and analysed 50,000+ records with Pandas and improved model accuracy to 91%\n"
                  "- Wrote MySQL queries and reduced report generation time by 40%",
    "projects": "AI Resume Analyzer | Python, Scikit-learn, Streamlit | 2025\n"
                "- Developed a TF-IDF and cosine-similarity engine that ranks resumes against a job description\n"
                "- Designed a skill-gap module and automated shortlisting for 100+ resumes\n"
                "Sentiment Analysis API | Python, Flask, NLTK | 2024\n"
                "- Implemented a sentiment classifier with 88% accuracy and deployed it with Docker",
    "education": "MCA, Himachal Pradesh Technical University | 2024 - 2026\nCGPA: 8.4\n"
                 "BCA, Government College | 2021 - 2024",
    "certifications": "- Machine Learning Specialization - Coursera\n- Python for Everybody - Coursera",
})
build_resume_docx(good, os.path.join(OUT, "aisha_verma_good.docx"))

# 2) strong skills but terrible format (one paragraph, no headings, no contact) -> DOCX
bad = Document()
bad.add_paragraph(
    "i am rohan and i have done mca i know python machine learning pandas numpy scikit-learn sql "
    "flask git i made a resume analyzer project using tf-idf and also a sentiment analysis project "
    "using nlp i have worked as intern and made rest api using flask and mysql database i am a hard "
    "working person and i want job in good company my skills are data structures oop docker github")
bad.save(os.path.join(OUT, "rohan_poor_format.docx"))


# 3) partial resume: right headings but no summary/projects/phone -> PDF
def simple_pdf(path, lines):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for ln in lines:
        pdf.multi_cell(0, 6, ln, new_x="LMARGIN", new_y="NEXT")
    pdf.output(path)


simple_pdf(os.path.join(OUT, "neha_partial.pdf"), [
    "Neha Sharma", "neha.sharma@example.com", "",
    "SKILLS", "Python, SQL, Excel, HTML, CSS, Git",
    "", "EDUCATION", "BCA - Shimla University", "",
    "EXPERIENCE", "Web Intern at Pixel Studio (2024 - 2025)",
    "- Created landing pages using HTML and CSS",
    "- Wrote small Python scripts to automate Excel reports",
])

# 4) mismatched profile (Java / Android) -> PDF
simple_pdf(os.path.join(OUT, "karan_mismatch.pdf"), [
    "Karan Mehta", "karan.mehta@example.com | +91 99887 76655 | github.com/karanmehta", "",
    "SUMMARY", "Android developer with 4 years of experience building consumer mobile apps.", "",
    "SKILLS", "Languages: Java, Kotlin", "Mobile: Android Studio, Firebase, Jira",
    "", "EXPERIENCE", "Android Developer - AppLabs  Jan 2022 - Present",
    "- Developed 6 Android apps with 100000+ downloads using Kotlin and Java",
    "- Integrated Firebase and payment gateways, improving checkout success by 12%", "",
    "EDUCATION", "B.Tech Computer Science - ABC Institute, 2017 - 2021",
])
# 5) well formatted, but written in typical chatbot style (buzzwords, same-length bullets, % everywhere)
ai_style = profile_from_fields({
    "name": "Vikram Rao", "email": "vikram.rao@example.com", "phone": "+91 91234 56780",
    "linkedin": "linkedin.com/in/vikramrao", "github": "github.com/vikramrao",
    "summary": "Results-driven and detail-oriented Python Developer with a proven track record of leveraging "
               "cutting-edge machine learning solutions to drive innovation. Passionate about harnessing "
               "data to deliver robust, scalable and impactful products in a fast-paced environment.",
    "skills": "Languages: Python, SQL\nML & Data: Pandas, NumPy, Scikit-learn, Machine Learning, NLP\n"
              "Backend & Tools: Flask, REST API, MySQL, Git, GitHub, Docker",
    "experience": "Python Developer Intern | TechNova Solutions | Jan 2025 - Jun 2025\n"
                  "- Spearheaded the development of a robust REST API using Flask, resulting in a 40% improvement in system performance\n"
                  "- Leveraged advanced machine learning techniques to analyze large datasets, leading to a 25% increase in prediction accuracy\n"
                  "- Orchestrated seamless database optimization with MySQL, ensuring a 30% reduction in query response time\n"
                  "- Streamlined cross-functional collaboration with stakeholders, thereby enhancing team productivity by 20%",
    "projects": "Smart Recommendation Engine | Python, Scikit-learn | 2025\n"
                "- Engineered a scalable recommendation system leveraging collaborative filtering, resulting in a 35% boost in engagement\n"
                "- Implemented comprehensive data pipelines using Pandas and NumPy, ensuring a 50% faster processing of datasets\n"
                "- Championed best practices in version control with Git, fostering a 15% improvement in code quality",
    "education": "MCA, Himachal Pradesh Technical University | 2024 - 2026\nCGPA: 8.5",
})
build_resume_docx(ai_style, os.path.join(OUT, "vikram_ai_style.docx"))

# 6) plain human style: uneven bullets, concrete details, few round numbers
human = profile_from_fields({
    "name": "Meera Thakur", "email": "meera.thakur@example.com", "phone": "98160 12345",
    "github": "github.com/meerathakur",
    "summary": "MCA student who likes building small tools in Python. Looking for a junior developer role.",
    "skills": "Languages: Python, SQL, Java\nTools: Flask, MySQL, Git, Pandas",
    "experience": "Intern | Hill Soft, Shimla | Jun 2025 - Aug 2025\n"
                  "- Fixed 17 bugs in the Flask admin panel\n"
                  "- Wrote the MySQL queries for the monthly sales report after the old script kept timing out on 8,200 rows\n"
                  "- Helped the senior dev test the login page",
    "projects": "College Library App | Python, Flask, MySQL | 2025\n"
                "- Issue/return screen and fine calculation\n"
                "- Search by title or author; first version was slow, so I added an index on the title column\n"
                "- Used by our department library for about 3 weeks (hosted on a college lab PC)\n"
                "Weather Notes | Python | 2024\n"
                "- Small script that saves daily weather from a free API into a CSV file",
    "education": "MCA, HPTU | 2024 - 2026\nBCA, Govt College Solan | 2021 - 2024",
})
build_resume_docx(human, os.path.join(OUT, "meera_human_style.docx"))
# 7) plain chatbot style: NO heavy buzzwords, but generic wording, "-ing" result endings, no numbers
ai_plain = profile_from_fields({
    "name": "Priya Sharma", "email": "priya.sharma@example.com", "phone": "+91 98765 12345",
    "linkedin": "linkedin.com/in/priyasharma", "github": "github.com/priyasharma",
    "summary": "Motivated and detail-oriented MCA graduate with a strong foundation in Python, SQL, and web "
               "development. Seeking an entry-level Python Developer role to apply technical skills, contribute to "
               "impactful projects, and grow within a dynamic organization.",
    "skills": "Programming Languages: Python, Java, SQL\nFrameworks: Flask, Django\nTools: Git, GitHub, VS Code\n"
              "Soft Skills: Problem-solving, Communication, Teamwork, Time management",
    "projects": "Library Management System | Python, Flask, MySQL\n"
                "- Developed a web-based Library Management System using Python and Flask to manage book records and user transactions efficiently.\n"
                "- Implemented user authentication and role-based access control, enhancing application security and usability.\n"
                "- Designed a responsive user interface using HTML, CSS, and Bootstrap, improving user experience across devices.\n"
                "Weather Forecast Application | Python, REST API\n"
                "- Built a weather application that fetches real-time data using REST APIs and displays results in an intuitive interface.\n"
                "- Utilized JSON parsing and error handling to ensure reliable data retrieval and smooth application performance.\n"
                "- Collaborated with peers to test and refine features, ensuring high-quality deliverables.",
    "education": "MCA, Himachal Pradesh Technical University | 2024 - 2026\nBCA, Government College | 2021 - 2024",
    "certifications": "- Python for Data Science - NPTEL\n- SQL Fundamentals - Coursera",
})
build_resume_docx(ai_plain, os.path.join(OUT, "priya_ai_plain.docx"))

# 8) human style, experienced: specific numbers (not round), uneven bullets, plain wording
human_exp = profile_from_fields({
    "name": "Deepak Chauhan", "email": "deepak.c@example.com", "phone": "+91 98160 99887",
    "github": "github.com/deepakc",
    "summary": "Backend developer, 4 years. Mostly Python and Postgres, some Go. Currently looking at data platform roles.",
    "skills": "Python, Go, PostgreSQL, Airflow, Kafka, Docker, AWS (EC2, S3, RDS)",
    "experience": "Backend Developer | Finlytics | Mar 2022 - Present\n"
                  "- Moved the nightly ETL from cron scripts to Airflow; full run went from about 3h to 40 min\n"
                  "- Wrote a Kafka consumer in Go for payment events, handles ~1.2k msgs/sec on two small pods\n"
                  "- On-call every 4th week. Cut noisy alerts from 60/week to under 10 by fixing two flaky health checks\n"
                  "- Mentored 2 interns on SQL tuning (EXPLAIN ANALYZE, missing indexes)\n"
                  "Junior Developer | Webcraft | Jul 2020 - Feb 2022\n"
                  "- Django + DRF APIs for a logistics client\n"
                  "- Fixed a nasty N+1 query that was making the dashboard take 12s to load",
    "education": "B.Tech CSE, NIT Hamirpur | 2016 - 2020",
})
build_resume_docx(human_exp, os.path.join(OUT, "deepak_human_experienced.docx"))
print("Sample resumes written to", OUT)

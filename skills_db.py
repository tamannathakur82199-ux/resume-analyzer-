"""Skill database, alias map and resume-section dictionaries.

Everything that is "knowledge" (skills, synonyms, section headings, action verbs)
lives here so it can be extended without touching the logic modules.
"""

# category -> list of skills (display names)
SKILLS = {
    "Programming Languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "PHP", "Go",
        "Kotlin", "Swift", "R", "Ruby", "Scala", "Dart", "MATLAB",
    ],
    "Web Development": [
        "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django",
        "Flask", "FastAPI", "Spring Boot", "Bootstrap", "Tailwind CSS", "jQuery",
        "REST API", "GraphQL", "Streamlit",
    ],
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Redis",
        "Firebase", "PL/SQL",
    ],
    "Data Science & AI": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence",
        "Natural Language Processing", "Computer Vision", "Data Analysis",
        "Data Visualization", "Statistics", "Pandas", "NumPy", "Scikit-learn",
        "TensorFlow", "PyTorch", "Keras", "OpenCV", "NLTK", "spaCy", "Power BI",
        "Tableau", "Excel", "Matplotlib", "Generative AI", "LLM", "TF-IDF",
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "CI/CD",
        "Linux", "Git", "GitHub", "Terraform", "Nginx",
    ],
    "CS Fundamentals": [
        "Data Structures", "Algorithms", "OOP", "Operating Systems",
        "Computer Networks", "DBMS", "System Design", "Design Patterns",
        "Software Testing", "Agile", "Scrum",
    ],
    "Tools & Others": [
        "VS Code", "Jira", "Postman", "Selenium", "JUnit", "Android Studio",
        "Figma", "Maven", "Unit Testing",
    ],
}

# alternative spellings -> canonical display name
SKILL_ALIASES = {
    "js": "JavaScript", "JS": "JavaScript", "ecmascript": "JavaScript",
    "ts": "TypeScript", "TS": "TypeScript",
    "golang": "Go", "cpp": "C++", "c plus plus": "C++", "csharp": "C#",
    "reactjs": "React", "react.js": "React", "react js": "React",
    "angularjs": "Angular", "angular.js": "Angular",
    "vue": "Vue.js", "vuejs": "Vue.js", "vue js": "Vue.js",
    "node": "Node.js", "nodejs": "Node.js", "node js": "Node.js",
    "express": "Express.js", "expressjs": "Express.js",
    "springboot": "Spring Boot", "spring": "Spring Boot",
    "tailwind": "Tailwind CSS", "html5": "HTML", "css3": "CSS",
    "rest": "REST API", "restful api": "REST API", "restful apis": "REST API",
    "rest apis": "REST API", "restful services": "REST API",
    "postgres": "PostgreSQL", "postgre sql": "PostgreSQL", "mongo": "MongoDB",
    "mongo db": "MongoDB", "my sql": "MySQL", "plsql": "PL/SQL",
    "ml": "Machine Learning", "ML": "Machine Learning",
    "dl": "Deep Learning", "DL": "Deep Learning",
    "ai": "Artificial Intelligence", "AI": "Artificial Intelligence",
    "nlp": "Natural Language Processing", "cv": "Computer Vision",
    "genai": "Generative AI", "gen ai": "Generative AI", "llms": "LLM",
    "large language models": "LLM", "large language model": "LLM",
    "tfidf": "TF-IDF", "tf idf": "TF-IDF", "tf-idf": "TF-IDF",
    "sklearn": "Scikit-learn", "scikit learn": "Scikit-learn",
    "scikitlearn": "Scikit-learn", "tensor flow": "TensorFlow",
    "py torch": "PyTorch", "numpy": "NumPy", "num py": "NumPy",
    "open cv": "OpenCV", "powerbi": "Power BI", "ms excel": "Excel",
    "microsoft excel": "Excel", "data analytics": "Data Analysis",
    "data visualisation": "Data Visualization", "statistical analysis": "Statistics",
    "amazon web services": "AWS", "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud", "microsoft azure": "Azure",
    "k8s": "Kubernetes", "kubernets": "Kubernetes", "cicd": "CI/CD",
    "ci cd": "CI/CD", "ubuntu": "Linux", "unix": "Linux", "github actions": "CI/CD",
    "dsa": "Data Structures", "data structure": "Data Structures",
    "data structures and algorithms": "Data Structures",
    "algorithm": "Algorithms", "oops": "OOP", "oop": "OOP",
    "object oriented programming": "OOP", "object-oriented programming": "OOP",
    "object oriented": "OOP", "object-oriented": "OOP",
    "os": "Operating Systems", "operating system": "Operating Systems",
    "cn": "Computer Networks", "computer network": "Computer Networks",
    "networking": "Computer Networks", "database management system": "DBMS",
    "database management systems": "DBMS", "rdbms": "DBMS",
    "vscode": "VS Code", "visual studio code": "VS Code",
    "testing": "Software Testing", "agile methodology": "Agile",
    "junit5": "JUnit", "scrum master": "Scrum",
}

# terms that must match with the exact case (too ambiguous otherwise)
CASE_SENSITIVE_EXTRA = {"Excel", "Go"}


def is_case_sensitive(term: str) -> bool:
    return len(term) <= 2 or term in CASE_SENSITIVE_EXTRA


# canonical display name -> category
SKILL_CATEGORY = {s: cat for cat, items in SKILLS.items() for s in items}
ALL_SKILLS = list(SKILL_CATEGORY.keys())

# section key -> accepted heading texts (lower case, letters/space only)
SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "career summary", "objective",
                "career objective", "profile", "professional profile", "about me",
                "about", "personal statement"],
    "skills": ["skills", "technical skills", "key skills", "core skills",
               "core competencies", "skills and tools", "skills and technologies",
               "tech stack", "technical proficiency", "technologies", "expertise",
               "areas of expertise"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment history", "work history", "internship",
                   "internships", "internship experience", "industrial training",
                   "employment", "career history",
                   "work experience internships", "work experience and internships",
                   "experience and internships", "internships and experience",
                   "work experience internship"],
    "education": ["education", "academic qualifications", "academic background",
                  "educational qualifications", "academics", "qualifications",
                  "educational background", "academic details"],
    "projects": ["projects", "academic projects", "personal projects", "key projects",
                 "project work", "major projects", "project experience",
                 "technical projects"],
    "certifications": ["certifications", "certificates", "certification",
                       "licenses and certifications", "courses", "training",
                       "courses and certifications", "online courses"],
    "achievements": ["achievements", "awards", "honors", "honours", "accomplishments",
                     "awards and achievements", "extracurricular activities",
                     "extra curricular activities", "positions of responsibility",
                     "leadership", "co curricular activities"],
    "other": ["languages", "interests", "hobbies", "declaration", "references",
              "personal details", "personal information", "strengths"],
}

SECTION_TITLES = {
    "summary": "Professional Summary",
    "skills": "Technical Skills",
    "experience": "Work Experience / Internships",
    "education": "Education",
    "projects": "Projects",
    "certifications": "Certifications",
    "achievements": "Achievements",
}

ACTION_VERBS = {
    "achieved", "analyzed", "analysed", "architected", "automated", "built",
    "collaborated", "configured", "contributed", "created", "debugged", "delivered",
    "deployed", "designed", "developed", "devised", "documented", "engineered",
    "enhanced", "established", "evaluated", "executed", "implemented", "improved",
    "increased", "integrated", "launched", "led", "maintained", "managed",
    "migrated", "modeled", "monitored", "optimized", "optimised", "organized",
    "performed", "planned", "presented", "reduced", "refactored", "researched",
    "resolved", "reviewed", "scaled", "secured", "simplified", "solved",
    "streamlined", "supported", "tested", "trained", "transformed", "tuned",
    "upgraded", "utilized", "won", "wrote", "coordinated", "mentored", "applied",
    "extracted", "generated", "visualized", "parsed", "ranked", "processed",
}

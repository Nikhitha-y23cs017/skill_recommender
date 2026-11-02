import pandas as pd
from urllib.parse import quote_plus

# Run this script from the folder that contains raw_skills.csv.
# It creates career_dataset.csv in the same folder.
# IMPORTANT: This uses complete skill phrases. Do NOT split skills by spaces.

INPUT_FILE = "raw_skills.csv"
OUTPUT_FILE = "career_dataset.csv"

# Curated skill phrases for each role. Multi-word skills remain together.
ROLE_SKILLS = {
    "Data Scientist": [
        "Python", "SQL", "machine learning", "statistics", "Pandas", "NumPy",
        "data analysis", "data visualization"
    ],
    "Machine Learning Engineer": [
        "Python", "machine learning", "deep learning", "algorithms",
        "model deployment", "data structures"
    ],
    "AI Engineer": [
        "Python", "artificial intelligence", "machine learning",
        "natural language processing", "computer vision", "deep learning"
    ],
    "Data Analyst": [
        "SQL", "Excel", "Python", "data analysis", "data visualization",
        "statistics", "dashboards", "business intelligence"
    ],
    "Backend Developer": [
        "Python", "Java", "SQL", "API development", "databases",
        "data structures", "algorithms", "backend development"
    ],
    "Frontend Developer": [
        "HTML", "CSS", "JavaScript", "React", "user interface design",
        "responsive design", "web development"
    ],
    "Full Stack Developer": [
        "HTML", "CSS", "JavaScript", "React", "Python", "SQL",
        "API development", "databases", "web development"
    ],
    "Mobile Developer": [
        "Java", "Kotlin", "Flutter", "Dart", "mobile development",
        "API integration", "user interface design", "Android development"
    ],
    "DevOps Engineer": [
        "Linux", "Git", "Docker", "Kubernetes", "cloud computing",
        "automation", "CI/CD", "networking", "scripting"
    ],
    "Cloud Engineer": [
        "cloud computing", "AWS", "Azure", "Linux", "networking",
        "Docker", "automation", "security", "infrastructure"
    ],
    "Cloud Architect": [
        "cloud computing", "cloud architecture", "AWS", "Azure",
        "networking", "security", "scalability", "infrastructure design"
    ],
    "Site Reliability Engineer": [
        "Linux", "cloud computing", "monitoring", "automation",
        "Kubernetes", "Docker", "networking", "reliability engineering",
        "scripting"
    ],
    "Cybersecurity Analyst": [
        "cybersecurity", "networking", "Linux", "incident response",
        "security monitoring", "threat analysis", "vulnerability analysis",
        "SIEM"
    ],
    "Penetration Tester": [
        "cybersecurity", "networking", "Linux", "ethical hacking",
        "vulnerability testing", "web security", "scripting"
    ],
    "Security Engineer": [
        "cybersecurity", "networking", "cloud security", "Linux",
        "firewalls", "automation", "incident response", "security architecture"
    ],
    "Database Administrator": [
        "SQL", "databases", "MySQL", "PostgreSQL", "backup and recovery",
        "database performance", "database security", "Linux"
    ],
    "QA Automation Engineer": [
        "software testing", "Python", "Selenium", "test automation",
        "API testing", "software quality", "Git"
    ],
    "Business Intelligence Developer": [
        "SQL", "data analysis", "dashboards", "business intelligence",
        "data visualization", "databases", "ETL"
    ],
    "NLP Engineer": [
        "Python", "natural language processing", "machine learning",
        "deep learning", "text analysis", "transformers"
    ],
    "Computer Vision Engineer": [
        "Python", "computer vision", "deep learning", "image processing",
        "machine learning", "neural networks"
    ],
}

def make_resource(skill):
    # This is a search link, not a claim that one specific course is endorsed.
    query = quote_plus(f"{skill} free tutorial")
    return f"Free {skill} tutorials", f"https://www.youtube.com/results?search_query={query}"

def main():
    try:
        source = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"ERROR: Cannot find {INPUT_FILE}.")
        print("Place convert_dataset.py and raw_skills.csv in the same project folder.")
        return

    if "role" not in source.columns:
        print("ERROR: raw_skills.csv must contain a 'role' column.")
        print("Found columns:", list(source.columns))
        return

    rows = []
    for role in source["role"].dropna().astype(str):
        skills = ROLE_SKILLS.get(role.strip())

        if not skills:
            print(f"WARNING: No curated skill list found for: {role}")
            continue

        for skill in skills:
            course, url = make_resource(skill)
            rows.append({
                "career": role.strip(),
                "skill": skill,
                "course": course,
                "url": url
            })

    result = pd.DataFrame(rows, columns=["career", "skill", "course", "url"])
    result.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"SUCCESS: Created {OUTPUT_FILE}")
    print(f"Careers included: {result['career'].nunique()}")
    print(f"Career-skill rows created: {len(result)}")
    print("\nSample rows:")
    print(result.head(12).to_string(index=False))
    print("\nMulti-word skills such as 'machine learning' and 'data analysis' are preserved.")

if __name__ == "__main__":
    main()

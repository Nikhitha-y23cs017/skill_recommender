
import csv
from pathlib import Path

base = Path(__file__).parent
source = base / "raw_skills.csv"
output = base / "career_dataset.csv"

if not source.exists():
    raise FileNotFoundError(
        "Place raw_skills.csv inside your career project folder."
    )

count = 0
seen = set()

with open(source, "r", encoding="utf-8-sig", newline="") as infile, \
     open(output, "w", encoding="utf-8-sig", newline="") as outfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    writer.writerow(["career", "skill", "course", "url"])

    for row in reader:
        career = row["role"].strip()
        skills = row["skills"].strip()

        for skill in skills.split():
            skill = skill.strip(" ,;")
            if not skill:
                continue

            key = (career.lower(), skill.lower())
            if key in seen:
                continue

            seen.add(key)

            writer.writerow([
                career,
                skill,
                "Learn " + skill,
                "https://www.google.com/search?q=learn+" +
                skill.replace(" ", "+")
            ])
            count += 1

print("Dataset converted successfully!")
print("Career-skill rows:", count)
print("Output:", output)

import os
import json
import re

SECTIONS_DIR = "sections"
OUTPUT_FILE = "cv.json"

# Helper to read markdown file
def read_md(filename):
    with open(os.path.join(SECTIONS_DIR, filename), encoding="utf-8") as f:
        return f.read()

# Extract introduction (first paragraph)
def extract_introduction(md):
    match = re.search(r"# Introduction\n+(.+?)(?:\n---|$)", md, re.DOTALL)
    return match.group(1).strip().replace("\n", " ") if match else ""

# Extract skills (primary, full stack, testing)
def extract_skills(md):
    skills = {}
    # Primary
    primary = re.findall(r"- (.+)", re.search(r"#### Primary(.+?)####", md, re.DOTALL).group(1))
    skills["primary"] = primary
    # Full stack
    fs = {}
    for key in ["frontend", "frameworks", "backend", "databases", "programming", "ssg"]:
        fs[key] = re.findall(rf"\*\*{key.capitalize()}\*\*: (.+)", md)
        if fs[key]:
            fs[key] = [x.strip() for x in re.split(r",\s*", fs[key][0])]
        else:
            fs[key] = []
    skills["full_stack"] = fs
    # Testing
    testing = {}
    for key in ["frameworks", "tools", "performance", "observability"]:
        block = re.search(rf"#### Testing(.+?)#### Tools", md, re.DOTALL)
        if block:
            testing[key] = re.findall(rf"- \*\*{key.capitalize()}\*\*: (.+)", block.group(1))
            if testing[key]:
                testing[key] = [x.strip() for x in re.split(r",\s*", testing[key][0])]
            else:
                testing[key] = []
        else:
            testing[key] = []
    skills["testing"] = testing
    return skills

# Extract work experience (first 3 roles)
def extract_work_experience(md):
    roles = []
    for match in re.finditer(r"### (.+)\n\*\*(.+)\*\* - (.+) \((.+)\)([\s\S]*?)(?=###|$)", md):
        title, company, location, dates, details = match.groups()
        highlights = re.findall(r"- (.+)", details)
        roles.append({
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "dates": dates.strip(),
            "highlights": highlights
        })
        if len(roles) == 3:
            break
    return roles

# Extract education (first 2 entries)
def extract_education(md):
    entries = []
    for match in re.finditer(r"- \*\*(.+)\*\* from \*\*(.+)\*\*, (.+) \((.+)\)", md):
        degree, institution, location, dates = match.groups()
        entries.append({
            "degree": degree.strip(),
            "institution": institution.strip(),
            "location": location.strip(),
            "dates": dates.strip()
        })
        if len(entries) == 2:
            break
    return entries

# Extract languages
def extract_languages(md):
    return re.findall(r"- (.+) \((.+)\)", md)

if __name__ == "__main__":
    intro_md = read_md("Introduction.md")
    skills_md = read_md("Skills.md")
    work_md = read_md("Work-Experience.md")
    edu_md = read_md("Education.md")

    data = {
        "introduction": extract_introduction(intro_md),
        "skills": extract_skills(skills_md),
        "work_experience": extract_work_experience(work_md),
        "education": extract_education(edu_md),
        "languages": [
            {"language": lang, "level": level} for lang, level in extract_languages(edu_md)
        ],
        "projects": "Available upon request"
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Generated {OUTPUT_FILE} from markdown files.")

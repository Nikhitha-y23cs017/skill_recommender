
import csv
from pathlib import Path

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

st.set_page_config(
    page_title="KG Career Guidance",
    page_icon="🎯",
    layout="wide"
)

BASE_DIR = Path(__file__).parent


def load_careers():
    careers = {}
    path = BASE_DIR / "career_dataset.csv"

    if not path.exists():
        return careers

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            career = row.get("career", "").strip()
            skill = row.get("skill", "").strip()

            if not career or not skill:
                continue

            careers.setdefault(
                career,
                {"skills": [], "courses": {}}
            )

            if skill.lower() not in [
                item.lower() for item in careers[career]["skills"]
            ]:
                careers[career]["skills"].append(skill)

            careers[career]["courses"][skill] = (
                row.get("course", "").strip(),
                row.get("url", "").strip()
            )

    return careers


def load_resources():
    resources = {}
    path = BASE_DIR / "learning_resources.csv"

    if not path.exists():
        return resources

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            skill = row.get("skill", "").strip().lower()

            if not skill:
                continue

            resources.setdefault(skill, [])
            resources[skill].append({
                "platform": row.get("platform", "").strip(),
                "name": row.get("resource_name", "").strip(),
                "url": row.get("url", "").strip(),
                "type": row.get("resource_type", "").strip()
            })

    return resources


CAREERS = load_careers()
RESOURCES = load_resources()

st.title("🎯 Knowledge Graph-Based Career Guidance")
st.write(
    "Discover suitable technology careers, identify missing skills, "
    "and find learning resources through an interactive knowledge graph."
)

if not CAREERS:
    st.error(
        "career_dataset.csv was not found or contains no valid data. "
        "Place it in the same folder as app.py."
    )
    st.stop()


all_skills = sorted({
    skill
    for details in CAREERS.values()
    for skill in details["skills"]
})


# Interest keywords are matched against the actual career titles.
# Add more keywords here if your dataset uses different job titles.
interest_map = {
    "Software Development": [
        "software", "developer", "programmer", "application engineer"
    ],
    "Backend Development": [
        "backend", "back-end", "server-side"
    ],
    "Frontend Development": [
        "frontend", "front-end", "ui developer", "web designer"
    ],
    "Full Stack Development": [
        "full stack", "full-stack"
    ],
    "Web Development": [
        "web developer", "web development", "frontend", "full stack"
    ],
    "Mobile App Development": [
        "mobile developer", "android", "ios developer", "mobile app"
    ],
    "Java Development": [
        "java developer", "java engineer", "backend developer"
    ],
    "Python Development": [
        "python developer", "python engineer", "backend developer"
    ],
    "Data Analysis": [
        "data analyst", "business intelligence", "data scientist"
    ],
    "Data Science": [
        "data scientist", "data science"
    ],
    "Business Intelligence": [
        "business intelligence", "bi developer", "data analyst"
    ],
    "Artificial Intelligence": [
        "ai engineer", "artificial intelligence", "machine learning",
        "nlp engineer", "computer vision"
    ],
    "Machine Learning": [
        "machine learning", "ml engineer", "data scientist", "ai engineer"
    ],
    "Natural Language Processing": [
        "nlp", "language model"
    ],
    "Computer Vision": [
        "computer vision", "vision engineer"
    ],
    "Generative AI": [
        "generative ai", "llm", "nlp engineer", "ai engineer"
    ],
    "Cloud Computing": [
        "cloud engineer", "cloud architect", "site reliability", "devops"
    ],
    "Cloud Architecture": [
        "cloud architect", "cloud engineer"
    ],
    "DevOps": [
        "devops", "site reliability", "infrastructure engineer"
    ],
    "Cybersecurity": [
        "cybersecurity", "security engineer", "penetration tester"
    ],
    "Ethical Hacking": [
        "penetration tester", "ethical hacker", "security analyst"
    ],
    "Database Management": [
        "database administrator", "database engineer", "data engineer"
    ],
    "Data Engineering": [
        "data engineer", "database engineer"
    ],
    "Software Testing": [
        "qa", "test engineer", "software tester", "quality assurance"
    ],
    "QA Automation": [
        "qa automation", "automation tester", "test automation"
    ],
    "Networking": [
        "network engineer", "network administrator", "cybersecurity"
    ],
    "System Administration": [
        "system administrator", "systems engineer", "linux administrator"
    ],
    "Research and Development": [
        "research", "machine learning", "data scientist", "ai engineer"
    ],
    "IT Support": [
        "it support", "technical support", "help desk"
    ],
    "Blockchain Development": [
        "blockchain", "smart contract", "web3"
    ],
    "Game Development": [
        "game developer", "game programmer", "unity developer"
    ],
    "UI/UX Design": [
        "ui/ux", "ux designer", "ui designer", "product designer"
    ]
}


st.sidebar.header("👩‍🎓 Student Profile")

interests = st.sidebar.multiselect(
    "What are your interests?",
    options=list(interest_map.keys()),
    help="Select one or more career areas you are interested in."
)

known_skills = st.sidebar.multiselect(
    "Which skills do you already know?",
    options=all_skills
)

top_n = st.sidebar.slider(
    "Number of careers to recommend",
    min_value=3,
    max_value=max(3, min(20, len(CAREERS))),
    value=min(5, max(3, len(CAREERS)))
)


def get_interest_score(career, selected_interests):
    if not selected_interests:
        return 0.0

    title = career.lower()
    relevant = 0

    for interest in selected_interests:
        keywords = interest_map[interest]

        if any(keyword in title for keyword in keywords):
            relevant += 1

    return relevant / len(selected_interests)


if st.sidebar.button("Recommend Careers", type="primary"):
    results = []

    selected_skills = {skill.lower() for skill in known_skills}

    for career, details in CAREERS.items():
        required = set(details["skills"])

        matched = {
            skill for skill in required
            if skill.lower() in selected_skills
        }

        missing = required - matched

        interest_score = get_interest_score(career, interests)
        skill_score = len(matched) / len(required) if required else 0.0

        if interests and known_skills:
            score = 0.7 * interest_score + 0.3 * skill_score
        elif interests:
            score = interest_score
        elif known_skills:
            score = skill_score
        else:
            score = 0.0

        results.append({
            "career": career,
            "score": score,
            "matched": sorted(matched),
            "missing": sorted(missing),
            "interest_score": interest_score,
            "skill_score": skill_score
        })

    results.sort(
        key=lambda item: (
            item["score"],
            item["interest_score"],
            item["skill_score"]
        ),
        reverse=True
    )

    st.session_state["results"] = results
    st.session_state["top_n"] = top_n


if "results" in st.session_state:
    results = st.session_state["results"]
    number_to_show = st.session_state.get("top_n", 5)
    shown_results = results[:number_to_show]

    st.subheader("🏆 Recommended Careers")

    if not interests and not known_skills:
        st.info(
            "Select your interests or known skills in the sidebar, "
            "then click Recommend Careers for personalized results."
        )

    for item in shown_results:
        career = item["career"]
        details = CAREERS[career]

        with st.expander(
            f'{career} — Match score: {item["score"]:.0%}'
        ):
            st.write("**Skills you already know**")
            st.write(", ".join(item["matched"]) or "None selected")

            st.write("**Skills to learn**")
            st.write(
                ", ".join(item["missing"])
                or "No skill gaps in this dataset"
            )

            st.write("**Learning resources**")

            for skill in item["missing"]:
                skill_resources = RESOURCES.get(skill.lower(), [])

                if skill_resources:
                    for resource in skill_resources:
                        if resource["url"]:
                            st.markdown(
                                f'- **{skill}** — '
                                f'[{resource["name"]}]({resource["url"]}) '
                                f'({resource["platform"]})'
                            )
                elif skill in details["courses"]:
                    name, url = details["courses"][skill]

                    if url:
                        st.markdown(f"- **{skill}** — [{name}]({url})")
                    else:
                        st.write(f"- {skill}: {name}")
                else:
                    st.write(
                        f"- {skill}: No resource mapped yet. "
                        "Add one to learning_resources.csv."
                    )

    st.subheader("🕸️ Knowledge Graph")

    graph = nx.Graph()
    graph.add_node("Student", kind="student")

    for item in shown_results:
        career = item["career"]

        graph.add_node(career, kind="career")
        graph.add_edge("Student", career, relation="recommended career")

        for skill in CAREERS[career]["skills"]:
            graph.add_node(skill, kind="skill")
            graph.add_edge(career, skill, relation="requires")

            if skill in item["missing"]:
                resources = RESOURCES.get(skill.lower(), [])
                fallback = CAREERS[career]["courses"].get(skill)

                resource_name = None
                resource_url = ""

                if resources:
                    resource_name = resources[0]["name"]
                    resource_url = resources[0]["url"]
                elif fallback:
                    resource_name, resource_url = fallback

                if resource_name:
                    graph.add_node(
                        resource_name,
                        kind="resource",
                        url=resource_url
                    )
                    graph.add_edge(
                        skill,
                        resource_name,
                        relation="learn through"
                    )

    net = Network(
        height="550px",
        width="100%",
        bgcolor="#111827",
        font_color="white"
    )

    net.barnes_hut()

    colors = {
        "student": "#F59E0B",
        "career": "#60A5FA",
        "skill": "#34D399",
        "resource": "#F472B6"
    }

    for node, data in graph.nodes(data=True):
        net.add_node(
            node,
            label=node,
            title=data["kind"].title(),
            color=colors[data["kind"]]
        )

    for source, target, data in graph.edges(data=True):
        net.add_edge(source, target, title=data["relation"])

    html = net.generate_html()
    components.html(html, height=570, scrolling=True)

    st.caption(
        "Yellow: Student | Blue: Career | Green: Skill | "
        "Pink: Learning resource"
    )

st.divider()

st.caption(
    "Prototype: recommendations use selected interests and known skills. "
    "Match scores are estimates based on the supplied career dataset, "
    "not guarantees of job suitability."
)

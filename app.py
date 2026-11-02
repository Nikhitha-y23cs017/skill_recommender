
import csv
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network


st.set_page_config(
    page_title="KG Career Guidance",
    page_icon="🎯",
    layout="wide"
)

BASE_DIR = Path(__file__).parent


# -------------------- LOAD CAREER DATA --------------------

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

            careers.setdefault(career, {"skills": [], "courses": {}})

            if skill.lower() not in {
                item.lower() for item in careers[career]["skills"]
            }:
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


# -------------------- PAGE HEADER --------------------

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


# -------------------- INTEREST TO CAREER MAPPING --------------------

career_interest_map = {
    "Software Development": [
        "Backend Developer", "Frontend Developer",
        "Full Stack Developer", "Mobile Developer",
        "QA Automation Engineer"
    ],
    "Backend Development": ["Backend Developer"],
    "Frontend Development": ["Frontend Developer"],
    "Full Stack Development": ["Full Stack Developer"],
    "Web Development": [
        "Frontend Developer", "Full Stack Developer"
    ],
    "Mobile App Development": ["Mobile Developer"],
    "Java Development": [
        "Backend Developer", "Mobile Developer"
    ],
    "Python Development": [
        "Data Scientist", "Machine Learning Engineer",
        "AI Engineer", "Data Analyst", "Backend Developer",
        "NLP Engineer", "Computer Vision Engineer"
    ],
    "Data Analysis": [
        "Data Analyst", "Data Scientist",
        "Business Intelligence Developer"
    ],
    "Data Science": ["Data Scientist"],
    "Business Intelligence": [
        "Business Intelligence Developer", "Data Analyst"
    ],
    "Artificial Intelligence": [
        "AI Engineer", "Machine Learning Engineer",
        "Data Scientist", "NLP Engineer",
        "Computer Vision Engineer"
    ],
    "Machine Learning": [
        "Machine Learning Engineer", "Data Scientist",
        "AI Engineer", "NLP Engineer",
        "Computer Vision Engineer"
    ],
    "Natural Language Processing": ["NLP Engineer"],
    "Computer Vision": ["Computer Vision Engineer"],
    "Generative AI": [
        "AI Engineer", "NLP Engineer",
        "Machine Learning Engineer"
    ],
    "Cloud Computing": [
        "Cloud Engineer", "Cloud Architect",
        "DevOps Engineer", "Site Reliability Engineer"
    ],
    "Cloud Architecture": ["Cloud Architect"],
    "DevOps": [
        "DevOps Engineer", "Site Reliability Engineer"
    ],
    "Cybersecurity": [
        "Cybersecurity Analyst", "Security Engineer",
        "Penetration Tester"
    ],
    "Ethical Hacking": ["Penetration Tester"],
    "Database Management": ["Database Administrator"],
    "Data Engineering": [
        "Database Administrator",
        "Business Intelligence Developer"
    ],
    "Software Testing": ["QA Automation Engineer"],
    "QA Automation": ["QA Automation Engineer"],
    "Networking": [
        "Cloud Engineer", "DevOps Engineer",
        "Cybersecurity Analyst", "Security Engineer",
        "Site Reliability Engineer"
    ],
    "System Administration": [
        "Site Reliability Engineer", "Cloud Engineer",
        "DevOps Engineer"
    ],
    "Research and Development": [
        "Data Scientist", "Machine Learning Engineer",
        "AI Engineer", "NLP Engineer",
        "Computer Vision Engineer"
    ],
    "IT Support": [
        "Cybersecurity Analyst", "Database Administrator",
        "Cloud Engineer"
    ],
    "Blockchain Development": [],
    "Game Development": [],
    "UI/UX Design": ["Frontend Developer"]
}


# -------------------- STUDENT PROFILE --------------------

st.sidebar.header("👩‍🎓 Student Profile")

interests = st.sidebar.multiselect(
    "What are your interests?",
    options=list(career_interest_map.keys()),
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


# -------------------- RECOMMENDATION FUNCTIONS --------------------

def normalized_skill(skill):
    return " ".join(skill.strip().lower().split())


def get_interest_score(career, selected_interests):
    if not selected_interests:
        return 0.0

    career_name = career.strip().lower()
    matched_interests = 0

    for interest in selected_interests:
        related_careers = career_interest_map.get(interest, [])
        related_titles = {
            name.strip().lower() for name in related_careers
        }

        if career_name in related_titles:
            matched_interests += 1

    return matched_interests / len(selected_interests)


# -------------------- GENERATE RECOMMENDATIONS --------------------

if st.sidebar.button("Recommend Careers", type="primary"):
    results = []
    selected_skills = {
        normalized_skill(skill) for skill in known_skills
    }

    if not interests and not known_skills:
        st.session_state["results"] = []
        st.session_state["top_n"] = top_n
        st.session_state["needs_profile"] = True

    else:
        st.session_state["needs_profile"] = False

        for career, details in CAREERS.items():
            required = details["skills"]

            required_by_normalized = {
                normalized_skill(skill): skill
                for skill in required
            }

            matched_normalized = (
                set(required_by_normalized) & selected_skills
            )

            matched = {
                required_by_normalized[skill]
                for skill in matched_normalized
            }

            missing = set(required) - matched

            interest_score = get_interest_score(career, interests)
            skill_score = (
                len(matched) / len(required) if required else 0.0
            )

            if interests and known_skills:
                score = (
                    0.60 * interest_score
                    + 0.40 * skill_score
                )
            elif interests:
                score = interest_score
            else:
                score = skill_score

            results.append({
                "career": career,
                "score": score,
                "matched": sorted(matched, key=str.lower),
                "missing": sorted(missing, key=str.lower),
                "interest_score": interest_score,
                "skill_score": skill_score
            })

        results.sort(
            key=lambda item: (
                item["score"],
                item["interest_score"],
                item["skill_score"],
                -len(item["missing"])
            ),
            reverse=True
        )

        st.session_state["results"] = results
        st.session_state["top_n"] = top_n


# -------------------- DISPLAY CAREER RESULTS --------------------

if "results" in st.session_state:
    results = st.session_state["results"]
    number_to_show = st.session_state.get("top_n", 5)
    shown_results = results[:number_to_show]

    st.subheader("🏆 Recommended Careers")

    if st.session_state.get("needs_profile", False):
        st.info(
            "Select your interests or known skills in the sidebar, "
            "then click Recommend Careers."
        )

    elif shown_results:

        for item in shown_results:
            career = item["career"]
            details = CAREERS[career]

            with st.expander(
                f'{career} — Match score: {item["score"]:.0%}'
            ):
                st.write("**Why this career was recommended**")

                st.write(
                    f'Interest match: {item["interest_score"]:.0%} | '
                    f'Skill match: {item["skill_score"]:.0%}'
                )

                readiness = max(
                    0.0, min(1.0, float(item["skill_score"]))
                )

                total_required = len(details["skills"])
                matched_count = len(item["matched"])

                st.write("**Career skill readiness**")
                st.progress(readiness)

                st.write(
                    f"{matched_count} of {total_required} required "
                    f"skills matched ({readiness:.0%} readiness)"
                )

                st.write("**Skills you already know**")
                st.write(", ".join(item["matched"]) or "None selected")

                st.write("**Skills to learn**")
                st.write(
                    ", ".join(item["missing"])
                    or "No skill gaps in this dataset"
                )

                # ---------- LEARNING RESOURCES ----------

                st.write("**Learning resources**")

                for skill in item["missing"]:
                    skill_resources = RESOURCES.get(
                        normalized_skill(skill), []
                    )

                    if skill_resources:
                        for resource in skill_resources:
                            name = resource["name"] or resource["platform"]
                            url = resource["url"]
                            platform = resource["platform"]

                            if url:
                                st.markdown(
                                    f'- **{skill}** — '
                                    f'[{name}]({url}) ({platform})'
                                )
                            elif name:
                                st.write(f"- **{skill}** — {name}")

                    elif skill in details["courses"]:
                        name, url = details["courses"][skill]

                        if url:
                            st.markdown(
                                f"- **{skill}** — [{name or skill}]({url})"
                            )
                        elif name:
                            st.write(f"- **{skill}**: {name}")
                        else:
                            st.write(
                                f"- **{skill}**: No resource URL available."
                            )

                    else:
                        st.write(
                            f"- **{skill}**: No resource mapped yet. "
                            "Add one to learning_resources.csv."
                        )

                # ---------- PERSONALIZED ROADMAP ----------

                st.write("### 🗺️ Your Personalized Learning Roadmap")

                missing_in_dataset_order = [
                    skill for skill in details["skills"]
                    if skill in item["missing"]
                ]

                if not missing_in_dataset_order:
                    st.success(
                        "You have matched every required skill in this "
                        "dataset. Next, build a project and practise "
                        "interview questions."
                    )

                else:
                    phase_count = min(
                        3, len(missing_in_dataset_order)
                    )

                    phase_names = [
                        "Phase 1 — Start here",
                        "Phase 2 — Build your skills",
                        "Phase 3 — Practice and specialize"
                    ]

                    phases = [[] for _ in range(phase_count)]

                    for index, skill in enumerate(
                        missing_in_dataset_order
                    ):
                        phase_index = min(
                            index * phase_count
                            // len(missing_in_dataset_order),
                            phase_count - 1
                        )
                        phases[phase_index].append(skill)

                    for phase_index, phase_skills in enumerate(phases):
                        with st.container(border=True):
                            st.write(f"**{phase_names[phase_index]}**")

                            for skill in phase_skills:
                                st.write(f"- [ ] **{skill}**")

                                skill_resources = RESOURCES.get(
                                    normalized_skill(skill), []
                                )

                                if skill_resources:
                                    resource = skill_resources[0]

                                    if resource["url"]:
                                        st.markdown(
                                            f'  [Start learning: '
                                            f'{resource["name"] or skill}]'
                                            f'({resource["url"]})'
                                        )
                                    elif resource["name"]:
                                        st.caption(
                                            f'  Resource: {resource["name"]}'
                                        )

                                else:
                                    fallback = details["courses"].get(skill)

                                    if fallback and fallback[1]:
                                        st.markdown(
                                            f"  [Start learning: "
                                            f"{fallback[0] or skill}]"
                                            f"({fallback[1]})"
                                        )
                                    else:
                                        st.caption(
                                            "Add a learning link for this "
                                            "skill in learning_resources.csv."
                                        )

                    st.info(
                        "Roadmap order is a suggested sequence based on "
                        "your dataset's skill order. It is not a verified "
                        "prerequisite map."
                    )

        # =========================================================
        # NEO4J-STYLE KNOWLEDGE GRAPH
        # =========================================================

        st.subheader("🕸️ Knowledge Graph")

        st.caption(
            "Explore how your profile connects to interests, recommended "
            "careers, required skills, and learning resources."
        )

        net = Network(
            height="670px",
            width="100%",
            bgcolor="#0B1220",
            font_color="#F8FAFC",
            directed=True,
            cdn_resources="in_line"
        )

        net.barnes_hut(
            gravity=-28000,
            central_gravity=0.25,
            spring_length=180,
            spring_strength=0.025,
            damping=0.09
        )

        colors = {
            "student": "#F59E0B",
            "interest": "#A78BFA",
            "career": "#60A5FA",
            "known_skill": "#34D399",
            "missing_skill": "#FB7185",
            "resource": "#F472B6"
        }

        added_nodes = set()

        def add_graph_node(node_id, label, kind, title=None):
            if node_id in added_nodes:
                return

            net.add_node(
                node_id,
                label=label,
                title=title or kind.replace("_", " ").title(),
                color={
                    "background": colors[kind],
                    "border": "#E2E8F0",
                    "highlight": {
                        "background": colors[kind],
                        "border": "#FFFFFF"
                    }
                },
                shape="dot",
                size=28 if kind in ("student", "career") else 20,
                borderWidth=2,
                font={
                    "size": 16,
                    "face": "Arial",
                    "color": "#F8FAFC"
                }
            )

            added_nodes.add(node_id)

        def add_graph_edge(source, target, relation):
            net.add_edge(
                source,
                target,
                label=relation,
                title=relation,
                arrows="to",
                color={
                    "color": "#94A3B8",
                    "highlight": "#F8FAFC"
                },
                font={
                    "size": 11,
                    "color": "#CBD5E1",
                    "strokeWidth": 3,
                    "strokeColor": "#0B1220"
                },
                smooth={"type": "dynamic"}
            )

        # Student node
        add_graph_node(
            "student", "Student", "student", "Your profile"
        )

        # Student -> Interests
        for interest_index, interest in enumerate(interests):
            interest_id = f"interest::{interest_index}::{interest}"

            add_graph_node(
                interest_id, interest, "interest", "Selected interest"
            )

            add_graph_edge(
                "student", interest_id, "INTERESTED_IN"
            )

        # Student -> Known skills
        known_skill_ids = {}

        for skill in known_skills:
            skill_key = normalized_skill(skill)
            skill_id = f"known_skill::{skill_key}"

            known_skill_ids[skill_key] = skill_id

            add_graph_node(
                skill_id, skill, "known_skill",
                "Skill you selected as known"
            )

            add_graph_edge("student", skill_id, "HAS_SKILL")

        # Careers -> Required skills -> Learning resources
        for career_index, item in enumerate(shown_results):
            career = item["career"]
            career_id = f"career::{career_index}::{career}"

            add_graph_node(
                career_id,
                career,
                "career",
                f'Match score: {item["score"]:.0%} | '
                f'Skill readiness: {item["skill_score"]:.0%}'
            )

            add_graph_edge(
                "student", career_id, "RECOMMENDED"
            )

            matched_keys = {
                normalized_skill(skill)
                for skill in item["matched"]
            }

            for skill_index, skill in enumerate(CAREERS[career]["skills"]):
                skill_key = normalized_skill(skill)

                if skill_key in matched_keys:
                    kind = "known_skill"
                    skill_id = known_skill_ids.get(
                        skill_key, f"known_skill::{skill_key}"
                    )
                    relation = "HAS_SKILL"

                    add_graph_node(
                        skill_id, skill, kind,
                        "Skill matched to this career"
                    )

                else:
                    kind = "missing_skill"
                    skill_id = (
                        f"missing_skill::{career_index}::"
                        f"{skill_index}::{skill_key}"
                    )
                    relation = "REQUIRES"

                    add_graph_node(
                        skill_id, skill, kind,
                        "Skill to learn for this career"
                    )

                add_graph_edge(
                    career_id, skill_id, relation
                )

                # Missing skill -> Learning resources
                if kind == "missing_skill":
                    skill_resources = RESOURCES.get(skill_key, [])
                    fallback = CAREERS[career]["courses"].get(skill)

                    if skill_resources:
                        for resource_index, resource in enumerate(
                            skill_resources[:2]
                        ):
                            resource_name = (
                                resource.get("name")
                                or resource.get("platform")
                                or skill
                            )

                            resource_id = (
                                f"resource::{career_index}::{skill_index}::"
                                f"{resource_index}::{resource_name}"
                            )

                            resource_title = resource_name

                            if resource.get("platform"):
                                resource_title += (
                                    f'\nPlatform: {resource["platform"]}'
                                )

                            if resource.get("url"):
                                resource_title += (
                                    f'\n{resource["url"]}'
                                )

                            add_graph_node(
                                resource_id,
                                resource_name,
                                "resource",
                                resource_title
                            )

                            add_graph_edge(
                                skill_id, resource_id, "LEARN_THROUGH"
                            )

                    elif fallback and (fallback[0] or fallback[1]):
                        resource_name = (
                            fallback[0] or f"Learn {skill}"
                        )

                        resource_id = (
                            f"resource::{career_index}::{skill_index}"
                            f"::fallback::{resource_name}"
                        )

                        add_graph_node(
                            resource_id,
                            resource_name,
                            "resource",
                            fallback[1] or "Course from career_dataset.csv"
                        )

                        add_graph_edge(
                            skill_id, resource_id, "LEARN_THROUGH"
                        )

        # Graph display settings
        net.set_options("""
        {
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "multiselect": true,
            "tooltipDelay": 100
          },
          "nodes": {
            "shadow": {
              "enabled": true,
              "size": 8,
              "x": 2,
              "y": 2
            }
          },
          "edges": {
            "width": 1.5,
            "selectionWidth": 2.5,
            "hoverWidth": 2,
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.7
              }
            }
          },
          "physics": {
            "enabled": true,
            "stabilization": {
              "enabled": true,
              "iterations": 180,
              "fit": true
            },
            "barnesHut": {
              "gravitationalConstant": -28000,
              "centralGravity": 0.25,
              "springLength": 180,
              "springConstant": 0.025,
              "damping": 0.09,
              "avoidOverlap": 0.25
            }
          }
        }
        """)

        components.html(
            net.generate_html(),
            height=690,
            scrolling=True
        )

        st.markdown(
            "**Node legend:** 🟠 Student · 🟣 Interest · 🔵 Career · "
            "🟢 Known skill · 🔴 Skill to learn · 🩷 Learning resource"
        )

        st.caption(
            "Relationship labels: INTERESTED_IN, HAS_SKILL, RECOMMENDED, "
            "REQUIRES, and LEARN_THROUGH. This is a Neo4j-style "
            "visualization built with PyVis; graph data is not stored "
            "in a Neo4j database."
        )


# -------------------- FOOTER --------------------

st.divider()

st.caption(
    "Prototype: recommendations use selected interests and known skills. "
    "Match scores are estimates based on the supplied career dataset, "
    "not guarantees of job suitability. Interests that do not have matching "
    "career records cannot currently be recommended."
)

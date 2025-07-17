import streamlit as st
import random
from collections import defaultdict

# ========== Student Class ========== #
class Student:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
        self.pref_names = []
        self.pref_map = {}
        self.next_index = 0
        self.partner = None

    def set_preferences(self, preferences):
        self.pref_names = preferences
        self.pref_map = {sid: i for i, sid in enumerate(preferences)}

    def get_next_preference(self):
        if self.next_index < len(self.pref_names):
            sid = self.pref_names[self.next_index]
            self.next_index += 1
            return sid
        return None

    def prefers(self, new_sid, current_sid):
        return self.pref_map.get(new_sid, float('inf')) < self.pref_map.get(current_sid, float('inf'))

# ========== Matching Algorithm ========== #
def stable_matching(students_dict):
    unmatched = list(students_dict.keys())

    while unmatched:
        sid = unmatched.pop(0)
        student = students_dict[sid]
        next_sid = student.get_next_preference()
        if not next_sid:
            continue
        preferred = students_dict[next_sid]

        if preferred.partner is None:
            preferred.partner = sid
            student.partner = preferred.sid
        else:
            current = preferred.partner
            if preferred.prefers(sid, current):
                students_dict[current].partner = None
                unmatched.append(current)
                preferred.partner = sid
                student.partner = preferred.sid
            else:
                unmatched.append(sid)

    pairs = set()
    matched = set()
    for sid, student in students_dict.items():
        if student.partner and sid not in matched and student.partner not in matched:
            a, b = sorted([sid, student.partner])
            pairs.add((a, b))
            matched.update([a, b])

    # Random match remaining students
    unmatched = list(set(students_dict.keys()) - matched)
    random.shuffle(unmatched)
    while len(unmatched) >= 2:
        a = unmatched.pop()
        b = unmatched.pop()
        pairs.add(tuple(sorted([a, b])))

    return pairs

# ========== Streamlit App ========== #
st.set_page_config(page_title="Roommate Matcher", page_icon="🏠", layout="centered")

st.title("🏠 Perfect Roommate Matcher")
st.write("Match roommates based on preferences. Designed for small groups of known students.")

# Session storage
if "students" not in st.session_state:
    st.session_state.students = []
if "preferences" not in st.session_state:
    st.session_state.preferences = {}

# Add students
st.subheader("Step 1: Add Students")
name = st.text_input("Enter student name", key="name_input")
if st.button("Add Student"):
    if name and name not in [s["name"] for s in st.session_state.students]:
        sid = f"s{len(st.session_state.students)+1}"
        st.session_state.students.append({"sid": sid, "name": name})
        st.success(f"Added {name}")
    else:
        st.warning("Name is empty or already added.")

if st.session_state.students:
    st.write("Current Students:")
    for s in st.session_state.students:
        st.write(f"- {s['name']} ({s['sid']})")

# Preferences
if len(st.session_state.students) >= 2 and len(st.session_state.students) % 2 == 0:
    st.subheader("Step 2: Set Preferences")
    for student in st.session_state.students:
        sid = student["sid"]
        name = student["name"]
        others = [s["name"] for s in st.session_state.students if s["name"] != name]
        selected = st.multiselect(f"{name}'s preferences (in order)", others, key=f"prefs_{sid}")
        st.session_state.preferences[sid] = selected

    # Match
    if st.button("Generate Matches"):
        # Build Student objects
        sid_to_student = {}
        name_to_sid = {s["name"]: s["sid"] for s in st.session_state.students}
        for s in st.session_state.students:
            obj = Student(s["sid"], s["name"])
            prefs = [name_to_sid[name] for name in st.session_state.preferences.get(s["sid"], [])]
            obj.set_preferences(prefs)
            sid_to_student[s["sid"]] = obj

        pairs = stable_matching(sid_to_student)
        sid_to_name = {s["sid"]: s["name"] for s in st.session_state.students}

        st.subheader("🛏️ Final Room Assignments")
        for a, b in sorted(pairs):
            st.write(f"- {sid_to_name[a]} ↔ {sid_to_name[b]}")
else:
    st.info("Add at least 2 students (even number) to proceed.")

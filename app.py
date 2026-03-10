import streamlit as st
import json
import re
from datetime import datetime
from groq import Groq

def _call_groq(client, system, user, max_tokens=2000):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.1, max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

def _extract_json(raw):
    raw = re.sub(r"```[a-z]*", "", raw).replace("```", "").strip()
    try: return json.loads(raw)
    except: pass
    for s_char, e_char in [('{','}'),('[',']')]:
        s = raw.find(s_char); e = raw.rfind(e_char)
        if s != -1 and e != -1 and e > s:
            try: return json.loads(raw[s:e+1])
            except: pass
    raise ValueError(f"Could not extract JSON:\n{raw[:300]}")

class MessageBus:
    def __init__(self): self._log = []
    def send(self, sender, receiver, content):
        self._log.append({"from":sender,"to":receiver,"content":content,"time":datetime.now().strftime("%H:%M:%S")})
    def all_messages(self): return self._log

class PlannerAgent:
    NAME = "Planner"
    def __init__(self, client, bus): self.client = client; self.bus = bus

    def split_subjects(self, text):
        self.bus.send(self.NAME, "System", "Detecting number of courses in input…")
        year = datetime.now().year
        raw = _call_groq(self.client,
            "You split academic text into separate course syllabi. Return ONLY valid JSON, no prose.",
            f"""Split the following text into individual course syllabi.
If there is only one course, return a list with one item.
Return ONLY this JSON — no extra text:
[{{"course_name":"<name>","syllabus_text":"<full text for this course only>"}}]

Text:
\"\"\"{text}\"\"\"
""", max_tokens=4000)
        result = _extract_json(raw)
        self.bus.send(self.NAME, "System", f"Detected {len(result)} course(s) in input.")
        return result

    def parse_one_syllabus(self, text, course_hint=""):
        self.bus.send(self.NAME, "Retriever", f"Parsing deadlines for: {course_hint or 'course'}…")
        year = datetime.now().year
        raw = _call_groq(self.client,
            "You are a precise academic planner. Return ONLY valid JSON, no prose, no markdown.",
            f"""Extract all academic deadlines from this syllabus.
Smart start_date (when student should BEGIN):
- quiz/reading/homework: 5 days before
- lab/assignment/problem set: 7 days before
- midterm/exam: 14 days before
- project/essay/paper/presentation/final: 21 days before
If no year, use {year} (or {year+1} if month passed).
Return ONLY this JSON:
{{"course":"<name>","deadlines":[{{"task":"<name>","task_type":"<exam|quiz|assignment|project|essay|lab|presentation|homework|other>","due_date":"YYYY-MM-DD","start_date":"YYYY-MM-DD","weight":"<% or unknown>"}}]}}

Syllabus:
\"\"\"{text}\"\"\"
""")
        result = _extract_json(raw)
        self.bus.send(self.NAME, "Retriever", f"'{result['course']}' — {len(result['deadlines'])} deadlines found.")
        return result

    def request_resources(self, task, task_type):
        self.bus.send(self.NAME, "Retriever", f"Need resources for: '{task}' (type: {task_type})")

class RetrieverAgent:
    NAME = "Retriever"
    def __init__(self, client, bus): self.client = client; self.bus = bus

    def find_resources(self, task, task_type, course):
        raw = _call_groq(self.client,
            "You are an academic resource specialist. Return ONLY valid JSON, no prose, no markdown.",
            f"""Student preparing for: "{task}" | Type: {task_type} | Course: {course}
Suggest exactly 3 specific, practical resources.
Return ONLY: [{{"title":"<name>","type":"<video|document|practice|tool|website>","description":"<one sentence>"}}]
""", max_tokens=600)
        resources = _extract_json(raw)
        self.bus.send(self.NAME, "Executor", f"Found {len(resources)} resources for '{task}'.")
        return resources

class ExecutorAgent:
    NAME = "Executor"
    def __init__(self, bus): self.bus = bus

    def create_calendar_events(self, deadlines, resources_map, course):
        self.bus.send(self.NAME, "System", f"Creating calendar events for '{course}'…")
        events = []
        for item in deadlines:
            due = datetime.strptime(item["due_date"], "%Y-%m-%d")
            start = datetime.strptime(item["start_date"], "%Y-%m-%d")
            days = max((due - start).days, 1)
            events.append({
                "title": item["task"], "task_type": item.get("task_type","other"),
                "course": course, "start": item["start_date"], "due": item["due_date"],
                "days_to_work": days, "weight": item.get("weight","unknown"),
                "resources": resources_map.get(item["task"], []),
                "reminder": f"Begin '{item['task']}' — {days} days to deadline",
            })
        self.bus.send(self.NAME, "System", f"✅ {len(events)} events created for '{course}'.")
        return events

st.set_page_config(page_title="TaskWeave", page_icon="🕸️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700;800&display=swap');
html,body,[data-testid="stAppViewContainer"]{font-family:'Sora',sans-serif !important;}
h1,h2,h3{font-family:'Sora',sans-serif !important;}
.tw-title{font-size:3rem;font-weight:800;letter-spacing:-1.5px;background:linear-gradient(120deg,#a78bfa,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-align:center;margin:0;}
.tw-sub{text-align:center;color:#6b7280;font-weight:300;font-size:1rem;margin-bottom:1.8rem;}
.msg-chip{font-family:'Space Mono',monospace;font-size:0.7rem;padding:5px 10px;border-radius:6px;margin:3px 0;display:block;word-break:break-word;}
.msg-planner{background:#dbeafe;color:#1d4ed8;border-left:3px solid #3b82f6;}
.msg-retriever{background:#ede9fe;color:#6d28d9;border-left:3px solid #7c3aed;}
.msg-executor{background:#d1fae5;color:#065f46;border-left:3px solid #059669;}
.msg-system{background:#f3f4f6;color:#6b7280;border-left:3px solid #d1d5db;}
.badge{font-family:'Space Mono',monospace;font-size:0.62rem;font-weight:700;padding:2px 8px;border-radius:99px;text-transform:uppercase;letter-spacing:0.06em;display:inline-block;margin-bottom:6px;}
.badge-exam{background:#fee2e2;color:#b91c1c;border:1px solid #ef4444;}
.badge-quiz{background:#fef3c7;color:#92400e;border:1px solid #f59e0b;}
.badge-assignment{background:#d1fae5;color:#065f46;border:1px solid #10b981;}
.badge-project{background:#e0e7ff;color:#3730a3;border:1px solid #6366f1;}
.badge-essay{background:#fae8ff;color:#86198f;border:1px solid #d946ef;}
.badge-lab{background:#dcfce7;color:#166534;border:1px solid #22c55e;}
.badge-homework{background:#fff7ed;color:#9a3412;border:1px solid #f97316;}
.badge-presentation{background:#ecfeff;color:#0e7490;border:1px solid #06b6d4;}
.badge-other{background:#f3f4f6;color:#374151;border:1px solid #9ca3af;}
.tw-card{background:rgba(0,0,0,0.03);border:1px solid rgba(0,0,0,0.1);border-radius:12px;padding:1.1rem 1.3rem;margin:0.6rem 0;transition:border-color 0.2s,box-shadow 0.2s;}
.tw-card:hover{border-color:#a78bfa;box-shadow:0 2px 12px rgba(167,139,250,0.15);}
.tw-card h4{margin:0 0 0.4rem;font-size:1rem;}
.meta{font-size:0.82rem;color:#6b7280;margin:2px 0;}
.course-header{background:linear-gradient(90deg,rgba(167,139,250,0.12),transparent);border-left:4px solid #a78bfa;border-radius:0 8px 8px 0;padding:0.6rem 1rem;margin:1.4rem 0 0.4rem;font-weight:700;font-size:1.05rem;}
</style>
""", unsafe_allow_html=True)

for k,v in [("bus",None),("all_courses",[]),("api_key","")]:
    if k not in st.session_state: st.session_state[k] = v

DEMO_SYLLABI = {
    "💻 Computer Science": """Data Structures & Algorithms — Spring 2025
Instructor: Dr. Priya Mehta
- Homework 1 (Arrays & Linked Lists): Due February 10, 2025 [5%]
- Quiz 1 (Recursion basics): February 17, 2025 [5%]
- Lab Report (Sorting benchmarks): Due March 1, 2025 [10%]
- Assignment 2 (Graph traversal): Due March 14, 2025 [10%]
- Midterm Exam (weeks 1–7): March 24, 2025 [20%]
- Essay: Algorithmic complexity in real systems: Due April 7, 2025 [10%]
- Group Project (Build a search engine): Due April 28, 2025 [20%]
- Quiz 2 (Dynamic programming): April 14, 2025 [5%]
- Final Presentation (Project demo): May 5, 2025 [5%]
- Final Exam (comprehensive): May 15, 2025 [10%]""",
    "🧬 Biology": """Cell Biology & Genetics — Spring 2025
Instructor: Dr. Ananya Sharma
- Lab Report 1 (Microscopy techniques): Due February 20, 2025 [10%]
- Quiz on Cell Structure and Organelles: March 3, 2025 [5%]
- Assignment: Literature Review on CRISPR: Due March 17, 2025 [10%]
- Midterm Exam (covers weeks 1–7): March 31, 2025 [25%]
- Lab Report 2 (PCR and Gel Electrophoresis): Due April 14, 2025 [10%]
- Research Paper on Gene Expression: Due May 1, 2025 [20%]
- Final Exam (comprehensive): May 19, 2025 [20%]""",
    "📜 History": """Modern World History — Fall 2025
Instructor: Prof. James Okafor
- Reading Response 1 (Colonialism, Ch 1–4): Due September 15, 2025 [5%]
- Essay: Causes of World War I: Due October 3, 2025 [15%]
- Quiz on the Interwar Period: October 13, 2025 [5%]
- Midterm Examination: October 27, 2025 [20%]
- Research Project (Cold War topic): Due November 10, 2025 [10%]
- Reading Response 2 (Decolonisation): Due November 24, 2025 [5%]
- Final Research Paper: Due December 8, 2025 [25%]
- Final Presentation (10 min): December 15, 2025 [15%]""",
    "📊 Economics": """Microeconomics — Spring 2025
Instructor: Dr. Leila Nasser
- Problem Set 1 (Supply & Demand): Due February 14, 2025 [8%]
- Quiz 1 (Consumer Theory): February 24, 2025 [7%]
- Problem Set 2 (Market Structures): Due March 10, 2025 [8%]
- Midterm Exam: March 21, 2025 [25%]
- Essay: Market failure and government intervention: Due April 11, 2025 [12%]
- Quiz 2 (Game Theory): April 21, 2025 [7%]
- Policy Analysis Project: Due May 2, 2025 [18%]
- Final Exam (comprehensive): May 16, 2025 [15%]""",
    "⚗️ Chemistry": """Organic Chemistry II — Spring 2025
Instructor: Dr. Rahul Verma
- Lab Report 1 (Nucleophilic Substitution): Due February 17, 2025 [8%]
- Homework 1 (Reaction mechanisms): Due February 28, 2025 [5%]
- Quiz 1 (Aromatic compounds): March 10, 2025 [7%]
- Lab Report 2 (Aldol Condensation): Due March 24, 2025 [8%]
- Midterm Exam (chapters 1–6): April 4, 2025 [22%]
- Homework 2 (Stereochemistry problems): Due April 18, 2025 [5%]
- Research Presentation (synthesis pathway): April 28, 2025 [15%]
- Final Exam (comprehensive): May 14, 2025 [30%]""",
    "🔀 Multiple Subjects (CS + Biology + Economics)": """Data Structures & Algorithms — Spring 2025
Instructor: Dr. Priya Mehta
- Homework 1 (Arrays & Linked Lists): Due February 10, 2025 [5%]
- Quiz 1 (Recursion basics): February 17, 2025 [5%]
- Midterm Exam: March 24, 2025 [20%]
- Group Project (Build a search engine): Due April 28, 2025 [20%]
- Final Exam (comprehensive): May 15, 2025 [10%]

---

Cell Biology & Genetics — Spring 2025
Instructor: Dr. Ananya Sharma
- Lab Report 1 (Microscopy techniques): Due February 20, 2025 [10%]
- Quiz on Cell Structure: March 3, 2025 [5%]
- Midterm Exam (covers weeks 1–7): March 31, 2025 [25%]
- Research Paper on Gene Expression: Due May 1, 2025 [20%]
- Final Exam (comprehensive): May 19, 2025 [20%]

---

Microeconomics — Spring 2025
Instructor: Dr. Leila Nasser
- Problem Set 1 (Supply & Demand): Due February 14, 2025 [8%]
- Quiz 1 (Consumer Theory): February 24, 2025 [7%]
- Midterm Exam: March 21, 2025 [25%]
- Policy Analysis Project: Due May 2, 2025 [18%]
- Final Exam (comprehensive): May 16, 2025 [15%]""",
}

BADGE_MAP = {"exam":"badge-exam","quiz":"badge-quiz","assignment":"badge-assignment","project":"badge-project","essay":"badge-essay","lab":"badge-lab","homework":"badge-homework","presentation":"badge-presentation"}
def badge_html(t): return f'<span class="badge {BADGE_MAP.get(t.lower(),"badge-other")}">{t}</span>'

with st.sidebar:
    st.markdown("## 🕸️ TaskWeave")
    st.markdown("<span style='color:#6b7280;font-size:0.82rem'>Multi-Agent Academic Planner</span>", unsafe_allow_html=True)
    st.divider()
    api_key = st.text_input("Groq API Key", type="password", value=st.session_state.api_key, placeholder="gsk_… (free at console.groq.com)")
    if api_key: st.session_state.api_key = api_key
    st.divider()
    st.markdown("**Agents**")
    st.markdown("🤖 **Planner** — detects courses, builds timelines")
    st.markdown("🔍 **Retriever** — finds resources per task")
    st.markdown("✅ **Executor** — creates calendar events")
    st.divider()
    st.markdown("**Inter-Agent Message Log**")
    if st.session_state.bus:
        for m in st.session_state.bus.all_messages()[-20:]:
            s = m["from"].lower()
            css = f"msg-{s}" if s in ("planner","retriever","executor") else "msg-system"
            st.markdown(f'<span class="msg-chip {css}"><b>{m["from"]} → {m["to"]}</b><br>{m["content"]}</span>', unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#9ca3af;font-size:0.8rem'>Agents idle</span>", unsafe_allow_html=True)

st.markdown('<h1 class="tw-title">🕸️ TaskWeave</h1>', unsafe_allow_html=True)
st.markdown('<p class="tw-sub">Three AI agents that turn your semester chaos into a manageable plan</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📄  Syllabus", "📅  Timeline", "🗓️  Calendar Events"])

with tab1:
    st.markdown("### Paste Your Course Syllabus")
    st.markdown("<span style='color:#6b7280;font-size:0.85rem'>Paste one subject or multiple subjects together — the agents will figure it out.</span>", unsafe_allow_html=True)
    col_sel, _ = st.columns([2,3])
    with col_sel:
        subject_choice = st.selectbox("📚 Load a demo syllabus", ["✏️ Type my own"] + list(DEMO_SYLLABI.keys()), index=6)
    default_text = "" if subject_choice == "✏️ Type my own" else DEMO_SYLLABI[subject_choice]
    syllabus = st.text_area("", value=default_text, height=260, placeholder="Paste one or more syllabi here…", key=f"syl_{subject_choice}")

    if st.button("🚀  Process Syllabus", type="primary"):
        if not st.session_state.api_key:
            st.error("Enter your free Groq API key in the sidebar. Get one at console.groq.com")
        elif not syllabus.strip():
            st.warning("Paste some syllabus text first.")
        else:
            bus = MessageBus()
            gclient = Groq(api_key=st.session_state.api_key)
            planner = PlannerAgent(gclient, bus)
            retriever = RetrieverAgent(gclient, bus)
            executor = ExecutorAgent(bus)
            st.session_state.bus = bus
            st.session_state.all_courses = []
            status = st.empty()
            overall = st.progress(0, text="Starting…")
            try:
                status.markdown('<div style="background:#dbeafe;border-left:4px solid #3b82f6;padding:0.8rem 1rem;border-radius:8px;color:#1d4ed8;margin:4px 0">🤖 <b>Planner Agent</b> — detecting courses in input…</div>', unsafe_allow_html=True)
                course_blocks = planner.split_subjects(syllabus)
                total_courses = len(course_blocks)
                overall.progress(0.05, text=f"Found {total_courses} course(s). Processing…")
                all_courses = []
                for ci, block in enumerate(course_blocks):
                    hint = block.get("course_name", f"Course {ci+1}")
                    text = block.get("syllabus_text", syllabus)
                    status.markdown(f'<div style="background:#dbeafe;border-left:4px solid #3b82f6;padding:0.8rem 1rem;border-radius:8px;color:#1d4ed8;margin:4px 0">🤖 <b>Planner Agent</b> — extracting deadlines for <em>{hint}</em>…</div>', unsafe_allow_html=True)
                    timeline = planner.parse_one_syllabus(text, hint)
                    n = len(timeline["deadlines"])
                    resources_map = {}
                    for i, item in enumerate(timeline["deadlines"]):
                        status.markdown(f'<div style="background:#ede9fe;border-left:4px solid #7c3aed;padding:0.8rem 1rem;border-radius:8px;color:#6d28d9;margin:4px 0">🔍 <b>Retriever Agent</b> — resources for <em>{item["task"]}</em>…</div>', unsafe_allow_html=True)
                        planner.request_resources(item["task"], item.get("task_type","other"))
                        try: resources = retriever.find_resources(item["task"], item.get("task_type","other"), timeline["course"])
                        except: resources = []
                        resources_map[item["task"]] = resources
                        overall.progress(min((ci/total_courses)+((i+1)/n/total_courses), 0.95), text=f"Processing {hint}…")
                    status.markdown(f'<div style="background:#d1fae5;border-left:4px solid #059669;padding:0.8rem 1rem;border-radius:8px;color:#065f46;margin:4px 0">✅ <b>Executor Agent</b> — creating events for <em>{hint}</em>…</div>', unsafe_allow_html=True)
                    events = executor.create_calendar_events(timeline["deadlines"], resources_map, timeline["course"])
                    all_courses.append({"course": timeline["course"], "timeline": timeline, "events": events})
                st.session_state.all_courses = all_courses
                overall.progress(1.0, text="Done!")
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
            status.empty()
            total_events = sum(len(c["events"]) for c in all_courses)
            total_dl = sum(len(c["timeline"]["deadlines"]) for c in all_courses)
            st.success(f"✨ Done! {total_courses} course(s) · {total_dl} deadlines · {total_events} calendar events created.")
            st.balloons()
            st.info("Check the **Timeline** and **Calendar Events** tabs ↑")

with tab2:
    if not st.session_state.all_courses:
        st.info("👆 Process a syllabus in the first tab to see your timeline.")
    else:
        all_courses = st.session_state.all_courses
        total_dl = sum(len(c["timeline"]["deadlines"]) for c in all_courses)
        st.markdown(f"**{len(all_courses)} course(s) · {total_dl} total deadlines**")
        for course_data in all_courses:
            tl = course_data["timeline"]; events = course_data["events"]
            st.markdown(f'<div class="course-header">📚 {tl["course"]}</div>', unsafe_allow_html=True)
            for item in tl["deadlines"]:
                due_dt = datetime.strptime(item["due_date"], "%Y-%m-%d")
                start_dt = datetime.strptime(item["start_date"], "%Y-%m-%d")
                days_work = max((due_dt - start_dt).days, 1)
                days_left = (due_dt - datetime.today()).days
                if days_left < 0: dl_str = f"<span style='color:#ef4444'>⚠️ {abs(days_left)}d overdue</span>"
                elif days_left <= 7: dl_str = f"<span style='color:#f59e0b'>{days_left}d left</span>"
                else: dl_str = f"<span style='color:#6b7280'>{days_left}d left</span>"
                resources = next((ev["resources"] for ev in events if ev["title"] == item["task"]), [])
                res_html = "".join(f'<span style="display:inline-block;background:#f0f0ff;border:1px solid #c4b5fd;border-radius:6px;padding:3px 9px;font-size:0.77rem;margin:3px;color:#6d28d9">📎 {r["title"]}</span>' for r in resources) or "<span style='color:#9ca3af;font-size:0.8rem'>—</span>"
                weight = item.get("weight","unknown")
                weight_str = f" · {weight}" if weight != "unknown" else ""
                st.markdown(f'<div class="tw-card">{badge_html(item.get("task_type","other"))}<h4>{item["task"]}</h4><div class="meta">🟢 Start: <b>{item["start_date"]}</b> &nbsp;·&nbsp; 🔴 Due: <b>{item["due_date"]}</b>{weight_str} &nbsp;·&nbsp; {dl_str}</div><div class="meta">⏱ Work window: <b>{days_work} days</b></div><div style="margin-top:8px">{res_html}</div></div>', unsafe_allow_html=True)

with tab3:
    if not st.session_state.all_courses:
        st.info("👆 Process a syllabus in the first tab to see calendar events.")
    else:
        all_courses = st.session_state.all_courses
        all_events = [ev for c in all_courses for ev in c["events"]]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Events", len(all_events))
        c2.metric("Courses", len(all_courses))
        c3.metric("Exams / Midterms", sum(1 for e in all_events if "exam" in e["task_type"]))
        c4.metric("Projects / Essays", sum(1 for e in all_events if e["task_type"] in ("project","essay")))
        st.markdown("---")
        for course_data in all_courses:
            events = course_data["events"]
            st.markdown(f'<div class="course-header">🗓️ {course_data["course"]}</div>', unsafe_allow_html=True)
            for ev in events:
                res_items = "".join(f'<div style="margin:4px 0;font-size:0.82rem;color:#374151">📌 <b>{r["title"]}</b><span style="color:#9ca3af"> ({r.get("type","")}) — {r.get("description","")}</span></div>' for r in ev["resources"]) if ev["resources"] else "<div style='color:#9ca3af;font-size:0.8rem'>No resources attached</div>"
                st.markdown(f'<div class="tw-card">{badge_html(ev["task_type"])}<h4>📅 {ev["title"]}</h4><div class="meta">🟢 Start working: <b>{ev["start"]}</b></div><div class="meta">🔴 Due date: <b>{ev["due"]}</b> &nbsp;·&nbsp; Weight: {ev["weight"]}</div><div class="meta">⏱ {ev["days_to_work"]} days of work scheduled</div><div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(0,0,0,0.07)"><div style="font-size:0.72rem;color:#9ca3af;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.05em">Attached Resources</div>{res_items}</div><div style="margin-top:8px;background:#ede9fe;border-radius:6px;padding:6px 10px;font-size:0.8rem;color:#6d28d9">🔔 {ev["reminder"]}</div></div>', unsafe_allow_html=True)

st.divider()
st.markdown("<div style='text-align:center;color:#9ca3af;font-size:0.8rem;padding:0.5rem'>TaskWeave · Multi-Agent Academic Planner · Built by Krrish Jindal (IIT Roorkee)</div>", unsafe_allow_html=True)

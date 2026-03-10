import streamlit as st
import json
import time
import re
from datetime import datetime, timedelta
from groq import Groq

# ──────────────────────────────────────────────────────────
# AGENT CLASSES  —  message passing via shared MessageBus
# ──────────────────────────────────────────────────────────

def _call_groq(client: Groq, system: str, user: str) -> str:
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.2,
        max_tokens=1500,
    )
    return response.choices[0].message.content.strip()


class MessageBus:
    """Simple in-process bus so agents can send messages to each other."""
    def __init__(self):
        self._log = []

    def send(self, sender: str, receiver: str, content: str):
        self._log.append({
            "from": sender, "to": receiver,
            "content": content,
            "time": datetime.now().strftime("%H:%M:%S"),
        })

    def all_messages(self):
        return self._log


class PlannerAgent:
    NAME = "Planner"

    def __init__(self, client: Groq, bus: MessageBus):
        self.client = client
        self.bus = bus

    def parse_syllabus(self, text: str) -> dict:
        self.bus.send(self.NAME, "System", "Analysing syllabus text…")
        system = (
            "You are a precise academic planner. "
            "Extract every deadline from the syllabus. "
            "Return ONLY valid JSON — no markdown fences, no prose."
        )
        year = datetime.now().year
        user = f"""Extract all academic deadlines from this syllabus.

For each deadline, decide a smart 'start_date' (when the student should BEGIN working):
- quiz / reading / homework: 5 days before due
- lab / assignment / problem set: 7 days before due
- midterm / exam: 14 days before due
- project / essay / research paper / final: 21 days before due

If no year is given, use {year} (or {year + 1} if the month has already passed).

Return ONLY this JSON — no extra text:
{{
  "course": "<course name>",
  "deadlines": [
    {{
      "task": "<task name>",
      "task_type": "<exam|quiz|assignment|project|essay|lab|presentation|homework|other>",
      "due_date": "YYYY-MM-DD",
      "start_date": "YYYY-MM-DD",
      "weight": "<e.g. 20% or unknown>"
    }}
  ]
}}

Syllabus:
\"\"\"
{text}
\"\"\"
"""
        raw = _call_groq(self.client, system, user)
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"```$", "", raw, flags=re.MULTILINE)
        result = json.loads(raw.strip())
        n = len(result["deadlines"])
        self.bus.send(self.NAME, "Retriever",
                      f"Parsed '{result['course']}' — {n} deadlines. Requesting resources for each.")
        return result

    def request_resources(self, task: str, task_type: str):
        self.bus.send(self.NAME, "Retriever",
                      f"Need resources for: '{task}' (type: {task_type})")


class RetrieverAgent:
    NAME = "Retriever"

    def __init__(self, client: Groq, bus: MessageBus):
        self.client = client
        self.bus = bus

    def find_resources(self, task: str, task_type: str, course: str) -> list:
        system = (
            "You are an academic resource specialist. "
            "Suggest specific, practical study resources. "
            "Return ONLY valid JSON — no markdown fences, no prose."
        )
        user = f"""A student is preparing for: "{task}"
Task type: {task_type}
Course: {course}

Suggest exactly 3 targeted, specific resources.

Return ONLY this JSON array:
[
  {{
    "title": "<resource name>",
    "type": "<video|document|practice|tool|website>",
    "description": "<one sentence on how it helps>"
  }}
]
"""
        raw = _call_groq(self.client, system, user)
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"```$", "", raw, flags=re.MULTILINE)
        resources = json.loads(raw.strip())
        self.bus.send(self.NAME, "Executor",
                      f"Found {len(resources)} resources for '{task}' — sending to Executor.")
        return resources


class ExecutorAgent:
    NAME = "Executor"

    def __init__(self, bus: MessageBus):
        self.bus = bus

    def create_calendar_events(self, deadlines: list, resources_map: dict, course: str) -> list:
        self.bus.send(self.NAME, "System", "Building calendar events with resources attached…")
        events = []
        for item in deadlines:
            due   = datetime.strptime(item["due_date"],   "%Y-%m-%d")
            start = datetime.strptime(item["start_date"], "%Y-%m-%d")
            days  = max((due - start).days, 1)
            events.append({
                "title":        item["task"],
                "task_type":    item.get("task_type", "other"),
                "course":       course,
                "start":        item["start_date"],
                "due":          item["due_date"],
                "days_to_work": days,
                "weight":       item.get("weight", "unknown"),
                "resources":    resources_map.get(item["task"], []),
                "reminder":     f"Begin '{item['task']}' — {days} days to deadline",
            })
        self.bus.send(self.NAME, "System",
                      f"Done — {len(events)} events created with reminders and materials attached.")
        return events


# ──────────────────────────────────────────────────────────
# PAGE CONFIG & STYLES
# ──────────────────────────────────────────────────────────

st.set_page_config(page_title="TaskWeave", page_icon="🕸️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #08080f !important;
    color: #ddd8f0 !important;
    font-family: 'Sora', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1e1e30 !important;
}
h1,h2,h3 { font-family: 'Sora', sans-serif !important; }

.tw-title {
    font-size: 3rem; font-weight: 800; letter-spacing: -1.5px;
    background: linear-gradient(120deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; text-align: center; margin: 0;
}
.tw-sub {
    text-align: center; color: #6b6b88;
    font-weight: 300; font-size: 1rem; margin-bottom: 1.8rem;
}

.msg-chip {
    font-family: 'Space Mono', monospace; font-size: 0.7rem;
    padding: 5px 10px; border-radius: 6px; margin: 3px 0;
    display: block; word-break: break-word;
}
.msg-planner   { background:#0d1a2e; color:#93c5fd; border-left:3px solid #3b82f6; }
.msg-retriever { background:#160d2e; color:#c4b5fd; border-left:3px solid #7c3aed; }
.msg-executor  { background:#0d2318; color:#6ee7b7; border-left:3px solid #059669; }
.msg-system    { background:#1a1a1a; color:#777;    border-left:3px solid #444; }

.badge {
    font-family: 'Space Mono', monospace; font-size: 0.62rem; font-weight: 700;
    padding: 2px 8px; border-radius: 99px; text-transform: uppercase;
    letter-spacing: 0.06em; display: inline-block; margin-bottom: 6px;
}
.badge-exam       { background:#1e0a0a; color:#f87171; border:1px solid #ef4444; }
.badge-quiz       { background:#1a1000; color:#fbbf24; border:1px solid #f59e0b; }
.badge-assignment { background:#001a1a; color:#34d399; border:1px solid #10b981; }
.badge-project    { background:#0a0a1e; color:#818cf8; border:1px solid #6366f1; }
.badge-essay      { background:#1a0a18; color:#e879f9; border:1px solid #d946ef; }
.badge-lab        { background:#0a1a10; color:#4ade80; border:1px solid #22c55e; }
.badge-other      { background:#1a1a1a; color:#9ca3af; border:1px solid #6b7280; }

.tw-card {
    background: #111120; border: 1px solid #1e1e30; border-radius: 12px;
    padding: 1.1rem 1.3rem; margin: 0.7rem 0;
    transition: border-color 0.2s;
}
.tw-card:hover { border-color: #a78bfa; }
.tw-card h4 { margin: 0 0 0.4rem; font-size: 1rem; color: #e2e0f0; }
.meta { font-size: 0.82rem; color: #7070a0; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────

for key, val in [("bus", None), ("timeline", None), ("events", []), ("api_key", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🕸️ TaskWeave")
    st.markdown("<span style='color:#6b6b88;font-size:0.82rem'>Multi-Agent Academic Planner</span>",
                unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("Groq API Key", type="password",
                             value=st.session_state.api_key,
                             placeholder="gsk_… (free at console.groq.com)")
    if api_key:
        st.session_state.api_key = api_key

    st.divider()
    st.markdown("**Agents**")
    st.markdown("🤖 **Planner** — reads syllabus, builds timeline")
    st.markdown("🔍 **Retriever** — finds study resources per task")
    st.markdown("✅ **Executor** — creates calendar events")
    st.divider()

    st.markdown("**Inter-Agent Message Log**")
    if st.session_state.bus:
        msgs = st.session_state.bus.all_messages()
        for m in msgs[-15:]:
            s = m["from"].lower()
            css = f"msg-{s}" if s in ("planner", "retriever", "executor") else "msg-system"
            st.markdown(
                f'<span class="msg-chip {css}">'
                f'<b>{m["from"]} → {m["to"]}</b><br>{m["content"]}'
                f'</span>', unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#333;font-size:0.8rem'>Agents idle — process a syllabus to see messages</span>",
                    unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# MAIN TABS
# ──────────────────────────────────────────────────────────

st.markdown('<h1 class="tw-title">🕸️ TaskWeave</h1>', unsafe_allow_html=True)
st.markdown('<p class="tw-sub">Three AI agents that turn your semester chaos into a manageable plan</p>',
            unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📄  Syllabus", "📅  Timeline", "🗓️  Calendar Events"])

SAMPLE = """Cell Biology — Spring 2025
Instructor: Dr. Ananya Sharma

Grading & Deadlines:
- Lab Report 1 (Microscopy techniques): Due March 15, 2025  [10%]
- Quiz on Cell Structure and Organelles: March 22, 2025  [5%]
- Assignment: Literature Review on Cell Division: Due April 2, 2025  [10%]
- Midterm Exam (covers weeks 1–7): April 10, 2025  [25%]
- Research Paper on Photosynthesis pathways: Due May 3, 2025  [20%]
- Lab Report 2 (Protein analysis): Due May 12, 2025  [10%]
- Final Exam (comprehensive): May 22, 2025  [20%]
"""

# ── TAB 1 ──────────────────────────────────────────────────

with tab1:
    st.markdown("### Paste Your Course Syllabus")
    st.markdown("<span style='color:#6b6b88;font-size:0.85rem'>"
                "Works with any subject — biology, history, CS, economics, law, anything."
                "</span>", unsafe_allow_html=True)

    syllabus = st.text_area("", value=SAMPLE, height=220, placeholder="Paste your syllabus here…")

    if st.button("🚀  Process Syllabus", type="primary"):
        if not st.session_state.api_key:
            st.error("Enter your free Groq API key in the sidebar first. Get one at console.groq.com")
        elif not syllabus.strip():
            st.warning("Paste some syllabus text first.")
        else:
            bus       = MessageBus()
            gclient   = Groq(api_key=st.session_state.api_key)
            planner   = PlannerAgent(gclient, bus)
            retriever = RetrieverAgent(gclient, bus)
            executor  = ExecutorAgent(bus)
            st.session_state.bus = bus

            status = st.empty()

            with st.spinner(""):
                # Step 1 — Planner
                status.markdown(
                    '<div style="background:#0d1a2e;border-left:4px solid #3b82f6;'
                    'padding:0.8rem 1rem;border-radius:8px;color:#93c5fd;margin:4px 0">'
                    '🤖 <b>Planner Agent</b> — parsing syllabus with AI…</div>',
                    unsafe_allow_html=True)
                try:
                    timeline = planner.parse_syllabus(syllabus)
                except json.JSONDecodeError:
                    st.error("AI returned unexpected output. Try again or simplify the syllabus.")
                    st.stop()
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.stop()

                st.session_state.timeline = timeline
                n = len(timeline["deadlines"])

                # Step 2 — Retriever
                resources_map = {}
                progress = st.progress(0)
                for i, item in enumerate(timeline["deadlines"]):
                    status.markdown(
                        f'<div style="background:#160d2e;border-left:4px solid #7c3aed;'
                        f'padding:0.8rem 1rem;border-radius:8px;color:#c4b5fd;margin:4px 0">'
                        f'🔍 <b>Retriever Agent</b> — resources for <em>{item["task"]}</em>…</div>',
                        unsafe_allow_html=True)
                    planner.request_resources(item["task"], item.get("task_type", "other"))
                    try:
                        resources = retriever.find_resources(
                            item["task"], item.get("task_type", "other"), timeline["course"])
                    except Exception:
                        resources = []
                    resources_map[item["task"]] = resources
                    progress.progress((i + 1) / n)

                # Step 3 — Executor
                status.markdown(
                    '<div style="background:#0d2318;border-left:4px solid #059669;'
                    'padding:0.8rem 1rem;border-radius:8px;color:#6ee7b7;margin:4px 0">'
                    '✅ <b>Executor Agent</b> — creating calendar events…</div>',
                    unsafe_allow_html=True)
                events = executor.create_calendar_events(
                    timeline["deadlines"], resources_map, timeline["course"])
                st.session_state.events = events

            status.empty()
            st.success(f"✨ Done! {n} deadlines found · {len(events)} calendar events created.")
            st.balloons()
            st.info("Check the **Timeline** and **Calendar Events** tabs above ↑")


# ── TAB 2: TIMELINE ────────────────────────────────────────

BADGE_MAP = {
    "exam": "badge-exam", "quiz": "badge-quiz",
    "assignment": "badge-assignment", "project": "badge-project",
    "essay": "badge-essay", "lab": "badge-lab",
}

def badge_html(task_type: str) -> str:
    css = BADGE_MAP.get(task_type.lower(), "badge-other")
    return f'<span class="badge {css}">{task_type}</span>'

with tab2:
    if not st.session_state.timeline:
        st.info("👆 Process a syllabus in the first tab to see your timeline.")
    else:
        tl = st.session_state.timeline
        st.markdown(f"### 📚 {tl['course']}")
        st.markdown(f"<span style='color:#6b6b88'>{len(tl['deadlines'])} deadlines · sorted by due date</span>",
                    unsafe_allow_html=True)

        for item in tl["deadlines"]:
            due_dt    = datetime.strptime(item["due_date"],   "%Y-%m-%d")
            start_dt  = datetime.strptime(item["start_date"], "%Y-%m-%d")
            days_work = max((due_dt - start_dt).days, 1)
            days_left = (due_dt - datetime.today()).days

            if days_left < 0:
                dl_str = f"<span style='color:#ef4444'>⚠️ {abs(days_left)}d overdue</span>"
            elif days_left <= 7:
                dl_str = f"<span style='color:#f59e0b'>{days_left}d left</span>"
            else:
                dl_str = f"<span style='color:#6b6b88'>{days_left}d left</span>"

            resources = next(
                (ev["resources"] for ev in st.session_state.events if ev["title"] == item["task"]), [])
            res_html = "".join(
                f'<span style="display:inline-block;background:#1a1a2e;border:1px solid #2e2e50;'
                f'border-radius:6px;padding:3px 9px;font-size:0.77rem;margin:3px;color:#a78bfa">'
                f'📎 {r["title"]}</span>'
                for r in resources
            ) or "<span style='color:#444;font-size:0.8rem'>—</span>"

            weight = item.get("weight", "unknown")
            weight_str = f" · Weight: {weight}" if weight != "unknown" else ""

            st.markdown(f"""
<div class="tw-card">
  {badge_html(item.get("task_type","other"))}
  <h4>{item['task']}</h4>
  <div class="meta">🟢 Start: <b>{item['start_date']}</b> &nbsp;·&nbsp; 🔴 Due: <b>{item['due_date']}</b>{weight_str} &nbsp;·&nbsp; {dl_str}</div>
  <div class="meta">⏱ Work window: <b>{days_work} days</b></div>
  <div style="margin-top:8px">{res_html}</div>
</div>
""", unsafe_allow_html=True)


# ── TAB 3: CALENDAR EVENTS ─────────────────────────────────

with tab3:
    if not st.session_state.events:
        st.info("👆 Process a syllabus in the first tab to see calendar events.")
    else:
        events = st.session_state.events
        st.markdown(f"### 🗓️ {events[0]['course']}")

        c1, c2, c3 = st.columns(3)
        exams = sum(1 for e in events if "exam" in e["task_type"])
        c1.metric("Total Events",      len(events))
        c2.metric("Exams / Midterms",  exams)
        c3.metric("Other Tasks",       len(events) - exams)

        st.markdown("---")

        for ev in events:
            res_items = "".join(
                f'<div style="margin:4px 0;font-size:0.82rem;color:#a0a0c0">'
                f'📌 <b>{r["title"]}</b>'
                f'<span style="color:#555"> ({r.get("type","")}) — {r.get("description","")}</span>'
                f'</div>'
                for r in ev["resources"]
            ) if ev["resources"] else "<div style='color:#444;font-size:0.8rem'>No resources attached</div>"

            st.markdown(f"""
<div class="tw-card">
  {badge_html(ev['task_type'])}
  <h4>📅 {ev['title']}</h4>
  <div class="meta">🟢 Start working: <b>{ev['start']}</b></div>
  <div class="meta">🔴 Due date: <b>{ev['due']}</b> &nbsp;·&nbsp; Weight: {ev['weight']}</div>
  <div class="meta">⏱ {ev['days_to_work']} days of work scheduled</div>
  <div style="margin-top:10px;padding-top:8px;border-top:1px solid #1e1e30">
    <div style="font-size:0.72rem;color:#6b6b88;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.05em">Attached Resources</div>
    {res_items}
  </div>
  <div style="margin-top:8px;background:#1a1a2e;border-radius:6px;padding:6px 10px;font-size:0.8rem;color:#818cf8">
    🔔 {ev['reminder']}
  </div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────

st.divider()
st.markdown("""
<div style='text-align:center;color:#2a2a40;font-size:0.8rem;padding:0.5rem'>
  TaskWeave · Multi-Agent Academic Planner · Built by Krrish Jindal (IIT Roorkee)
</div>
""", unsafe_allow_html=True)

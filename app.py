import streamlit as st
import json
import time
from datetime import datetime, timedelta
import random

# Mock agent responses
class PlannerAgent:
    def __init__(self):
        self.name = "Planner"
    
    def parse_syllabus(self, text):
        # Simulate parsing
        time.sleep(1)
        return {
            "course": "Data Structures and Algorithms",
            "deadlines": [
                {"task": "Assignment 1: Arrays and Linked Lists", "due_date": "2024-04-15", "start_date": "2024-04-08"},
                {"task": "Quiz 1: Complexity Analysis", "due_date": "2024-04-22", "start_date": "2024-04-20"},
                {"task": "Mid-term Exam", "due_date": "2024-05-10", "start_date": "2024-05-03"},
                {"task": "Project: Graph Algorithms Implementation", "due_date": "2024-05-25", "start_date": "2024-05-05"},
                {"task": "Assignment 2: Trees and Heaps", "due_date": "2024-05-18", "start_date": "2024-05-11"},
            ]
        }
    
    def request_resources(self, task):
        return f"[Planner → Retriever] Need resources for: {task}"

class RetrieverAgent:
    def __init__(self):
        self.name = "Retriever"
    
    def find_resources(self, task):
        # Simulate finding resources
        time.sleep(0.5)
        resources = {
            "Assignment 1: Arrays and Linked Lists": ["Lecture notes: Week 1-2", "Tutorial: Array operations.pdf"],
            "Quiz 1: Complexity Analysis": ["Big-O notation guide", "Practice problems set 1"],
            "Mid-term Exam": ["All lecture slides", "Previous year papers", "Study guide chapters 1-5"],
            "Project: Graph Algorithms Implementation": ["Graph theory notes", "BFS/DFS implementation guide"],
            "Assignment 2: Trees and Heaps": ["Binary tree notes", "Heap operations tutorial"],
        }
        return resources.get(task, ["General study materials"])
    
    def respond(self, request):
        return f"[Retriever → Planner] Found resources"

class ExecutorAgent:
    def __init__(self):
        self.name = "Executor"
        self.calendar_events = []
    
    def create_calendar_events(self, deadlines, resources_map):
        # Simulate creating calendar events
        time.sleep(0.5)
        events = []
        for item in deadlines:
            events.append({
                "title": item["task"],
                "start": item["start_date"],
                "due": item["due_date"],
                "resources": resources_map.get(item["task"], []),
                "reminder": f"Start working on {item['task']}"
            })
        self.calendar_events = events
        return events
    
    def send_notification(self, event):
        return f"[Executor] Reminder set for: {event['title']}"

# Initialize agents
if 'planner' not in st.session_state:
    st.session_state.planner = PlannerAgent()
    st.session_state.retriever = RetrieverAgent()
    st.session_state.executor = ExecutorAgent()
    st.session_state.messages = []
    st.session_state.timeline = None
    st.session_state.events = []

st.set_page_config(page_title="TaskWeave", page_icon="🎯", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .planner {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .retriever {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .executor {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    .event-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎯 TaskWeave</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Three AI Agents Working Together to Manage Your Semester</div>', unsafe_allow_html=True)

# Sidebar with agent status
with st.sidebar:
    st.header("Agent Status")
    st.markdown("### 🤖 Planner Agent")
    st.write("Extracts deadlines and creates timeline")
    st.markdown("### 🔍 Retriever Agent")
    st.write("Finds relevant study materials")
    st.markdown("### ✅ Executor Agent")
    st.write("Creates calendar events and reminders")
    
    st.divider()
    st.write("**Agent Communication Log**")
    for msg in st.session_state.messages[-5:]:
        st.text(msg)

# Main content
tab1, tab2, tab3 = st.tabs(["📄 Upload Syllabus", "📅 Timeline", "🗓️ Calendar"])

with tab1:
    st.header("Upload Course Syllabus")
    
    # Sample syllabus text
    sample_text = """
    Data Structures and Algorithms - Spring 2024
    
    Course Schedule:
    - Assignment 1 (Arrays & Linked Lists): Due April 15
    - Quiz 1 (Complexity Analysis): April 22
    - Mid-term Exam: May 10
    - Project (Graph Algorithms): Due May 25
    - Assignment 2 (Trees & Heaps): Due May 18
    """
    
    syllabus_text = st.text_area("Paste syllabus text or upload PDF", sample_text, height=200)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 Process Syllabus", type="primary"):
            with st.spinner("Agents are working..."):
                # Step 1: Planner parses syllabus
                st.markdown('<div class="agent-box planner">📋 <b>Planner Agent:</b> Parsing syllabus...</div>', unsafe_allow_html=True)
                st.session_state.messages.append("[Planner] Analyzing syllabus")
                timeline = st.session_state.planner.parse_syllabus(syllabus_text)
                st.session_state.timeline = timeline
                
                # Step 2: Planner requests resources from Retriever
                st.markdown('<div class="agent-box planner">📋 <b>Planner Agent:</b> Requesting resources from Retriever...</div>', unsafe_allow_html=True)
                resources_map = {}
                
                progress_bar = st.progress(0)
                for i, item in enumerate(timeline["deadlines"]):
                    msg = st.session_state.planner.request_resources(item["task"])
                    st.session_state.messages.append(msg)
                    
                    # Retriever finds resources
                    st.markdown(f'<div class="agent-box retriever">🔍 <b>Retriever Agent:</b> Finding resources for {item["task"]}...</div>', unsafe_allow_html=True)
                    resources = st.session_state.retriever.find_resources(item["task"])
                    resources_map[item["task"]] = resources
                    st.session_state.messages.append(f"[Retriever] Found {len(resources)} resources")
                    
                    progress_bar.progress((i + 1) / len(timeline["deadlines"]))
                
                # Step 3: Executor creates calendar events
                st.markdown('<div class="agent-box executor">✅ <b>Executor Agent:</b> Creating calendar events...</div>', unsafe_allow_html=True)
                st.session_state.messages.append("[Executor] Creating calendar events")
                events = st.session_state.executor.create_calendar_events(timeline["deadlines"], resources_map)
                st.session_state.events = events
                
                st.success("✨ All agents completed their tasks!")
                st.balloons()

with tab2:
    st.header("Semester Timeline")
    if st.session_state.timeline:
        st.subheader(f"📚 {st.session_state.timeline['course']}")
        
        for item in st.session_state.timeline["deadlines"]:
            with st.expander(f"📌 {item['task']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Start Date:** {item['start_date']}")
                    st.write(f"**Due Date:** {item['due_date']}")
                with col2:
                    # Find resources for this task
                    for event in st.session_state.events:
                        if event['title'] == item['task']:
                            st.write("**Resources Found:**")
                            for res in event['resources']:
                                st.write(f"  • {res}")
    else:
        st.info("👆 Upload a syllabus in the first tab to see your timeline")

with tab3:
    st.header("Calendar Events")
    if st.session_state.events:
        st.write(f"**{len(st.session_state.events)} events created**")
        
        for event in st.session_state.events:
            st.markdown(f"""
            <div class="event-card">
                <h4>📅 {event['title']}</h4>
                <p><b>Start working:</b> {event['start']}</p>
                <p><b>Due date:</b> {event['due']}</p>
                <p><b>Reminder:</b> {event['reminder']}</p>
                <p><b>Materials attached:</b> {', '.join(event['resources'][:2])}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👆 Process a syllabus to see calendar events")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <b>TaskWeave</b> - Multi-Agent System for Academic Planning<br>
    Built with Planner, Retriever, and Executor agents working in coordination
</div>
""", unsafe_allow_html=True)

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
        # Actually parse the syllabus text
        time.sleep(1)
        
        import re
        from datetime import datetime, timedelta
        
        # Extract course name from first line or first mention
        lines = text.strip().split('\n')
        course_name = "Course"
        for line in lines[:5]:
            if line.strip() and not line.strip().startswith('-'):
                course_name = line.strip()
                break
        
        # Find all dates and associated tasks
        deadlines = []
        
        # Common patterns for dates
        date_patterns = [
            r'(?:Due|due|DUE)[\s:]*([A-Z][a-z]+\s+\d{1,2}(?:,?\s*\d{4})?)',  # Due: February 20, 2024
            r'([A-Z][a-z]+\s+\d{1,2}(?:,?\s*\d{4})?)',  # February 20, 2024
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 02/20/2024
            r'(\d{4}-\d{2}-\d{2})',  # 2024-02-20
        ]
        
        # Task keywords
        task_keywords = ['assignment', 'quiz', 'exam', 'project', 'midterm', 'mid-term', 'final', 'test', 'homework']
        
        current_year = datetime.now().year
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains a task keyword
            has_task = any(keyword in line_lower for keyword in task_keywords)
            
            if has_task:
                # Try to find a date in this line or next few lines
                search_text = '\n'.join(lines[i:min(i+3, len(lines))])
                
                found_date = None
                task_name = line.strip().lstrip('-').strip()
                
                # Try each date pattern
                for pattern in date_patterns:
                    matches = re.findall(pattern, search_text, re.IGNORECASE)
                    if matches:
                        date_str = matches[0]
                        try:
                            # Parse the date
                            if '/' in date_str:
                                found_date = datetime.strptime(date_str, '%m/%d/%Y')
                            elif '-' in date_str:
                                found_date = datetime.strptime(date_str, '%Y-%m-%d')
                            else:
                                # Try parsing "Month Day" or "Month Day, Year"
                                if ',' in date_str:
                                    found_date = datetime.strptime(date_str, '%B %d, %Y')
                                else:
                                    # No year, assume current or next year
                                    try:
                                        found_date = datetime.strptime(f"{date_str}, {current_year}", '%B %d, %Y')
                                    except:
                                        found_date = datetime.strptime(f"{date_str}, {current_year + 1}", '%B %d, %Y')
                            break
                        except:
                            continue
                
                if found_date:
                    # Calculate start date (1 week before for small tasks, 2-3 weeks for exams/projects)
                    days_before = 7
                    if any(word in line_lower for word in ['exam', 'project', 'midterm', 'mid-term', 'final']):
                        days_before = 14
                    
                    start_date = found_date - timedelta(days=days_before)
                    
                    # Clean up task name
                    if ':' in task_name:
                        task_name = task_name.split(':', 1)[0].strip()
                    task_name = re.sub(r'^\d+\.?\s*', '', task_name)  # Remove leading numbers
                    task_name = re.sub(r'\s+', ' ', task_name)  # Normalize whitespace
                    
                    deadlines.append({
                        "task": task_name,
                        "due_date": found_date.strftime('%Y-%m-%d'),
                        "start_date": start_date.strftime('%Y-%m-%d')
                    })
        
        # Sort by due date
        deadlines.sort(key=lambda x: x['due_date'])
        
        # If no deadlines found, return a helpful message
        if not deadlines:
            deadlines = [{
                "task": "No deadlines detected - please format syllabus with dates",
                "due_date": datetime.now().strftime('%Y-%m-%d'),
                "start_date": datetime.now().strftime('%Y-%m-%d')
            }]
        
        return {
            "course": course_name,
            "deadlines": deadlines
        }
    
    def request_resources(self, task):
        return f"[Planner → Retriever] Need resources for: {task}"

class RetrieverAgent:
    def __init__(self):
        self.name = "Retriever"
    
    def find_resources(self, task):
        # Actually generate relevant resources based on task content
        time.sleep(0.5)
        
        task_lower = task.lower()
        resources = []
        
        # General academic resource types based on task keywords
        if any(word in task_lower for word in ['exam', 'midterm', 'mid-term', 'final']):
            resources.extend([
                'Previous exam papers',
                'Comprehensive study guide',
                'Review notes and summaries',
                'Practice questions'
            ])
        elif 'quiz' in task_lower:
            resources.extend([
                'Quick review notes',
                'Key concepts summary',
                'Practice problems'
            ])
        elif any(word in task_lower for word in ['project', 'research', 'thesis', 'dissertation']):
            resources.extend([
                'Project guidelines and rubric',
                'Research methodology guide',
                'Reference examples',
                'Citation and formatting guide'
            ])
        elif any(word in task_lower for word in ['assignment', 'homework', 'problem set', 'exercise']):
            resources.extend([
                'Lecture notes for this topic',
                'Textbook chapters',
                'Solution examples',
                'Office hours schedule'
            ])
        elif any(word in task_lower for word in ['presentation', 'seminar', 'talk']):
            resources.extend([
                'Presentation guidelines',
                'Sample slides',
                'Public speaking tips'
            ])
        elif any(word in task_lower for word in ['paper', 'essay', 'report', 'writing']):
            resources.extend([
                'Writing guide',
                'Sample papers',
                'Peer review checklist',
                'Grammar and style guide'
            ])
        elif any(word in task_lower for word in ['lab', 'experiment', 'practical']):
            resources.extend([
                'Lab manual',
                'Safety guidelines',
                'Equipment setup guide',
                'Data analysis templates'
            ])
        elif any(word in task_lower for word in ['reading', 'chapter', 'book']):
            resources.extend([
                'Reading guide',
                'Chapter summaries',
                'Discussion questions'
            ])
        else:
            # Generic fallback
            resources.extend([
                'Lecture notes',
                'Recommended readings',
                'Study materials',
                'Online resources'
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_resources = []
        for r in resources:
            if r not in seen:
                seen.add(r)
                unique_resources.append(r)
        
        return unique_resources[:3]  # Return max 3 resources
    
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
    sample_text = """Advanced Database Systems - Spring 2024
Instructor: Dr. Sarah Chen

Course Overview:
This course covers advanced topics in database systems including distributed databases,
NoSQL systems, query optimization, and transaction management.

Important Dates:
- Assignment 1 (SQL Query Optimization): Due February 20, 2024
- Quiz 1 (Indexing and B-Trees): February 27, 2024
- Assignment 2 (Distributed Transactions): Due March 15, 2024
- Mid-term Exam: March 22, 2024 (Covers weeks 1-6)
- Project Proposal: Due April 5, 2024
- Assignment 3 (NoSQL Database Design): Due April 19, 2024
- Quiz 2 (Concurrency Control): April 26, 2024
- Project Implementation: Due May 10, 2024
- Final Exam: May 17, 2024 (Comprehensive)

Prerequisites: Introduction to Databases, basic SQL knowledge
Grading: Assignments (30%), Quizzes (20%), Mid-term (20%), Project (20%), Final (10%)
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

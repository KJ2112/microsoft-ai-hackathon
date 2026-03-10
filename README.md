# TaskWeave

**Three AI agents working together to turn your semester chaos into a manageable plan.**

## What This Does

College students get 5-6 syllabi at the start of each semester, each with assignments, quizzes, projects, and exams. Most people either manually copy everything into a calendar (boring and error-prone) or just wing it and hope they remember (spoiler: they don't). TaskWeave fixes this with three AI agents that actually coordinate with each other to handle your workload.

## The Three Agents

**Planner Agent** reads your syllabus and builds a complete timeline. It doesn't just extract "Assignment due April 15" but figures out you should probably start working on it April 8. Research paper due in week 12? You'll get a reminder to start in week 8.

**Retriever Agent** finds study materials. When the Planner creates your timeline, the Retriever searches for relevant lecture notes, past assignments, and resources you'll actually need.

**Executor Agent** makes it all happen. It creates calendar events, sets up reminders, and attaches the materials the Retriever found so everything's in one place.

The key part: these agents talk to each other. The Planner asks the Retriever for notes, the Executor tells the Planner what's done so it can adjust future suggestions. It's distributed intelligence working on a shared goal.

## Quick Start

```bash
pip install streamlit
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## How to Use It

1. Paste your course syllabus text into the box (or use the sample one that's already there)
2. Click "Process Syllabus" and watch the agents work in real-time
3. Check the Timeline tab to see when you should start working on things
4. Look at the Calendar tab to see all your events with study materials attached

You can watch the agents communicate in the sidebar. You'll see messages like "[Planner] Analyzing syllabus" and "[Retriever] Found 3 resources" as they coordinate.

## Live Demo

**Deployment**: https://microsoft-ai-hackathon-lxm4g6bdclweigebxjwd7j.streamlit.app/

**Presentation + Video Demo**: https://drive.google.com/drive/folders/15NWyZzOgP6qLeoKskrfPVV-wtrUOTNti

## What I Built This For

This was made for the Microsoft AI Unlocked hackathon's Agent Teamwork challenge. The goal was to show three agents genuinely cooperating through message passing rather than just building three separate tools. The focus was on proving the coordination pattern works, not on production polish.

## Current Status

What works right now:
- Three agents with message-based communication
- Timeline extraction with smart start dates
- Resource discovery and mapping
- Calendar event generation
- Visual UI showing agent coordination in real-time

What's using mock data (for demo purposes):
- The syllabus parsing (hardcoded to show the architecture)
- Resource retrieval (showing the pattern without real document search)

What could be added with more time:
- Azure OpenAI for actual syllabus parsing with GPT-4
- Azure AI Search for real document retrieval
- Calendar API integrations (Google Calendar, Outlook)
- Deployed on Azure Container Apps for real scalability

## Tech Stack

Python, Streamlit, basic agent architecture with message passing. Kept it simple to focus on the agent coordination concept.

## Sample Syllabus

If you want to test with a longer syllabus, paste this:

```
Advanced Database Systems - Spring 2024
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

Prerequisites:
Students should have completed Introduction to Databases and have basic understanding
of SQL, normalization, and relational algebra.

Grading:
Assignments (30%), Quizzes (20%), Mid-term (20%), Project (20%), Final (10%)
```

---

Built by Krrish Jindal (IIT Roorkee) for Microsoft AI Unlocked 2026

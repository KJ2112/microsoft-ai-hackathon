# TaskWeave

**Three AI agents working together to turn your semester chaos into a manageable plan.**

## What This Does

College students get 5-6 syllabi at the start of each semester, each with assignments, quizzes, projects, and exams. Most people either manually copy everything into a calendar (boring and error-prone) or just wing it and hope they remember (spoiler: they don't). TaskWeave fixes this with three AI agents that actually coordinate with each other to handle your workload.

## The Three Agents

**Planner Agent** reads your syllabus and builds a complete timeline. It doesn't just extract "Assignment due April 15" but figures out you should probably start working on it April 8. Research paper due in week 12? You'll get a reminder to start in week 8. It uses pattern matching to detect dates in multiple formats and identifies task types automatically.

**Retriever Agent** finds study materials based on what type of task it is. Exams get study guides and previous papers. Essays get writing guides and citation help. Labs get safety guidelines and data templates. It adapts to the task type, not the subject, so it works for biology, history, economics, or any course.

**Executor Agent** makes it all happen. It creates calendar events, sets up reminders, and attaches the materials the Retriever found so everything's in one place.

The key part: these agents talk to each other. The Planner asks the Retriever for resources, the Retriever responds with relevant materials, and the Executor creates events with everything attached. It's distributed intelligence working on a shared goal.

## Quick Start

```bash
pip install streamlit
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## How to Use It

1. Paste your course syllabus text into the box (works with any subject - biology, history, literature, economics, CS, anything)
2. Click "Process Syllabus" and watch the agents work in real-time
3. Check the Timeline tab to see when you should start working on things
4. Look at the Calendar tab to see all your events with study materials attached

You can watch the agents communicate in the sidebar. You'll see messages like "[Planner] Analyzing syllabus" and "[Retriever] Found 3 resources" as they coordinate.

## Live Demo

**Deployment**: https://microsoft-ai-hackathon-lxm4g6bdclweigebxjwd7j.streamlit.app/

**Presentation + Video Demo**: https://drive.google.com/drive/folders/15NWyZzOgP6qLeoKskrfPVV-wtrUOTNti

## What I Built This For

This was made for the Microsoft AI Unlocked hackathon's Agent Teamwork challenge. The goal was to show three agents genuinely cooperating through message passing rather than just building three separate tools. The focus was on proving the coordination pattern works with real parsing logic.

## Current Status

What works right now:
- Three agents with message-based communication
- Real syllabus parsing with regex for multiple date formats
- Automatic task detection (assignments, quizzes, exams, projects, essays, labs, presentations)
- Smart start date calculation based on task complexity
- Resource generation based on task type (works for any subject)
- Calendar event generation with attached resources
- Visual UI showing agent coordination in real-time

What this is:
- A working prototype showing multi-agent coordination
- Real text parsing using pattern matching
- Subject-agnostic resource recommendation
- Proof of concept for distributed agent architecture

What could be added with more time:
- Azure OpenAI for even smarter syllabus parsing with LLMs
- Azure AI Search for actual document retrieval from uploaded files
- Calendar API integrations (Google Calendar, Outlook, iCal)
- Email/SMS notifications through Executor
- Deployed on Azure Container Apps for real scalability
- User accounts and persistence

## Tech Stack

Python, Streamlit, regex-based parsing, agent architecture with message passing. Kept it focused on the agent coordination pattern while making the parsing actually work.

## Sample Syllabi to Test

The app works with any subject. Try these examples:

**Biology:**
```
Cell Biology - Spring 2024

- Lab Report 1 (Microscopy): Due March 15, 2024
- Quiz on Cell Structure: March 22, 2024
- Midterm Exam: April 10, 2024
- Research Paper on Photosynthesis: Due May 5, 2024
- Final Practical Exam: May 20, 2024
```

**History:**
```
Modern European History - Fall 2024

- Essay on French Revolution: September 30, 2024
- Reading Response (Chapters 1-5): October 15, 2024
- Midterm Examination: November 1, 2024
- Research Project Proposal: November 20, 2024
- Final Presentation: December 8, 2024
```

**Economics:**
```
Microeconomics - Spring 2024

- Problem Set 1: February 28, 2024
- Quiz on Supply & Demand: March 10, 2024
- Midterm Exam: April 5, 2024
- Economic Analysis Paper: May 1, 2024
- Final Exam: May 18, 2024
```

The Planner extracts dates in formats like "March 15, 2024", "September 30", "2024-04-05", or "02/28/2024". The Retriever then suggests resources based on whether it's a lab, essay, exam, quiz, project, etc.

---

Built by Krrish Jindal (IIT Roorkee) for Microsoft AI Unlocked 2024

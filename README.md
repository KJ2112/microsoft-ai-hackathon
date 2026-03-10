# TaskWeave

**Three AI agents working together to turn your semester chaos into a manageable plan.**

## What This Does

College students get 5-6 syllabi at the start of each semester, each with assignments, quizzes, projects, and exams. Most people either manually copy everything into a calendar (boring and error-prone) or just wing it and hope they remember. TaskWeave fixes this with three AI agents that coordinate through a shared message bus to handle your workload.

## The Three Agents

**Planner Agent** uses an LLM to read your syllabus and build a complete timeline. It doesn't just extract "Assignment due April 15" — it figures out you should probably start working on it April 8. Research paper due in week 12? You'll see a start date in week 8. It handles multiple date formats and identifies task types automatically.

**Retriever Agent** finds study materials based on what type of task it is. Exams get past paper suggestions and study guides. Essays get writing and citation resources. Labs get safety guidelines and data templates. It adapts to the task type, not the subject, so it works for biology, history, economics, or any course.

**Executor Agent** assembles everything into structured calendar events with reminders and the Retriever's resources attached, so each event is self-contained.

The key part: **these agents communicate through a shared MessageBus**. The Planner sends a message requesting resources, the Retriever replies with materials, and the Executor creates events with everything included. You can watch every message in real time in the sidebar.

## Quick Start

```bash
pip install streamlit groq
streamlit run app.py
```

Open your browser to `http://localhost:8501`

Get a **free** Groq API key at [console.groq.com](https://console.groq.com) and paste it in the sidebar.

## How to Use It

1. Enter your free Groq API key in the sidebar
2. Paste your course syllabus text (any subject works)
3. Click **Process Syllabus** and watch the three agents work in real-time
4. Check the **Timeline** tab to see when you should start working on each task
5. Check the **Calendar Events** tab to see all events with study resources attached

Watch the **Inter-Agent Message Log** in the sidebar — you'll see exactly when Planner talks to Retriever, when Retriever sends resources to Executor, and so on.

## Live Demo

**Deployment**: https://microsoft-ai-hackathon-lxm4g6bdclweigebxjwd7j.streamlit.app/

**Presentation + Video Demo**: https://drive.google.com/drive/folders/15NWyZzOgP6qLeoKskrfPVV-wtrUOTNti

## Sample Syllabi to Test

The app works with any subject. Try pasting these:

**Biology:**
```
Cell Biology - Spring 2025

- Lab Report 1 (Microscopy): Due March 15, 2025
- Quiz on Cell Structure: March 22, 2025
- Midterm Exam: April 10, 2025
- Research Paper on Photosynthesis: Due May 5, 2025
- Final Practical Exam: May 20, 2025
```

**History:**
```
Modern European History - Fall 2025

- Essay on French Revolution: September 30, 2025
- Reading Response (Chapters 1-5): October 15, 2025
- Midterm Examination: November 1, 2025
- Research Project Proposal: November 20, 2025
- Final Presentation: December 8, 2025
```

**Microeconomics:**
```
Microeconomics - Spring 2025

- Problem Set 1: February 28, 2025
- Quiz on Supply & Demand: March 10, 2025
- Midterm Exam: April 5, 2025
- Economic Analysis Paper: May 1, 2025
- Final Exam: May 18, 2025
```

## Tech Stack

Python, Streamlit, Groq API (LLaMA 3), agent architecture with message-passing via a shared MessageBus.

## What's Next (with more time / resources)

- Azure OpenAI / GPT-4 for higher accuracy parsing
- Azure AI Search for retrieval from student's own uploaded notes
- Real calendar API integrations (Google Calendar, Outlook, iCal)
- Azure Container Apps deployment for scalability
- Email / SMS notifications through the Executor
- User accounts and multi-semester persistence

---

Built by Krrish Jindal (IIT Roorkee) for Microsoft AI Unlocked 2026

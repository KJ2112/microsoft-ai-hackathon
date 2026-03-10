# TaskWeave

**Three AI agents working together to turn your semester chaos into a manageable plan.**

## The Problem

Every semester, students get 5–6 syllabi each packed with 15–20 deadlines across different formats, subjects, and dates. Most students either spend 30+ minutes manually copying everything into a calendar  or just wing it and end up in last-minute panic. Neither works.

## The Solution

TaskWeave takes your raw syllabus text : one subject or all of them pasted together  and runs three coordinating AI agents that produce a complete, resource-backed semester plan automatically.

## The Three Agents

**Planner Agent** is the coordinator. It first detects how many courses are in the input and splits them. Then for each course it uses an LLM to extract every deadline and calculate a smart start date based on task complexity, a quiz gets a 5-day head start, a research paper gets 21 days. It sends messages to the Retriever requesting resources, and coordinates the overall flow.

**Retriever Agent** responds to the Planner's requests. For each task it receives, it uses an LLM to suggest three specific, practical study resources tailored to both the task type and the subject. A biology lab gets different resources than a history essay. It then passes everything to the Executor.

**Executor Agent** assembles the final output. It takes the deadlines from the Planner and the resources from the Retriever, and creates structured calendar events with reminders and all materials attached , so every event is self-contained.

The key architectural point: **these agents don't just run sequentially , they communicate**. Messages flow through a shared `MessageBus`. The Planner requests help, the Retriever responds, the Executor confirms completion. You can watch every message in real time in the sidebar.

## Quick Start

```bash
pip install streamlit groq
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

Get a **free** Groq API key at [console.groq.com](https://console.groq.com) and paste it in the sidebar.

## How to Use

1. Enter your Groq API key in the sidebar
2. Pick a demo subject from the dropdown, or paste your own syllabus
3. To show multi-subject support, select **"🔀 Multiple Subjects (CS + Biology + Economics)"**
4. Click **Process Syllabus** and watch the agents work through each course
5. Check the **Timeline** tab : deadlines sorted with smart start dates and attached resources
6. Check the **Calendar Events** tab : full events with reminders and study materials per course

The **Inter-Agent Message Log** in the sidebar shows every message passing between agents in real time.

## Multi-Subject Support

Paste syllabi from multiple courses together and the Planner Agent automatically detects the course boundaries, splits them, and processes each one independently through the full agent pipeline. The Timeline and Calendar views then show each course under its own section.

## Live Demo

**Deployment**: https://microsoft-ai-hackathon-lxm4g6bdclweigebxjwd7j.streamlit.app/

**Presentation + Video**: https://drive.google.com/drive/folders/15NWyZzOgP6qLeoKskrfPVV-wtrUOTNti

## Tech Stack

- **Python + Streamlit** : UI and app framework
- **Groq API (LLaMA 3.3 70B)** : powers all three agents (free tier)
- **MessageBus** : custom in-process message passing between agents
- **Agent architecture** : three specialised agents with distinct roles and real coordination

## What's Next

With more time and resources:
- **Azure OpenAI** for even more accurate syllabus parsing
- **Azure AI Search** to retrieve from the student's own uploaded notes
- **Azure Container Apps** to deploy each agent as its own scalable microservice
- **Azure Service Bus** to replace the in-process MessageBus with a real distributed queue
- **Calendar API integrations** : Google Calendar, Outlook, iCal export
- **Email / SMS notifications** through the Executor agent
- **User accounts** and multi-semester history

---

Built by Krrish Jindal (IIT Roorkee) for Microsoft AI Unlocked 2026

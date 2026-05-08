# AI Social Media Manager Agent

An AI-powered Social Media Management System built using Python, Streamlit, n8n, and Groq LLMs.  
This project automates social media content generation, scheduling, and analytics using AI agents and workflow automation.

---

# Features

- AI-generated social media content
- Multi-platform support
  - LinkedIn
  - Twitter/X
  - Instagram
  - Facebook
- Content scheduling using n8n workflows
- AI-powered analytics insights
- Draft and scheduled post management
- Streamlit interactive dashboard
- REST API integration
- Automation pipeline using AI agents

---

# Tech Stack

## Frontend
- Streamlit

## Backend
- Python

## AI / LLM
- Groq LLM (`llama-3.1-8b-instant`)

## Automation
- n8n

## APIs
- REST APIs
- Webhooks

---

# Project Architecture

User → Streamlit UI → AI Agent → Tools Layer → n8n Workflow → Groq LLM → Response

---

# Folder Structure

```bash
├── app.py
├── agent.py
├── tools.py
├── data.json
├── requirements.txt
├── .gitignore
└── README.md


# Live App :
 *(https://ai-social-media-manager-cgpycew8vskpvp2qmsv75m.streamlit.app/)*

# 🌍 ClimateSense AI

> AI-Powered Personal Climate Coach | SDG 13 – Climate Action

ClimateSense AI is an intelligent web application that helps users understand their daily carbon footprint and receive personalized sustainability recommendations through a multi-agent AI workflow.

Instead of acting as a chatbot, ClimateSense AI processes a user's lifestyle habits through a structured LangGraph pipeline, calculates carbon emissions using deterministic algorithms, and generates actionable insights using Google's Gemini AI.

---

# Features

- Carbon Footprint Estimation
- AI-Powered Sustainability Recommendations
- Daily Eco Challenge
- Sustainability Report Generation
- Modern React Dashboard
- Multi-Agent LangGraph Workflow
- FastAPI Backend
- Gemini AI Integration
- PostgreSQL Ready Architecture

---

# Tech Stack

## Frontend

- React.js
- Vite
- JavaScript
- CSS
- Axios

## Backend

- FastAPI
- Python
- LangGraph
- LangChain
- Google Gemini API
- SQLAlchemy
- PostgreSQL

---

# Project Architecture

```
React Frontend
       │
       ▼
 FastAPI REST API
       │
       ▼
 LangGraph Workflow
       │
       ▼
 Gemini AI + Carbon Calculator
       │
       ▼
 JSON Response
       │
       ▼
 React Dashboard
```

More details are available in:

- ARCHITECTURE.md
- WORKFLOW.md

---

# Application Workflow

1. User enters daily lifestyle information.
2. FastAPI validates the request.
3. LangGraph executes the AI workflow.
4. Carbon emissions are calculated.
5. Gemini generates personalized recommendations.
6. Daily Eco Challenge is created.
7. Sustainability Report is generated.
8. Results are displayed on the dashboard.

---

# Folder Structure

```
ClimateSense-AI/

frontend/
backend/
README.md
ARCHITECTURE.md
WORKFLOW.md
```

---

# Running the Project

## Backend

```bash
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Render Backend Deployment

Create a Python web service from the repository root.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```env
DATABASE_URL=your_postgres_url
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_URL=https://your-frontend-domain
```

The `.python-version` file pins Render to Python 3.12 so binary wheels are used
for packages such as `pydantic-core` instead of attempting a Rust build.

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# API Endpoint

```
POST /api/analyze
```

Example Request

```json
{
  "transport":"Car - 20 km",
  "electricity":"AC - 6 hours",
  "water":"10 minute shower",
  "food":"Vegetarian",
  "waste":"2 plastic bottles"
}
```

---

# Future Improvements

- User Authentication
- Profile Management
- Saved Analysis History
- Weekly Reports
- Leaderboards
- Carbon Tracking
- Mobile Application

---

# SDG Alignment

This project contributes towards

**United Nations Sustainable Development Goal 13**

Climate Action

---

# Author

Aishwarya K P

Built as an AI-powered sustainability assistant using LangGraph and Gemini AI.

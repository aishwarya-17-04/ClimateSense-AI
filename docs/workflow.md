# ClimateSense AI Workflow

## Overview

ClimateSense AI follows a structured AI workflow powered by LangGraph.

Each node performs one specific responsibility before passing the updated state to the next node.

---

# Workflow Diagram

```
User
 │
 ▼
React Frontend
 │
 ▼
POST /api/analyze
 │
 ▼
FastAPI
 │
 ▼
Input Validator
 │
 ▼
Habit Analyzer
 │
 ▼
Carbon Calculator
 │
 ▼
Impact Analyzer
 │
 ├──────────────┐
 ▼              ▼
Recommendation  Challenge
Generator       Generator
 │              │
 └──────┬───────┘
        ▼
Report Generator
        │
        ▼
JSON Response
        │
        ▼
React Dashboard
```

---

# Step 1 — User Input

The user enters information about transportation, electricity usage, water consumption, food habits, and waste generation through the React interface.

---

# Step 2 — Request Validation

FastAPI validates the request using Pydantic models before invoking the LangGraph workflow.

---

# Step 3 — Habit Analysis

The Habit Analyzer interprets the user's lifestyle data into structured information suitable for carbon calculations.

---

# Step 4 — Carbon Calculation

A deterministic carbon calculator estimates emissions across all lifestyle categories.

---

# Step 5 — Impact Analysis

The system identifies the highest emission contributors and prepares contextual insights.

---

# Step 6 — AI Recommendation Generation

Gemini AI generates personalized sustainability recommendations based on the analyzed data.

---

# Step 7 — Daily Eco Challenge

The system creates a practical sustainability challenge encouraging users to reduce their environmental impact.

---

# Step 8 — Sustainability Report

A comprehensive report summarizing the user's carbon footprint, recommendations, and challenge is generated.

---

# Step 9 — Response Delivery

FastAPI returns the final JSON response to the React frontend, where it is presented through an interactive dashboard.

---

# Benefits of the Workflow

- Modular Design
- Deterministic Carbon Calculation
- AI-Assisted Recommendations
- Scalable Architecture
- Easy Maintenance
- Independent Node Testing
- Future Ready for Authentication and Persistence
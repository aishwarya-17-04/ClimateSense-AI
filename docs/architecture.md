# ClimateSense AI Architecture

## Overview

ClimateSense AI follows a layered architecture that separates the user interface, business logic, AI orchestration, and response generation into independent modules.

The architecture emphasizes modularity, maintainability, scalability, and deterministic carbon calculations while leveraging generative AI for personalized sustainability guidance.

---

# High-Level Architecture

```
                React Frontend
                       │
                       ▼
             FastAPI REST API
                       │
                       ▼
              LangGraph Workflow
                       │
      ┌────────────────┴──────────────┐
      ▼                               ▼
Carbon Calculation            Gemini AI Agents
      │                               │
      └───────────────┬───────────────┘
                      ▼
             Structured JSON Response
                      │
                      ▼
              React Dashboard
```

---

# System Components

## Frontend

Responsible for

- User Interface
- Form Handling
- Dashboard
- Recommendations
- Report Display

Technology

- React
- Vite
- Axios

---

## Backend

Responsible for

- REST API
- Request Validation
- LangGraph Execution
- Response Serialization

Technology

- FastAPI
- Pydantic

---

## LangGraph Orchestrator

Coordinates the execution of multiple AI nodes.

Responsibilities

- State Management
- Sequential Execution
- Error Handling
- Node Communication

---

# AI Workflow Nodes

### Input Validator

Validates incoming user data.

---

### Habit Analyzer

Extracts structured lifestyle habits from user input.

---

### Carbon Calculator

Performs deterministic carbon emission calculations.

---

### Impact Analyzer

Identifies the major contributors to the user's carbon footprint.

---

### Recommendation Generator

Uses Gemini AI to generate personalized sustainability recommendations.

---

### Challenge Generator

Creates a daily eco-friendly challenge.

---

### Report Generator

Combines all outputs into a sustainability report.

---

# Design Principles

- Single Responsibility Principle
- Separation of Concerns
- Modular Architecture
- Deterministic Calculations
- AI-Assisted Decision Support
- Scalable Node-Based Design

---

# Technology Stack

Frontend

- React
- Vite

Backend

- FastAPI
- Python

AI

- LangGraph
- LangChain
- Google Gemini

Database

- PostgreSQL (prepared for persistence)

Deployment

- Render
- Vercel

---

# Deployment Architecture

```
Users

↓

Vercel

↓

FastAPI (Render)

↓

Gemini API

↓

JSON Response

↓

Browser
```

---

# Future Expansion

- JWT Authentication
- User Profiles
- Saved Reports
- Analytics Dashboard
- Multi-user Support
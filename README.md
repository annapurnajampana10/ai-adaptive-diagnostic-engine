## AI-Driven Adaptive Diagnostic Engine

Backend: **FastAPI + MongoDB (Motor)**  
Frontend: **React (Vite)**
AI Integraton: **Open AI API** (Deterministic fallback scoring if API key is unavailable)

This project delivers a 1D adaptive diagnostic prototype that selects questions based on an estimated learner level and provides AI-driven feedback when an LLM key is configured.

## Requirements coverage (assignment mapping)

- **Database (MongoDB Atlas or local)**: Implemented (Motor client, configurable via `.env`).
- **Question bank (>= 20 GRE-style questions)**: Implemented via `scripts/seed_questions.py`.
  - Each question includes `difficulty` (0.1–1.0), `topic`, `tags`, `options`, and `correct_answer`.
- **Adaptive algorithm**: Implemented in `app/services/adaptive.py` and `app/routes/diagnostic.py`.
  - Baseline starts at **0.5** (stored in session).
  - Next question difficulty shifts based on performance.
- **AI integration (OpenAI)**: Implemented in `app/services/llm.py`.
  - Evaluates answers and generates AI feedback.
  - If `OPENAI_API_KEY` is missing or quota is exhausted, the system falls back to a deterministic scoring heuristic.
  - After **answered questions**, the system generates a **personalized 3-step study plan**.
- **Architecture**: Modular FastAPI app with separate `routes/`, `services/`, `schemas/`, and `db/`.
- **API**: `GET /next-question`, `POST /submit-answer` (plus convenience endpoints `/` and `/health`).

## Project structure

- `app/main.py`: FastAPI app + CORS
- `app/routes/diagnostic.py`: API endpoints + session + question selection
- `app/services/adaptive.py`: adaptive difficulty helpers
- `app/services/llm.py`: AI answer evaluation + study plan generation
- `app/db/mongo.py`: MongoDB connection + indexes
- `scripts/seed_questions.py`: seeds/updates question bank
- `frontend/`: Vite + React UI

## Setup

### 1) Backend (FastAPI)

Create and activate a virtualenv, then install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```bash
copy .env.example .env
```

Seed questions (requires MongoDB running):

```bash
python scripts/seed_questions.py
```

Run the backend:

```bash
uvicorn app.main:app --reload --port 8080
```

### 2) Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Open the UI at `http://localhost:5173`.

## Adaptive logic (high level)

The system stores a session document in MongoDB (`user_sessions`) including:

- `ability`: numeric estimate (starts at 0.5)
- `difficulty_level`: `easy | medium | hard` (starts at `medium`)
- `asked_question_ids`, `answers`, and `topic_stats`

Selection:

- A numeric target difficulty is computed from `difficulty_level` (easy≈0.3, medium≈0.5, hard≈0.8).
- The next question is selected from a window around the target; previously asked questions are avoided where possible.

Difficulty update rule (per answer score):

- If score > 0.7 → move harder
- If score < 0.4 → move easier
- Otherwise → keep same difficulty
After **answered questions**, the backend generates a **personalized study plan** based on the learner’s performance and weak areas.

## API documentation

FastAPI interactive docs:

- Swagger UI: `GET /docs`
- OpenAPI JSON: `GET /openapi.json`

### `GET /next-question`

Query params:

- `session_id` (optional): if omitted, a new session is created.

Response:

- `session`: session info (including current `difficulty_level`)
- `question`: next question object (or null if exhausted)

### `POST /submit-answer`

Body:

```json
{
  "session_id": "string",
  "question_id": "string",
  "selected_answer": "string"
}
```

Flow:

user answer → evaluate answer (LLM/heuristic) → score+feedback → store in MongoDB →
update difficulty level → fetch next question → return feedback+score+next question

Response includes:

- `feedback`: AI-generated explanation
- `score`: numeric score between 0.0–1.0
- `next_question`: question object (or null)
- `study_plan`: array of recommendations (generated after 10 answers)
- session metadata

  ## Study Plan Generation

After the learner answers **10 questions**, the backend analyzes the session performance and generates a **personalized 3-step study plan**.

This plan is returned in the `/submit-answer` response when `answered_count >= 10`.

Example:

```json
"study_plan": [
  "Review fundamental concepts related to incorrect answers",
  "Practice medium-difficulty questions to strengthen understanding",
  "Attempt timed practice tests to improve speed and accuracy"
]
```
## Notes on LLM usage

- Set `OPENAI_API_KEY` in `.env` to enable real LLM feedback.
- If OpenAI returns `insufficient_quota` (429), the backend will return a clear message indicating billing/credits are required.

# AI-Driven Adaptive Diagnostic Engine (FastAPI + MongoDB)

This project implements an adaptive diagnostic test engine:

- **MongoDB collections**: `questions`, `user_sessions`
- **Adaptive algorithm**: start ability at **0.5**, update by **±0.1**, next question difficulty matches ability
- **LLM integration**: after **answers**, generates a **personalized 3-step study plan** (OpenAI if configured; otherwise a deterministic fallback plan)

## Project Structure

adaptive-diagnostic-engine/
  app/
    core/config.py
    db/mongo.py
    routes/diagnostic.py
    schemas/
    services/
    main.py
  scripts/
    seed_questions.py
  requirements.txt
  .env.example
  README.md
```

## Setup (Windows PowerShell)

### 1) Create & activate a virtual environment

```powershell
cd C:\Users\anuja\adaptive-diagnostic-engine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables

Copy `.env.example` to `.env` and edit values as needed:

- **MONGODB_URI**: e.g. `mongodb://localhost:27017`
- **MONGODB_DB**: e.g. `adaptive_diagnostic`
- (Optional) **OPENAI_API_KEY** and **OPENAI_MODEL**

### 4) Seed questions (20+)

```powershell
python -m scripts.seed_questions
```

### 5) Run the API

```powershell
uvicorn app.main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs`

## API endpoints

### GET `/next-question`

Creates a new session if you omit `session_id`.

Example:

`GET /next-question`

or

`GET /next-question?session_id=<id>`

Response includes:

- `session.id`
- `session.ability`
- `question` (without `correct_answer`)

### POST `/submit-answer`

Body:

```json
{
  "session_id": "SESSION_ID",
  "question_id": "QUESTION_ID",
  "selected_answer": "YOUR_SELECTED_OPTION"
}
```

Returns:

- whether the answer was `correct`
- updated `ability`
- `next_question`
- `study_plan` (after 10 answers)

## Notes

- **Ability clamp**: stays within **0.1–1.0**, rounded to 1 decimal.
- **Question matching**: searches within a difficulty window around current ability and avoids repeats when possible.
- **LLM fallback**: if `OPENAI_API_KEY` is not set, a heuristic 3-step plan is returned.

## AI Log

During development of this project, AI tools such as Cursor and ChatGPT were used to accelerate implementation and debugging.

### How AI helped

- Assisted in generating the initial **FastAPI project structure** and modular architecture.
- Helped design the **adaptive diagnostic algorithm logic** for selecting questions based on learner ability.
- Provided suggestions for **MongoDB schema design** and session tracking.
- Assisted with **React frontend integration** for displaying questions, feedback, and study plans.
- Helped debug issues related to:
  - API responses
  - frontend state updates
  - study plan rendering after 10 questions
- Generated fallback logic when **OpenAI API quota errors occurred**.

### Challenges where manual debugging was required

- Ensuring the **study plan generated in the backend was properly displayed in the frontend UI**.
- Adjusting the **answer evaluation scoring logic**, as initial implementation returned constant scores.
- Debugging **session state updates between FastAPI and React**.

AI tools significantly reduced development time by helping with boilerplate code generation and debugging suggestions, while final implementation decisions and integration fixes were handled manually.

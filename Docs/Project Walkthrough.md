# 🥘 GourmetAI — Project File-by-File Walkthrough

> **Total source files:** ~50  |  **Total hand-written code:** ~4,700 lines  |  **Database:** 101 MB (12,485 restaurants)

---

## What does this project actually do?

A user opens the app, types a Bangalore neighborhood, picks a cuisine and budget range, and clicks **"Find My Match."** Behind the scenes, the system:

1. **Queries a local SQLite database** (pre-cleaned from 51K raw Zomato records) using smart SQL filters.
2. **Scores the matches** with a mathematical heuristic (70% rating + 30% log-scaled votes).
3. **Sends the top 20 candidates to Google Gemini AI**, which writes a personalized explanation for each restaurant.
4. If Gemini is slow or rate-limited, the system **instantly falls back** to heuristic templates — the user never sees an error.
5. Results are displayed as styled cards with match rationale bubbles.

---

## Project Root

| File | What it does | Why it exists |
|------|-------------|---------------|
| [`.env`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/.env) | Stores API keys (`GEMINI_API_KEY`) and feature flags (`BYPASS_LLM=true`) | Keeps secrets out of code. Streamlit Cloud reads these from its Secrets panel instead. |
| [`.env.example`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/.env.example) | Template showing which env vars are needed | So a new developer knows what to configure without seeing real keys. |
| [`requirements.txt`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/requirements.txt) | Lists all Python dependencies (FastAPI, Streamlit, google-genai, pandas, etc.) | `pip install -r requirements.txt` sets up the entire backend. Streamlit Cloud auto-reads this on deploy. |
| [`setup.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/setup.py) | Makes `zomato_ai` an installable Python package | Allows `from zomato_ai.phase2.api import ...` imports to work cleanly everywhere. |
| [`streamlit_app.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/streamlit_app.py) | **The Streamlit deployment entry point** (245 lines) | A full interactive dashboard that reproduces the entire concierge experience in pure Python — for deploying the backend on Streamlit Community Cloud. |
| [`zomato_restaurants.db`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_restaurants.db) | SQLite database file (101 MB, 12,485 restaurants) | The cleaned, indexed, ready-to-query data store that powers every search. |

---

## `zomato_ai/` — The Python Backend Package

### Core Configuration

| File | Lines | What it does | Why it exists |
|------|-------|-------------|---------------|
| [`__init__.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/__init__.py) | 2 | Marks `zomato_ai` as a Python package | So Python recognizes the folder as importable. |
| [`config.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/config.py) | 32 | Central settings manager using Pydantic `BaseSettings` | Loads `.env` values, validates types, and exposes `settings.GEMINI_API_KEY`, `settings.BYPASS_LLM`, `settings.db_path` globally. One source of truth for all configuration. |

---

### Phase 1 — Data Ingestion & Cleaning (`zomato_ai/phase1/`)

| File | Lines | What it does | Why it exists |
|------|-------|-------------|---------------|
| [`ingestion.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/phase1/ingestion.py) | 238 | Downloads raw Zomato CSV from Hugging Face, cleans it, and loads it into SQLite | **This is the data pipeline.** It handles: regex price cleaning (`"1,200"` → `1200`), null rating parsing (`"NEW"` → `None`), multi-tier median cost imputation (fills missing prices using neighborhood + restaurant type medians), deduplication, and SQLite index creation on `location`, `approx_cost`, and `rate`. |

> **When do you run this?** Once, at project setup. After it finishes, `zomato_restaurants.db` is ready and never needs to be regenerated unless you want fresh data.

---

### Phase 2 — Backend API & Heuristic Scoring (`zomato_ai/phase2/`)

| File | Lines | What it does | Why it exists |
|------|-------|-------------|---------------|
| [`models.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/phase2/models.py) | 21 | Pydantic schema definitions (`RecommendationRequest`, `RestaurantResponse`, `RecommendationResponse`) | Validates every API input and output. If someone sends a budget of `-500`, Pydantic rejects it before it reaches the database. |
| [`repository.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/phase2/repository.py) | 123 | Database access layer — runs parameterized SQL queries against SQLite | Encapsulates all SQL logic. Exposes methods like `get_candidate_restaurants(location, budget, cuisine, rating)`, `get_unique_locations()`, `get_unique_cuisines()`. Keeps raw SQL out of the API layer. |
| [`filtering.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/phase2/filtering.py) | 53 | The mathematical scoring algorithm | Computes `S = 0.70 × normalized_rating + 0.30 × log_scaled_votes` for each candidate, then sorts descending. This is how we pick the "best" restaurants without asking the AI to read thousands of rows. |
| [`api.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/phase2/api.py) | 189 | **The FastAPI application** — defines all HTTP endpoints | The central hub. Handles: `GET /api/locations`, `GET /api/cuisines`, `POST /api/recommend`, and serves static files. Contains the `BYPASS_LLM` fast-path check and the `generate_fallback_response()` function for heuristic templates. |

> **Data flow in Phase 2:**
> `User request` → `api.py` validates input → `repository.py` queries SQLite → `filtering.py` scores results → top 20 candidates are selected.

---

### Phase 3 — AI / LLM Integration (`zomato_ai/phase3/`)

| File | Lines | What it does | Why it exists |
|------|-------|-------------|---------------|
| [`prompt_builder.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/phase3/prompt_builder.py) | 50 | Constructs the text prompt sent to Gemini | Formats the user's preferences and the candidate restaurant JSON into a clean instruction template. Keeps prompt engineering logic separate from API transport. |
| [`llm_client.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/phase3/llm_client.py) | 116 | **Gemini API client manager** | Initializes the `google-genai` SDK client with a strict 2-second timeout and disabled auto-retries. Contains the system instruction rules (e.g., "recommend ALL candidates," "if cuisine is unspecified, return 8-12 diverse options"). Handles 429/503 rate-limit detection and triggers instant fail-fast fallback. |

> **Data flow in Phase 3:**
> `api.py` calls `prompt_builder.py` → prompt string → `llm_client.py` sends to Gemini → parses JSON response → returns recommendation list. If anything fails → `generate_fallback_response()` kicks in.

---

### Static Frontend (`zomato_ai/static/`)

| File | Lines | What it does | Why it exists |
|------|-------|-------------|---------------|
| [`index.html`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/static/index.html) | 145 | A standalone HTML dashboard with form inputs and results panels | The original "glassmorphism" UI served directly from the FastAPI backend at `http://localhost:8000/`. |
| [`styles.css`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/static/styles.css) | 651 | CSS styling with dark theme, neon accents, blur filters, skeleton loaders | Makes the static UI look premium. |
| [`app.js`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/zomato_ai/static/app.js) | 297 | JavaScript controller for form submission, autocomplete, and card rendering | Handles all client-side logic: location search-as-you-type, cuisine dropdown population, fetch calls to `/api/recommend`, loading spinners, and error panels. |

> **Note:** This is the simpler, self-contained UI. The premium Next.js portal (below) is the primary frontend.

---

## `frontend/` — The Premium Next.js Portal

| File | Lines | What it does | Why it exists |
|------|-------|-------------|---------------|
| [`package.json`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/package.json) | — | Node.js dependency manifest | Declares Next.js 16, React 19, TypeScript as dependencies. `npm install` reads this. |
| [`next.config.ts`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/next.config.ts) | — | Next.js framework configuration | Controls build behavior, image domains, and server-side settings. |
| [`tsconfig.json`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/tsconfig.json) | — | TypeScript compiler configuration | Sets path aliases (`@/` → `src/`), strict mode, and JSX settings. |

### `frontend/src/context/`

| File | Lines | What it does | Why it exists |
|------|-------|-------------|---------------|
| [`AppContext.tsx`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/src/context/AppContext.tsx) | 79 | Global React state manager | Holds `preferences`, `recommendations`, `loading`, and `error` state. Shared across all pages so data persists when navigating between Discover → Results → Restaurant Detail. |

### `frontend/src/app/` — The Page Routes

| File | Lines | Route | What it does |
|------|-------|-------|-------------|
| [`layout.tsx`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/src/app/layout.tsx) | 50 | Wraps all pages | Global header with **Home** and **Discover** tabs, logo, search icon, profile avatar, and footer. Wraps children inside `AppProvider`. |
| [`page.tsx`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/src/app/page.tsx) | 201 | `/` (Home) | Landing page with "Top Picks for You" spotlight cards, "Trending Nearby" horizontal feed, and "Hidden Gems" banner section. |
| [`preferences/page.tsx`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/src/app/preferences/page.tsx) | 374 | `/preferences` (Discover) | **The search form.** Location autocomplete dropdown, budget inputs, star rating selector, cuisine pill toggles (with "More" expansion), vibe textarea, and the **"Find My Match"** button (disables to "Finding Matches..." during loading). |
| [`recommendations/page.tsx`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/src/app/recommendations/page.tsx) | 258 | `/recommendations` | **The results page.** Displays a featured card, sidebar picks, and a grid of remaining matches. Shows 10 initially; "Reveal More Matches" loads the next 10 inline on the same page. |
| [`restaurant/[name]/page.tsx`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/src/app/restaurant/%5Bname%5D/page.tsx) | 249 | `/restaurant/:name` | Individual restaurant detail view with cuisine badges, booking module, order counter, and map coordinates. |
| [`globals.css`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/frontend/src/app/globals.css) | 1,344 | — | Complete design system: color tokens, Outfit typography, card layouts, gradient effects, hover animations, and responsive breakpoints. |

---

## `tests/` — Automated Test Suite

| File | What it tests |
|------|--------------|
| [`test_cleansing.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_cleansing.py) | Rate parsing (`"4.1/5"` → `4.1`, `"NEW"` → `None`) and cost cleaning (`"1,200"` → `1200`). |
| [`test_phase1.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_phase1.py) | Data ingestion pipeline — schema creation, data type validation, index existence. |
| [`test_phase2.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_phase2.py) | API endpoint schemas, budget boundary validation, rating filter accuracy. |
| [`test_phase3.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_phase3.py) | LLM prompt construction, JSON response parsing, fallback template generation. |
| [`test_phase4.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_phase4.py) | FastAPI HTTP endpoint integration tests (locations, cuisines, recommend). |
| [`test_failsafe.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_failsafe.py) | Mocks LLM failures and verifies the fallback system kicks in correctly. |
| [`test_performance.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_performance.py) | Benchmarks database query speed (must be < 5ms). |
| [`test_repository.py`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/tests/test_repository.py) | Database connection and repository method validation. |

> **Run all 31 tests:** `.venv/bin/pytest` — completes in under 3 seconds.

---

## `Docs/` — Project Documentation

| File | What it contains |
|------|-----------------|
| [`Problem Statement.md`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/Docs/Problem%20Statement.md) | The original assignment brief and project requirements. |
| [`Architecture.md`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/Docs/Architecture.md) | The full technical blueprint — database schemas, SQL queries, scoring formulas, prompt templates, UI routing, and deployment specs. |
| [`Summary.md`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/Docs/Summary.md) | Executive summary explaining each phase at a business level. |
| [`Improvements.md`](file:///Users/himalaya/Documents/Claude/Output/Zomato%20Project/Docs/Improvements.md) | Running changelog of feature requests and iterative improvements. |

---

## How everything connects — the 30-second version

```
User clicks "Find My Match" on the Next.js portal (port 3000)
        │
        ▼
POST /api/recommend  →  FastAPI backend (port 8000)
        │
        ├─ 1. repository.py queries SQLite (< 5ms)
        ├─ 2. filtering.py scores candidates mathematically
        ├─ 3. IF BYPASS_LLM=true → return heuristic templates instantly
        │     ELSE → llm_client.py calls Gemini (timeout 2s)
        │              IF Gemini fails → fallback to heuristic templates
        │
        ▼
JSON response → Next.js renders recommendation cards
```

For Streamlit deployment, the same pipeline runs inside `streamlit_app.py` — no FastAPI needed, it queries the database and calls Gemini directly.

# Executive Summary: AI-Powered Restaurant Recommendation System

*A high-level business and product overview of the Zomato AI Concierge architecture.*

## The Big Picture
We are building a "Personal Foodie Concierge." Instead of forcing users to scroll through hundreds of restaurants and read reviews, they tell us what they want, and we give them a curated list with personalized explanations of *why* they should go there.

Here is how the product comes to life, phase by phase, with the corresponding API endpoints that power each step:

---

### Phase 1: The Data Foundation (Ingestion & Cleaning)
* **What it does:** We pull raw Zomato Bangalore data (over 51,000 restaurants) from Hugging Face and clean it. We use regular expressions to clean price strings (e.g. "1,200" to 1200) and implement a multi-tier median imputation system to fill in missing prices based on location and restaurant type.
* **Why you care:** Missing or dirty data breaks user trust. By using advanced deduplication and specific index optimizations in our SQLite database, we ensure every query is perfectly clean and blindingly fast.
* **Database Target:** `zomato_restaurants.db` (stores 12,485 unique, cleaned restaurants).

---

### Phase 2: The Fast Filter (Backend Engine & Heuristics)
* **What it does:** When a user asks for "Italian in Indiranagar under ₹1000," our FastAPI backend instantly maps "under ₹1000" to our predefined budget tiers. We then rank matches using a custom mathematical heuristic: **70% normalized rating + 30% log-scaled popularity (votes)**.
* **Why you care (Cost & Speed):** Asking an AI to read the entire database is expensive and slow. By pre-filtering and mathematically scoring the top 20 candidates, we guarantee database query times under 5 milliseconds and keep LLM token usage (and costs) to an absolute minimum.

#### APIs Developed in this Phase:
*   **Locations API (`GET /api/locations`)**
    *   *What it does:* Scans the database and returns a sorted list of unique neighborhoods (e.g. Indiranagar, Whitefield) with matching capitalized property keys (`Location`).
    *   *Why:* Populates the location dropdown in the UI. This ensures the filter inputs always match actual data records.
*   **Cuisines API (`GET /api/cuisines`)**
    *   *What it does:* Extracts, cleanses, and returns a unique, sorted list of all cuisines served across Bangalore.
    *   *Why:* Powers the autocomplete filters in the user interface.

---

### Phase 3: The "Magic" (AI / LLM Integration)
* **What it does:** We feed the top 20 pre-filtered restaurants into the Gemini 2.5 Flash model (with API credentials loaded securely via a central Pydantic `Settings` manager). Using strict temperature controls (0.2) and structured JSON prompt templates, the AI acts as a local expert to write custom, human-like explanations. If no preferred cuisine is selected, the prompt system instruction directs the LLM to output a broad, diverse selection of 8-12 high-quality restaurants.
* **Why you care:** This is the core value proposition—personalized narrative. To guarantee reliability, we engineered a **strict 2.0-second timeout, exponential backoff, and automatic heuristic failsafe**. If the AI times out or hits API limits (429/503), the system seamlessly falls back to a programmatic template, ensuring the user gets a recommendation instantly without seeing an error screen.
* **Low-Latency Bypass:** For near-instantaneous search speeds, setting `BYPASS_LLM=true` in `.env` instructs the backend route handler to completely bypass the Gemini API call and serve heuristic recommendations immediately in under **5ms**.

#### APIs Developed in this Phase:
*   **Recommendation API (`POST /api/recommend`)**
    *   *What it does:* The main entry point. Receives user preferences, queries database records, ranks candidates via heuristics, calls the Gemini 2.5 Flash API to get custom reasoning explanations, and returns structured JSON cards.
    *   *Why:* Delivers curated, community-validated selections with human-like rationale explaining how it fits the user's specific request.

---

### Phase 4: The Storefront (Premium User Interface & Portal)
* **What it does:** A sleek, responsive web interface built on Next.js 16 (App Router) using TypeScript, featuring a dark "glassmorphic" layout, skeleton loaders, and red neon accents.
* **Clean Navigation:** The top global navigation header is stripped of unused links, keeping exactly two tabs: **Home** and **Discover** (preferences).
* **Enhanced Search Experience:** When a search request is submitted, the submit button is immediately disabled and changes its text to **`Finding Matches...`** to indicate status. Results load immediately.
* **Same-Page Pagination:** The search results page loads the top 10 recommendations initially. Clicking **"Reveal More Matches"** increments the count and dynamically loads the next 10 matches on the same page inline, avoiding redirects.

#### APIs Developed in this Phase:
*   **Static Assets Mount (`GET /`)**
    *   *What it does:* Serves the single-page HTML (`index.html`), CSS styling variable guides (`styles.css`), and JavaScript controllers (`app.js`) directly from the backend.
    *   *Why:* Allows loading the entire static dashboard by visiting the root server address in the browser.

---

### Phase 5: Quality Assurance & Launch Readiness
* **What it does:** We enforce strict QA Performance Budgets:
    * **Database Queries:** < 5 milliseconds
    * **End-to-End API Response (Heuristic Mode):** < 5 milliseconds
    * **End-to-End API Response (Including active Gemini API):** < 2.0 seconds
    * **UI Bundle Size:** < 100 KB
* **Why you care:** Automated testing (via 31 pytest cases) ensures our rating algorithms and AI parsers never break in production. The rigid performance thresholds guarantee that the app scales smoothly and never keeps the user waiting.

---

### Phase 6: Dual Deployment Specification
* **Backend Deployment (Streamlit):**
  * The backend and its underlying database `zomato_restaurants.db` are package-configured to deploy on Streamlit Community Cloud using the `streamlit_app.py` script.
  * Environmental configurations (Gemini keys, bypass modes) are handled via Streamlit's secrets manager.
* **Frontend Deployment (Vercel):**
  * The Next.js Premium Portal is deployed on Vercel, integrating server-side pre-rendering and routing API calls directly to the Streamlit backend host address.

---

**Conclusion:** We designed a robust, failsafe architecture that marries the low cost and high speed of traditional databases with the personalized, magical experience of Generative AI, all wrapped in a visually stunning interface.

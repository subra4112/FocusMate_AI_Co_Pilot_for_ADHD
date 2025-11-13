# FocusMate Mail Assistant

FocusMate is an ADHD-friendly productivity assistant for Gmail. It classifies and summarizes messages, extracts action items, schedules events in Google Calendar, and offers natural-language search across your inbox. The system uses LangChain (Claude/OpenAI models), FastAPI, Streamlit, and SQLite.

## Project Layout & Key Files
- **Entry points**
  - `focusmate_app.py`: CLI triage tool.
  - `api/server.py`: FastAPI application exposing REST endpoints.
  - `streamlit_app.py`: Streamlit dashboard.
- **Core logic**
  - `services/email_processor.py`: Pulls Gmail data, categorizes emails, and writes summaries.
  - `services/email_search.py`: Natural-language inbox search agent.
  - `core/priority.py`: Priority scoring helpers used during triage.
- **Data & persistence**
  - `db/storage.py`: SQLite helpers for `focusmate.db`.
  - `focusmate.db`: Primary cache and long-term storage (auto-created).
- **Integrations**
  - `tools/gmail_client.py`, `tools/calendar_client.py`: Gmail and Calendar wrappers.
  - `chains/email_analysis.py`: LangChain logic for email understanding.
- **OAuth helpers**
  - `google_oauth_setup.py`, `google_oauth_calendar_setup.py`: Generate `token.json`.
- **Frontends**
  - `frontend/index.html`: Minimal HTML UI consuming the API.
  - `frontend-react/`: Vite + React prototype. Run separately if desired.
- **Config samples**
  - `env.sample`: Environment variable template.
  - `req.txt`: Python dependencies.

## Prerequisites
- Python 3.12 (matching the provided `my_env` virtual environment).
- Gmail OAuth credentials file `credentials.json` in the project root.
- OpenAI API key (required for analysis and search).
- Optional: Supermemory API key for extended context retention.

## Setup
```bash
# 1. Create or reuse the virtual environment
python -m venv my_env

# 2. Activate it (PowerShell)
.\my_env\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install --upgrade pip
pip install -r req.txt
```

### Environment Variables
Copy `env.sample` to `.env` and fill in the values:
```
OPENAI_API_KEY=sk-...
SUPERMEMORY_API_KEY=optional
```
Both FastAPI (`uvicorn`) and Streamlit automatically load `.env`.

### Gmail & Calendar OAuth
Generate a combined `token.json` (stored locally) by running:
```bash
python google_oauth_setup.py
python google_oauth_calendar_setup.py
```
Follow the browser prompts and ensure your Google Cloud project has Gmail and Calendar scopes enabled.

## How to Run
- **CLI triage (command-line only)**
  ```bash
  python focusmate_app.py --unread 7      # triage unread emails from the last 7 days
  python focusmate_app.py --backfill 14   # classify all mail from the past 14 days
  ```
  Outputs summaries, categories, and suggested actions in the terminal.

- **REST API (FastAPI + Uvicorn)**
  ```bash
  uvicorn api.server:app --reload --port 8000
  ```
  Key endpoints:
  - `GET /health` – service check.
  - `GET /emails?limit=3` – fetch cached summaries grouped by category.
  - `POST /emails/refresh` – ingest new Gmail data and rebuild cache.
  - `POST /emails/search` – ask free-form questions about your inbox.

- **Dashboard (Streamlit)**
  ```bash
  streamlit run streamlit_app.py
  ```
  Presents the triaged inbox, summaries, and AI search in a three-column layout.

- **React prototype (optional)**
  ```bash
  cd frontend-react
  npm install
  npm run dev
  ```
  Exposes a Vite dev server with a richer interface consuming the FastAPI endpoints.

## Data & Storage
- `focusmate.db` is the primary SQLite database for cached emails, tasks, and calendar syncs.
- `cache.db` remains for legacy compatibility but is no longer updated.

## Development Notes
- Core logic lives under `services/` and `tools/`; edits here affect both API and Streamlit outputs.
- Run manual smoke tests after changing AI chains or database schemas.
- The existing virtual environment `my_env/` contains pip executables for `uvicorn`, `streamlit`, and other utilities if you prefer not to install globally.

## Troubleshooting
- **Rate limits (429) from OpenAI**: pause briefly or lower batch sizes.
- **OAuth scope errors**: delete `token.json`, rerun the OAuth scripts with the correct Gmail/Calendar scopes.
- **Slow refresh**: decrease the fetch window (e.g., `--unread 3`) or temporarily disable calendar writes.

## License
MIT — adjust for your distribution needs.

# Clean Setup Instructions

## Pre-requirements
- Install and run **Docker Desktop** (Windows/macOS) or **Docker daemon** (Linux).
- Install **Python 3.8+** with `venv` support.
- Install **Node.js + npm** (LTS recommended).

---

## Steps Done by `run.sh`

1. **Starts Ollama**:
   - Runs Ollama on port `11434`.
   - Pulls the model `gemma3:1b`.

2. **Starts MongoDB**:
   - Builds MongoDB using `./external-services/Dockerfile`.
   - Runs MongoDB on port `27017`.

3. **Sets up Python environment**:
   - Creates a virtual environment `aditya_env` if not already present.
   - Activates it and installs `backend/requirements.txt`.

4. **Runs Backend**:
   - Launches FastAPI backend via `uvicorn app.main:app --reload` from `backend/`.

5. **Runs Frontend**:
   - Installs dependencies (`npm install`) and runs dev server (`npm run dev`) from `frontend/`.

---

## Usage

Make the script executable and run:

```bash
chmod +x run.sh
./run.sh

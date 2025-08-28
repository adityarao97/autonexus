#!/usr/bin/env bash
set -e

# ------------------------------
# 1. Run Ollama with gemma3:1b
# ------------------------------
echo ">>> Starting Ollama with model gemma3:1b ..."
ollama run gemma3:1b

# ------------------------------
# 2. Run MongoDB from external-services Dockerfile
# ------------------------------
echo ">>> Starting MongoDB from ./external-services/Dockerfile ..."
docker build -t my-mongo ./external-services
docker run -d --name mongodb -p 27017:27017 my-mongo

# ------------------------------
# 3. Setup Python virtualenv
# ------------------------------
echo ">>> Setting up Python virtual environment (aditya_env) ..."
if [ ! -d "aditya_env" ]; then
  python3 -m venv aditya_env
fi
# Activate it
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
  source aditya_env/Scripts/activate
else
  source aditya_env/bin/activate
fi
pip install --upgrade pip
pip install -r backend/requirements.txt

# ------------------------------
# 4. Run Python backend
# ------------------------------
echo ">>> Starting backend with uvicorn ..."
cd backend
uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ..

# ------------------------------
# 5. Run NPM frontend
# ------------------------------
echo ">>> Starting frontend ..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo ">>> All services started!"
echo "Frontend : http://localhost:3000"
echo "Backend  : http://localhost:8000"
echo "Ollama   : http://localhost:11434"
echo "MongoDB  : mongodb://localhost:27017"

# Keep script running until killed
wait $BACKEND_PID $FRONTEND_PID

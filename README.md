# AutoNexus – Multi-Agent Supply Chain Optimization Platform

**AutoNexus** is a multi-agent supply chain optimization platform that uses **Claude MCP agents**, **Python**, **Neo4j**, **MySQL**, and a modern **React** dashboard to intelligently generate, evaluate, and visualize end-to-end logistics plans.

This system supports optimization based on **cost**, **eco-impact**, and **stability**, enabling organizations to explore and compare multiple supply chain strategies with transparent, explainable reasoning.

---

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
```

## Tech Stack

### Backend
- Python 3.x  
- Claude MCP Agents  
- FastAPI or Flask  
- Neo4j  
- MySQL  

### Frontend
- React.js  
- Material UI  
- Chart.js / D3.js  

### Dev Tools
- Docker  
- Neo4j Browser  
- Postman / Thunder Client  

---

## 4. Installation

### Clone the repository
```bash
git clone https://github.com/adityarao97/autonexus.git
cd autonexus
```

## Core Components

### Multi-Agent Engine
Dedicated Claude MCP agents for:
- Route generation  
- Cost modeling  
- Emissions scoring  
- Stability/risk assessment  
- Plan synthesis  

### Graph Model (Neo4j)
Represents:
- Suppliers  
- Distribution hubs  
- Warehouses  
- Transport routes  
- Capacities, delays, reliability scores  

### Optimization Pipeline
1. User sets cost/eco/stability weights.  
2. Agents produce candidate plans.  
3. Backend scores and ranks them.  
4. UI visualizes the chosen plan and alternatives.  

### Interactive Dashboard
- Route visualization  
- Cost and emission breakdowns  
- Risk metrics  
- Decision-tree comparisons  

---

## Sample Workflow

1. User inputs or imports supply chain nodes and routes.  
2. Backend updates the Neo4j graph.  
3. Agents generate and evaluate multiple route strategies.  
4. Backend selects optimal plans based on user-defined priorities.  
5. UI displays results, reasoning, and trade-offs.  
6. User iterates and runs simulations.  

---

## Future Enhancements

- Reinforcement learning for autonomous supply chain optimization  
- Real-time disruption monitoring and rerouting  
- Integration with logistics APIs (UPS, FedEx, Maersk, etc.)  
- Multi-agent negotiation for procurement strategies  
- Predictive cost forecasting using ML models  

---

## License

This project currently has no license.  
Add MIT, Apache 2.0, or GPL depending on distribution needs.

---

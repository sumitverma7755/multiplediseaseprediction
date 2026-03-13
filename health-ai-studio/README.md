# Health AI Studio (Production-Ready Full-Stack Scaffold)

This directory contains a production-oriented architecture for a healthcare AI dashboard with:

- Frontend: React + Vite + TailwindCSS
- Backend: Node.js + Express
- ML API: FastAPI (Python)
- Charts: Recharts
- PDF Reports: PDFKit

## Architecture

```text
health-ai-studio/
  frontend/
    src/
      components/
      pages/
      charts/
      services/
      hooks/
      utils/
  backend/
    src/
      controllers/
      routes/
      services/
      middleware/
      utils/
    data/
  ml-api/
    app/
```

## Features Implemented

1. UI Improvements
- Sidebar + responsive dashboard layout
- Module cards with icons, hover animation, shadows, and "Start Screening"
- Top navigation bar with search, notifications, profile dropdown
- Mobile/tablet responsive layout

2. Charts & Analytics
- Risk gauge chart
- Confidence score bar chart
- Weekly prediction trend chart
- Feature importance chart

3. Prediction Result Page
- Risk percentage
- Risk category (Low/Moderate/High)
- Important feature explanations
- AI recommendations
- Download AI Health Report (PDF)

4. Patient Management
- Add patient profile
- Save predictions per patient
- View previous reports by patient

5. Report Generator
- Prediction PDF export
- History export to CSV/PDF

6. History Page
- Filters: disease type, date range, patient
- CSV/PDF export

7. AI Assistant
- Embedded chat widget: "Ask Health AI"
- Explains results and gives preventive guidance

## Setup

### 1) ML API (FastAPI)

```bash
cd ml-api
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2) Backend (Express)

```bash
cd backend
npm install
npm run dev
```

Optional `.env` for backend:

```bash
PORT=8080
ML_API_URL=http://localhost:8000
```

### 3) Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Optional `.env` for frontend:

```bash
VITE_API_URL=http://localhost:8080/api
```

## API Endpoints

- `GET /api/health`
- `GET /api/patients`
- `POST /api/patients`
- `GET /api/patients/:patientId/reports`
- `POST /api/predictions`
- `GET /api/predictions/trends/weekly`
- `GET /api/history`
- `GET /api/history/summary`
- `GET /api/reports/prediction/:predictionId`
- `GET /api/reports/history?format=csv|pdf`
- `POST /api/assistant/chat`

## Notes

- Persistence currently uses JSON files in `backend/data/` for easy local setup.
- Replace JSON file storage with PostgreSQL/Mongo for production deployment.
- Add auth (JWT/OAuth), audit logs, and encryption for PHI before real clinical deployment.

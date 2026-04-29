# Carbon Quest Web Stack

Carbon Quest is now structured as a full-stack web application:

- `frontend/` contains the Vite + React + TypeScript client intended for Vercel.
- `backend/` contains the FastAPI + WebSocket session server intended for Render.
- `main.py` remains in the repository as the original desktop build reference, but the active web app lives entirely in `frontend/` and `backend/`.

## Architecture

### Frontend

- React 18 + Vite + TypeScript
- HTML5 Canvas scene renderer via `GameBoard.tsx`
- Local mode runs entirely client-side using `src/game/gameLogic.ts`
- Online mode uses the same rules and receives authoritative state via WebSocket

### Backend

- FastAPI + WebSockets
- In-memory party/session storage only
- No database required
- Pure Python game logic in `backend/game_logic.py`

## Local Development

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Create a `.env` file inside `frontend/` if needed:

```env
VITE_BACKEND_URL=ws://localhost:8000
```

## Deployment

### Vercel

- Deploy the `frontend/` directory
- Set `VITE_BACKEND_URL=wss://your-app.onrender.com`

### Render

- Deploy the `backend/` directory with the included `render.yaml`
- Set `FRONTEND_URL=https://your-app.vercel.app`

## Routes

- `/` title screen
- `/local` local same-device game
- `/online` join/create menu
- `/party/:code` host waiting room
- `/game/:sessionId` online game session

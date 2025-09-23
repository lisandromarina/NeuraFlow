# NeuraFlow

NeuraFlow is a full-stack application with a **React frontend** and a **FastAPI backend**, using Docker for development.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

---

## Project Structure

```
NeuraFlow/
├── backend/        # FastAPI backend
├── frontend/       # React frontend
├── docker-compose.yml
└── README.md
```

---

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/lisandromarina/NeuraFlow.git
cd NeuraFlow
```

### 2. Build and start the containers

```bash
docker-compose up --build
```

This will:

- Build the frontend and backend images.
- Start the frontend on [http://localhost:3000](http://localhost:3000)
- Start the backend on [http://localhost:8000](http://localhost:8000)

---

## Development Notes

### Frontend (React)

- Source code is mounted to `/app` inside the container for hot reload.
- Environment variables are set via `VITE_API_URL` to point to the backend.
- Node modules are persisted inside the container.

### Backend (FastAPI)

- Source code in `backend/app` is mounted for live reload.
- FastAPI will be accessible on [http://localhost:8000](http://localhost:8000).

---

## Stopping the Project

```bash
docker-compose down
```

This stops the containers but keeps the images.

---

## Notes

- Make sure your backend Dockerfile exposes **port 8000** and frontend Dockerfile exposes **port 5173** (React default).
- Adjust `VITE_API_URL` if you run backend on a different URL or port.

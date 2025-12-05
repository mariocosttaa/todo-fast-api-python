# 🚀 MarTaks - Modern Todo Application

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)

A robust, full-stack Todo application built with a modern **FastAPI** backend and a sleek **React** frontend. Designed for performance, scalability, and developer experience.

<p align="center">
  <img src="todo-app-presentation.gif" alt="MarTaks Demo" width="800">
</p>

---

## 🏗 Architecture

### Backend (`/backend`)
Built with **FastAPI**, following a layered architecture (Controllers, Services, Repositories) for maintainability.
- **Framework**: FastAPI (High performance, easy to learn, fast to code, ready for production)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic v2
- **Testing**: Pytest

### Frontend (`/frontend`)
Built with **React** and **Vite** for a lightning-fast development experience.
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: TailwindCSS v4
- **Language**: TypeScript
- **HTTP Client**: Axios

---

## 🛠 Prerequisites

- **Docker** & **Docker Compose** (Recommended)
- **Node.js** 22+ (For local frontend dev)
- **Python** 3.11+ (For local backend dev)

---

## 🚀 Getting Started

### Option 1: Docker (Recommended)
The easiest way to run the entire stack.

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd todo-fastapi
   ```

2. **Start the application**
   ```bash
   docker compose up --build -d
   ```
   This will start:
   - Backend API at `http://localhost:8000`
   - Frontend App at `http://localhost:3000`
   - PostgreSQL Database

3. **Access the App**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
   - API Docs (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Option 2: Local Development

#### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations (ensure DB is running via Docker or locally):
   ```bash
   export POSTGRES_HOST=localhost
   alembic upgrade head
   ```
5. Start the server:
   ```bash
   python -m app.main
   ```

#### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```

---

## 📚 Documentation

### Backend Documentation
The backend follows a well-documented, Laravel-inspired architecture. **Comprehensive documentation** covering all aspects of the backend implementation can be found in the [`backend/docs`](./backend/docs) directory.

This documentation includes:

| Topic | Description | Link |
|-------|-------------|------|
| **Database Access** | How to use the DB helper, sessions, and transaction management. | [📖 Read Docs](./backend/docs/database-access.md) |
| **Authentication** | JWT implementation, user sessions, and security best practices. | [📖 Read Docs](./backend/docs/authentication.md) |
| **Migrations** | Managing database schema changes with Alembic. | [📖 Read Docs](./backend/docs/alembic.md) |
| **Testing** | How to write and run tests with Pytest, including fixtures and best practices. | [📖 Read Docs](./backend/docs/testing.md) |
| **Management** | CLI commands for common tasks like generating controllers and models. | [📖 Read Docs](./backend/docs/manage.md) |

> 💡 **Tip**: Start with the [Database Access](./backend/docs/database-access.md) and [Authentication](./backend/docs/authentication.md) docs to understand the core patterns used throughout the application.

---

## 🔧 Common Commands

### Backend (Docker)
```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "message"

# Open Python Shell
docker compose exec backend python

# Run Tests
docker compose exec backend pytest
```

### Backend (Local)
*Ensure you have activated your virtual environment (`source backend/venv/bin/activate`)*
```bash
# Run migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "message"

# Run App
python -m app.main
```

---

## 📂 Project Structure

```
todo-fastapi/
├── backend/                # FastAPI Application
│   ├── alembic/           # Migration scripts
│   ├── app/
│   │   ├── controllers/   # Request handlers
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routers/       # API Routes
│   │   ├── services/      # Business logic
│   │   └── ...
│   ├── docs/              # Detailed documentation
│   └── tests/             # Pytest tests
├── frontend/               # React Application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   └── ...
├── docker-compose.yml     # Docker services config
└── README.md              # This file
```

---

## ✨ Features

- **Full Authentication**: Sign up, Login, Logout with JWT.
- **Task Management**: Create, Read, Update, Delete (CRUD) tasks.
- **Filtering & Search**: Filter by status, priority, and search text.
- **Responsive Design**: Beautiful UI that works on desktop and mobile.
- **Dark/Light Mode**: (Coming soon)
- **Drag & Drop**: Reorder tasks easily.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

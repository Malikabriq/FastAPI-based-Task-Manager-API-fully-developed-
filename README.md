# FastAPI Task Manager 🚀

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

A **FastAPI-based Task Manager API** for creating, tracking, updating, and deleting tasks. Integrated with **PostgreSQL** via SQLAlchemy, featuring computed fields for `progress` and `verdict`.

---

## Features ✨

- CRUD operations for tasks
- Task details: title, description, priority, status, estimated hours, hours spent
- Computed fields: `progress`, `verdict`
- Input validation with **Pydantic**
- Modular folder structure for scalability
- PostgreSQL database integration

---

## Quick Start ⚡

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/fastapi-task-manager.git
cd fastapi-task-manager
2️⃣ Set up virtual environment
python -m venv venv
# Activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Configure environment variables
Create a .env file with your PostgreSQL credentials:
DATABASE_URL=postgresql://username:password@host:port/dbname
5️⃣ Run the app
uvicorn app.main:app --reload
API Endpoints 🔗
| Method | Endpoint    | Description         |
| ------ | ----------- | ------------------- |
| POST   | /tasks/     | Create a new task   |
| GET    | /tasks/     | Get all tasks       |
| PUT    | /tasks/{id} | Update a task by ID |
| DELETE | /tasks/{id} | Delete a task by ID |
Dependencies:
FastAPI

SQLAlchemy

psycopg2-binary

Pydantic

Uvicorn

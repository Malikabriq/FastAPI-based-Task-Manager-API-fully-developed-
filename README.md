# FastAPI Task Manager API Fully developed.

A fully developed **Task Manager API** built with **FastAPI**, including user roles, permissions, admin management, and secure password reset.

---

## 🚀 Features

* **Task Management**:

  * Create, update, delete, and list tasks
* **Admin User Management**:

  * Admins can perform **CRUD operations on users**
  * Assign **roles and permissions** to users and admin
* **User Roles & Permissions**:

  * Role-based access control (RBAC)
  * Certain endpoints accessible only to admin or specific roles
* **Forgot Password / Password Reset**:

  * Users can reset password using **PIN sent via email**
* User Authentication (JWT-based)
* Auto-generated Swagger UI documentation

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Malikabriq/FastAPI-based-Task-Manager-API-fully-developed-.git
cd FastAPI-based-Task-Manager-API-fully-developed-
```

### 2. Create & activate virtual environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the API

```bash
uvicorn main:app --reload
```

Open the API docs at:

```
http://127.0.0.1:8000/docs
```

---

## 📁 Project Structure (example)

```
my_task_manager/
│── app/
│   ├── main.py
│   ├── models.py
│   ├── routers/
│   │   ├── tasks.py
│   │   └── users.py   # admin CRUD, roles & permissions, forgot password
│   ├── schemas.py
│   └── database.py
│── requirements.txt
│── README.md
│── .gitignore
```

---

## 🔑 Admin & User Notes

### Admin CRUD & Roles

| Action      | Method | Endpoint           | Description                                 |
| ----------- | ------ | ------------------ | ------------------------------------------- |
| Create User | POST   | `/users/`          | Assign role & permissions on creation       |
| Read User   | GET    | `/users/{user_id}` | View user info and role                     |
| Update User | PUT    | `/users/{user_id}` | Update user details, roles, and permissions |
| Delete User | DELETE | `/users/{user_id}` | Remove user                                 |

> **Role-based access:** Only admin or specific roles can access protected endpoints.

### Forgot Password

| Action         | Method | Endpoint                 | Description              |
| -------------- | ------ | ------------------------ | ------------------------ |
| Request PIN    | POST   | `/users/forgot-password` | Sends PIN to user email  |
| Reset Password | POST   | `/users/reset-password`  | Reset password using PIN |

**Example using cURL:**

```bash
# Request PIN
curl -X POST "http://127.0.0.1:8000/users/forgot-password" -H "Content-Type: application/json" -d '{"email":"user@example.com"}'

# Reset Password
curl -X POST "http://127.0.0.1:8000/users/reset-password" -H "Content-Type: application/json" -d '{"email":"user@example.com","pin":"123456","new_password":"newpass123"}'
```

---

## ✔️ Features Already Implemented

* Task CRUD operations
* User CRUD by admin
* Role & permission assignment for users and admin
* Forgot password via email/PIN
* JWT authentication

---

## 📝 License

Open-source and free to use.

Open-source and free to use.

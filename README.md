# 🚀 Social Media Backend (FastAPI)

A full-stack social media application backend built with FastAPI, featuring authentication, image uploads, likes, and comments.

---

## 🔥 Features

- 🔐 User Authentication (JWT)
- 📸 Image Upload (ImageKit)
- 📰 Feed System
- ❤️ Like Posts
- 💬 Comment on Posts
- 🗑 Delete Posts
- ⚡ Async FastAPI Backend

---

## 🛠 Tech Stack

- FastAPI
- SQLAlchemy (Async)
- SQLite
- FastAPI Users (Auth)
- ImageKit (Media Storage)
- Streamlit (Frontend)

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
|-------|--------|------------|
| POST | /auth/register | Register |
| POST | /auth/jwt/login | Login |
| POST | /upload | Upload Post |
| GET | /feed | Get Feed |
| POST | /posts/{id}/like | Like |
| POST | /posts/{id}/comment | Comment |
| DELETE | /posts/{id} | Delete |

---

## ⚙️ Setup

```bash
pip install -r requirements.txt
uvicorn app.app:app --reload
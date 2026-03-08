# AI-Powered Software Engineering Education Platform

A full-stack application designed to assist learners in navigating software engineering concepts through an interactive knowledge graph and AI-driven Q&A. The project separates frontend and backend, leveraging modern web technologies and machine learning to provide a personalized study experience.

## 🚀 Features

- **Dynamic knowledge graph** constructed from GitHub, Stack Overflow, and Wikipedia.
- **AI-based question answering** with concept-aware constraints to produce relevant responses.
- **Interactive visualization** of learning paths using Neo4j and frontend graph libraries.
- **Concept recommendation engine** that adapts to user progress and reduces study time.
- **Backend/frontend separation** for scalable development and deployment.

## 🛠 Technology Stack

- **Backend:** Python, FastAPI, Neo4j, Docker
- **Frontend:** TypeScript, React, Vite, Tailwind CSS
- **AI/ML:** DeepSeek API, HuggingFace Transformers, PyTorch
- **Database:** Neo4j Knowledge Graph

## 📁 Repository Structure

```
/please_last_project
├─ backend/            # FastAPI server and data scrapers
├─ frontend/           # React application
├─ node_modules/       # removed from repo (see .gitignore)
├─ *.py                # miscellaneous scripts for data processing
└─ README.md           # this file
```

## ⚙️ Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/115581748/please_last_project.git
   cd please_last_project
   ```
2. Backend dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate   # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```
3. Frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```
4. Configure environment variables (.env) with Neo4j credentials and API keys.
5. Start backend server:
   ```bash
   cd ../backend
   uvicorn main:app --reload
   ```
6. Launch frontend development server:
   ```bash
   cd ../frontend
   npm run dev
   ```

## 📷 Screenshots

*Insert project screenshots here when available.*

## 📦 Deployment

- Backend and frontend can be containerized using Docker.
- Example Docker Compose setup is available in `/docker-compose.yml` (if added).

## 📄 License

This project is released under the MIT License.

---

_For best results, add detailed usage instructions, contributions guidelines, and real screenshots._

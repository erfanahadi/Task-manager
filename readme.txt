Task Management API
Features
•	User registration and authentication (Token-based)
•	Task creation, update, deletion
•	Task workflow: To Do → In Progress → Completed
•	Progress-based state transitions
•	Permission rules (creator vs assignee)
•	API documentation with Swagger (drf-spectacular)
•	Dockerized setup (no local Python or DB needed)
Tech Stack
•	Python / Django
•	Django REST Framework
•	PostgreSQL (via Docker)
•	Docker & Docker Compose
•	drf-spectacular (Swagger / OpenAPI)
Requirements
You only need:
•	Docker
•	Docker Compose

Getting Started
1. Clone the repository:
git clone <repository-url>
cd <project-root>
2. Build and run the project:
docker compose up –build
API Documentations:
http://127.0.0.1:8000/api/docs/swagger/

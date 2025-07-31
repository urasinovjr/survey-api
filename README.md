Survey API

FastAPI-based API for managing construction surveys with 200+ questions, validations, and PostgreSQL support.

Setup

Clone the repository:

git clone https://github.com/yourusername/survey-api.git
cd survey-api

Set up virtual environment:

python -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure .env: Create a .env file with:

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/survey_db

Replace your_password with your PostgreSQL password.

Set up PostgreSQL:

sudo pacman -S postgresql
sudo su - postgres
initdb -D /var/lib/postgres/data
exit
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo su - postgres
psql
CREATE DATABASE survey_db;
GRANT ALL PRIVILEGES ON DATABASE survey_db TO postgres;
\q
exit

Initialize migrations with Alembic:

alembic init migrations

Edit migrations/env.py to use DATABASE_URL from .env. Generate initial migration:

alembic revision --autogenerate -m "initial"
alembic upgrade head

Run the application:

uvicorn main:app --reload

API Endpoints

POST /api/versions: Create a new version.

Example: curl -X POST "http://localhost:8000/api/versions" -H "Content-Type: application/json" -d '{"name": "v2.0"}'

GET /api/versions: List all versions.

POST /api/questions: Add a question.

Example: curl -X POST "http://localhost:8000/api/questions" -H "Content-Type: application/json" -d '{"version_id": 1, "number": "1.1", "text": "Наименование", "type": "dropdown", "options": {"values": ["Жилой дом"]}}'

POST /api/responses: Submit a response.

Testing

Run tests:

pytest tests/
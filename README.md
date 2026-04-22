# Diaspora Assistant

AI-powered assistant helping Kenyans in the diaspora manage tasks back home.

## Tech Stack
- Backend: Django (Python)
- Database: SQLite
- AI: Groq API (LLaMA3)
- Frontend: HTML + CSS + Vanilla JavaScript

## Setup Instructions

1. Clone the repo
   git clone https://github.com/rogitoms/diaspora_assistant.git
   cd diaspora_assistant

2. Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate        # Mac/Linux
   venv\Scripts\activate           # Windows

3. Install dependencies
   pip install -r requirements.txt

4. Create your .env file
   cp .env
   # Open .env and add your GROQ_API_KEY and SECRET_KEY

5. Run migrations
   python manage.py makemigrations
   python manage.py migrate

6. Start the server
   python manage.py runserver

7. Open http://127.0.0.1:8000

## Decisions I made and why
*(to be filled in after all features are built)*
# Diaspora Assistant

An AI-powered assistant that helps Kenyans living abroad manage tasks back 
home.

---

## Tech Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | Django (Python) |
| Database | SQLite |
| AI       | Groq API|
| Frontend | HTML + CSS + Vanilla JavaScript |

---

## Features

- **AI Intent Extraction** — understands what the customer wants from plain English
- **Risk Scoring** — calculates a 0-100 risk score based on diaspora context
- **Task Creation** — generates a unique task code (DSP-XXXXXXXX) for every request
- **Step Generation** — produces 3-6 actionable steps specific to each intent
- **3-Format Messages** — WhatsApp, Email, and SMS confirmations generated per task
- **Employee Assignment** — routes tasks to Finance, Legal, Operations, or Logistics
- **Task Dashboard** — view all tasks, filter by status, update status in real time
- **Status History** — every status change is logged to the database

---

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/rogitoms/diaspora_assistant.git
cd diaspora_assistant
```

### 2. Create and activate virtual environment
```
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Create your .env file
```
cp .env
```
Open `.env` and add your real values:
```
GROQ_API_KEY=your_groq_api_key_here
DEBUG=True
```
Get a free Groq API key at https://console.groq.com/keys

### 5. Run migrations
```
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the server
```
python manage.py runserver
```

### 7. Open the app
```
http://127.0.0.1:8000
```

---

## SQL Dump

The `sql_dump/` folder contains:
- `schema.sql` — full database schema
- `sample_data.json` — 5 sample tasks with complete data including entities, 
   steps, all three messages, risk scores, and employee assignments
- `full_dump.sql` — complete SQLite dump with all records

---

## Project Structure

```
diaspora-assistant/
├── backend/                  ← Django config (settings, urls, wsgi)
├── tasks/                    ← Main app
│   ├── models.py             ← Task, Step, Message, StatusHistory
│   ├── views.py              ← API endpoints
│   ├── ai_engine.py          ← Groq integration and intent extraction
│   ├── risk_scorer.py        ← Risk scoring logic
│   └── urls.py               ← URL routing
├── frontend/
│   ├── templates/index.html  ← Single page frontend
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── sql_dump/                 ← Schema and sample data
├── .env
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/` | Frontend dashboard |
| POST | `/api/submit/` | Submit a new request |
| GET  | `/api/tasks/` | Get all tasks |
| PATCH | `/api/tasks/<task_code>/status/` | Update task status |

---

## Risk Scoring Logic

Risk scores are calculated on a 0-100 scale using factors specific to the 
Kenyan diaspora context:

| Factor | Points | Reasoning |
|--------|--------|-----------|
| Intent: send_money base | 30 | Financial transactions carry inherent risk |
| Intent: verify_document base | 25 | Document fraud is common in Kenya |
| Intent: hire_service base | 15 | Service hires are lower risk |
| Intent: airport_transfer base | 10 | Logistics tasks are lowest risk |
| Amount over KES 100,000 | +25 | Very large transfers need extra scrutiny |
| Amount KES 50,000–100,000 | +15 | Significant transfer amount |
| Amount KES 10,000–50,000 | +8 | Moderate transfer amount |
| High urgency | +20 | Urgent + large amount is a classic fraud pattern |
| Medium urgency | +10 | Moderate urgency adds some risk |
| Land title document | +20 | Land fraud is extremely common in Kenya |
| ID or passport document | +10 | Identity documents carry moderate risk |
| Unknown recipient | +15 | Cannot verify where money is going |
| No location provided | +5 | Missing location makes verification harder |

**Labels:** 0–39 = Low · 40–69 = Medium · 70–100 = High

---

## Decisions I Made and Why

### AI Tools Used
- **Groq API** — chosen for its fast inference on open source models and 
  generous free tier
- **Model: llama-3.3-70b-versatile** —  chosen because it produces highly consistent 
  structured JSON output and follows complex system prompt instructions reliably.

### How I Designed the System Prompt
- Specified the exact JSON structure the model must return including field names, 
  types, and allowed values
- Constrained urgency to exactly `low | medium | high` to prevent free-form text
- Added intent-specific step guidance so steps are always relevant to the task type
- Set temperature to 0.2 for consistent structured output — higher temperature 
  produced more creative but less parseable responses
- Excluded any preamble or explanation because it broke JSON parsing
- Added `[TASK_CODE]` as a placeholder in messages so the real code could be 
  injected after the task was saved to the database


### One Thing That Did Not Work as Expected
- The Groq model returned raw newline characters (`\n`) inside JSON string values 
  which caused `json.loads()` to throw a JSONDecodeError with "Invalid control 
  character". The JSON looked correct visually but was technically malformed. 
  I fixed this by running `re.sub(r'(?<!\\)\n', ' ', raw)` before parsing, 
  which strips the raw newlines while preserving intentional escaped ones. 

### Why SQLite
- It requires zero configuration, the database is a single file that is easy to 
  inspect and commit, and Django's ORM abstracts the differences so switching to 
  PostgreSQL later would require changing only one setting.

### Why Django over Flask
- Django provides the admin panel out of the box which made it easy to inspect the database during 
  development without writing extra code.
```

---


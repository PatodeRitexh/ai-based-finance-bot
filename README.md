# Personal Finance Advisor Bot

A self-hosted personal finance tracking and budgeting web application built with Python 3.11+, Flask, SQLite, and vanilla modern frontend standards. Designed specifically for Indian Rupee (INR, ₹) accounting, the system provides ledger logging, category budget caps, savings targets, and financial analysis powered by Google Gemini.

---

## 1. Project Overview

Personal Finance Advisor Bot is an engineering-focused personal finance manager. It operates with a local SQLite database, enforcing strict session-based tenant isolation. All calculations (cash flow, savings rates, budget variances) run server-side to guarantee arithmetic accuracy.

### Core Objectives
* Multi-source income logging (Salary, Freelance, Dividends, Business)
* Categorized daily and weekly expense tracking across 9 standard areas
* Category-level monthly budget constraints with threshold warnings
* Visual progress monitoring for savings targets
* On-demand Gemini AI spending analysis and recommendations
* Deterministic local fallback if AI services are unavailable or rate limited

---

## 2. Features

* **Financial Ledger**: Add, edit, filter, and delete income and expense entries.
* **Indian Rupee Formatting**: Consistent INR (₹) representation adhering to the Indian numbering system (e.g. ₹1,50,000.00).
* **Budget Variance Tracking**: Category limits compared against actual spend, with automated warnings for allocations nearing (80%) or exceeding (100%) defined limits.
* **Savings Milestones**: Target-date milestone tracker with deposit contribution shortcuts.
* **Interactive Visualizations**: Expense distributions via Chart.js doughnut graphs and a 6-month comparative cash-flow trend chart.
* **Gemini AI Integration**: Analysis using Google Gemini SDK (`google-genai`), providing structured spending insights, overspending identification, and actionable reductions.
* **Security & Isolation**: Passwords hashed with PBKDF2/SHA-256 via Werkzeug. User queries strictly isolated via foreign keys.
* **Compliance & Legal Pages**: Dedicated Privacy Policy (`/privacy`) and Terms & Conditions (`/terms`) detailing local data storage and advisory boundaries.

---

## 3. Technology Stack

* **Backend**: Python 3.11+, Flask, Flask-SQLAlchemy, SQLite, Flask-CORS, Werkzeug
* **AI Engine**: Google Gemini API via official `google-genai` SDK
* **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+), Chart.js
* **Configuration**: `python-dotenv` reading from `.env`
* **Development Target**: Compatible with VS Code, Git, GitHub, Windows PowerShell, and Unix shells

---

## 4. Project Structure

```
personal-finance/
│
├── app.py                      # Flask application factory and server entrypoint
├── config.py                   # Environment loading and database settings
├── requirements.txt            # Python dependencies
├── seed.py                     # Demo data population script
├── README.md                   # Technical documentation
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusion rules (secrets, venv, sqlite)
│
├── models/                     # SQLAlchemy data models
│   ├── __init__.py             # Database instance and model exports
│   ├── user.py                 # User authentication and relationships
│   ├── income.py               # Income stream records
│   ├── expense.py              # Expense tracking with categories
│   ├── budget.py               # Monthly category limits
│   └── savings_goal.py         # Financial goals and progress
│
├── routes/                     # Blueprint controllers
│   ├── __init__.py             # Auth decorator and route helpers
│   ├── pages.py                # Landing, login, dashboard, legal routes
│   ├── auth.py                 # REST endpoints for register, login, logout
│   ├── dashboard.py            # Aggregated dashboard metrics endpoint
│   ├── income.py               # Income CRUD API
│   ├── expenses.py             # Expense CRUD API
│   ├── budgets.py              # Budget limits and comparisons API
│   ├── goals.py                # Savings goals and contributions API
│   └── ai.py                   # Gemini AI analysis endpoint
│
├── services/                   # Business logic and external integrations
│   ├── __init__.py             # Service exports
│   ├── finance_service.py      # Server-side cash-flow and trend calculations
│   └── gemini_service.py       # Gemini API client, retries, and fallback engine
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Shell layout, favicon, global assets
│   ├── index.html              # Clean landing page
│   ├── login.html              # Account sign in with demo credentials filler
│   ├── register.html           # Account registration
│   ├── dashboard.html          # Full tabbed financial management interface
│   ├── privacy.html            # Privacy Policy
│   └── terms.html              # Terms & Conditions
│
├── static/                     # Static assets
│   ├── favicon.svg             # Monogram Rupee SVG icon
│   ├── css/
│   │   └── style.css           # Fintech design system
│   └── js/
│       ├── app.js              # Global state, INR formatter, modals, tabs
│       ├── dashboard.js        # Metric cards and Chart.js integrations
│       ├── income.js           # Income CRUD handlers
│       ├── expenses.js         # Expense CRUD and filtering handlers
│       ├── budgets.js          # Budget limit setter and warnings
│       ├── goals.js            # Savings goal cards and deposit modal
│       └── ai-advisor.js       # Gemini analysis invocation and rendering
│
└── instance/
    └── finance.db              # Local SQLite database (auto-created)
```

---

## 5. Installation and Setup

### Prerequisites
* Python 3.11 or higher
* Git

### Clone or Open Project in VS Code
Open the project folder directly in VS Code:
```bash
cd D:\Study\personal-finance
code .
```

### 1. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Environment Configuration

Copy the example configuration to `.env`:

**Windows:**
```powershell
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

### Configure `.env` Variables:
```ini
# Flask Server Configuration
SECRET_KEY=generate_a_secure_random_string_for_production
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000

# Google Gemini API Key
# Generate a key at https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

*Note: The application includes a pre-configured `.env` with your active key. Keep `.env` strictly gitignored.*

---

## 7. Database Initialization and Demo Seeding

### Initialize Database
The database tables are automatically verified and created when the Flask app starts.

### Seed Realistic Indian Financial Demo Data
To immediately test the application with pre-populated Indian salary, expenses, category budgets, and savings goals:
```bash
python seed.py
```

**Demo Account Credentials:**
* **Email**: `demo@financebot.local`
* **Password**: `DemoPass123!`

---

## 8. Running The Application Locally

Run the development server:
```bash
python app.py
```

Open your browser and navigate to:
`http://127.0.0.1:5000`

---

## 9. Verification & Testing

Verify system components directly from the command line:

1. **Verify Database and Ledger Metrics:**
   ```bash
   python -c "from app import create_app; from services.finance_service import FinanceService; app = create_app(); print('Summary:', FinanceService.get_user_dashboard_summary(1))"
   ```

2. **Verify Gemini AI Service:**
   ```bash
   python -c "from app import create_app; from services.finance_service import FinanceService; from services.gemini_service import GeminiService; app = create_app(); s = FinanceService.get_user_dashboard_summary(1); print(GeminiService.analyze_finances(s))"
   ```

---

## 10. Git Repository Setup & Pushing to GitHub

To publish this project to your GitHub account:

```bash
# Initialize git repository
git init

# Stage all project files (secrets and database are excluded by .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: Personal Finance Advisor Bot"

# Set main branch
git branch -M main

# Link to your remote GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git

# Push to GitHub
git push -u origin main
```

---

## 11. Security Notes

1. **API Keys**: `GEMINI_API_KEY` is loaded exclusively from environment variables via `os.environ`. It is never stored in source code, client-side JavaScript, or Git commits.
2. **Password Storage**: Passwords are saved as cryptographically salted hashes. Plaintext passwords are never stored.
3. **Session Authentication**: Flask secure HTTP-only cookies prevent cross-site scripting (XSS) credential theft.
4. **Data Privacy**: All database queries filter strictly by `session['user_id']`. Users cannot read or modify another user's financial records.
5. **Advisory Disclaimer**: The application explicitly includes disclaimers confirming that generated data is for educational tracking and does not constitute certified investment advice. No automated financial trading is supported.

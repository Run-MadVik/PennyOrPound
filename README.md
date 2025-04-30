# PennyOrPound - Personal Expense Tracker

PennyOrPound is a robust expense tracking application that helps users manage their personal finances effectively. Users can sign up and track their daily expenses, view monthly summaries, categorize spending, add historical expenses, and gain valuable insights into their spending patterns.

## Features

- User authentication and secure signup/login
- Daily expense tracking
- Monthly expense summaries
- Expense categorization
- Historical expense entry
- Spending insights and analytics
- RESTful API built with FastAPI
- MongoDB database integration

## Prerequisites

- Python 3.11 or higher
- MongoDB instance (local or cloud)
- Git

## Project Setup

### 1. Clone the Repository

```bash
git clone git@github.com:Run-MadVik/PennyOrPound.git
cd PennyOrPound
```

### 2. Create Python Virtual Environment

Windows:
```cmd
python3 -m venv env
.\env\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

Windows/macOS/Linux:
```bash
pip install --no-cache-dir -r requirements.txt
```

### 4. Configure Git Hooks

Windows/macOS/Linux:
```bash
python configure_hooks.py
```

### 5. Environment Configuration

Windows:
```cmd
copy .env.example .env
```

macOS/Linux:
```bash
cp .env.example .env
```


### 6. Run Tests

Windows/macOS/Linux:
```bash
pytest -v
```

### 7. Start the Server

Windows/macOS/Linux:
```bash
uvicorn pennyorpound.app:app --reload
```

The API will be available at `http://localhost:8000`

API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

- The project uses pre-commit hooks for code formatting (black), import sorting (isort), and linting (pylint)
- All tests must pass before committing changes
- Make sure to update tests when adding new features
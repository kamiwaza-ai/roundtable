# Corporate Strategy Simulator - Backend

## Setup
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy .env.example to .env and configure:
```bash
cp .env.example .env
```

4. Initialize database:
```bash
alembic upgrade head
```

5. Run development server:
```bash
uvicorn app.main:app --reload
```

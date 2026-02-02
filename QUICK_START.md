# 🚀 Quick Start Guide - 5 Minutes Setup

## Prerequisites
- Python 3.10+
- Node.js 16+
- Redis (install: `sudo apt-get install redis-server` or `brew install redis`)

## Backend Setup (2 minutes)

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Start Django (Terminal 1)
python manage.py runserver
```

## Start Workers (2 minutes)

```bash
# Terminal 2: Start Redis
redis-server

# Terminal 3: Start Celery
cd backend
source venv/bin/activate
celery -A config worker -l info
```

## Frontend Setup (1 minute)

```bash
# Terminal 4: Start frontend
cd frontend
npm install
npm run serve
```

## Access Application

🌐 **Frontend**: http://localhost:8080
🔧 **Admin Panel**: http://localhost:8000/admin
📡 **API**: http://localhost:8000/api/reports/

## Test It!

1. Open http://localhost:8080
2. Upload the sample PDF from `/backend/sample_pdf/`
3. Wait for processing (10-30 seconds)
4. Download the generated Word document

---

## Troubleshooting

**Port already in use?**
```bash
# Backend: Use different port
python manage.py runserver 8001

# Frontend: Edit package.json, change port in serve script
```

**Redis connection error?**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

**Module not found?**
```bash
# Ensure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

**CORS errors?**
- Backend must run on port 8000
- Frontend must run on port 8080
- Check `backend/config/settings.py` CORS_ALLOWED_ORIGINS

---

## What's Next?

✅ Read `SETUP_GUIDE.md` for detailed explanations
✅ Customize `reports/services/pdf_extractor.py` for your PDFs
✅ Modify Word templates in `reports/services/word_generator.py`
✅ Add more features to `frontend/src/components/ReportExtractor.vue`

**Need help?** Check the detailed `SETUP_GUIDE.md`

# 📊 Surveillance Report Extractor

A complete Django + Vue.js application for extracting KPI data from surveillance monitoring PDFs and generating formatted Word documents.

## ✨ Features

- 📄 **PDF Upload** - Upload surveillance reports from Mention, Brand24, Talkwalker, Brandwatch
- 🔍 **Intelligent Extraction** - Automatically extract mentions, reach, sentiment, emotions, sources, topics, hashtags, influencers
- 📊 **Word Generation** - Create professionally formatted Word documents with tables
- ⚡ **Async Processing** - Background processing with Celery for large files
- 🎨 **Modern UI** - Vue.js + Vuetify interface with real-time status updates
- 💾 **Full History** - Store all extracted data in PostgreSQL with complete history

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+
- Node.js 16+
- Redis

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # Terminal 1
```

### Workers
```bash
# Terminal 2
redis-server

# Terminal 3
cd backend && source venv/bin/activate
celery -A config worker -l info
```

### Frontend
```bash
# Terminal 4
cd frontend
npm install
npm run serve
```

### Access
- 🌐 Frontend: http://localhost:8080
- 🔧 Admin: http://localhost:8000/admin
- 📡 API: http://localhost:8000/api/reports/

## 📖 Documentation

- **QUICK_START.md** - 5-minute setup guide (start here!)
- **SETUP_GUIDE.md** - Detailed step-by-step instructions
- **PROJECT_STRUCTURE.md** - Complete project structure explanation
- **README.md** - This file

## 🗂️ Project Structure

```
surveillance-report-extractor/
├── backend/                 # Django REST API
│   ├── config/             # Project settings
│   ├── reports/            # Main app
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API endpoints
│   │   ├── tasks.py        # Celery async tasks
│   │   └── services/       # Business logic
│   │       ├── pdf_extractor.py    # PDF → Data
│   │       └── word_generator.py   # Data → Word
│   ├── media/              # Uploaded/generated files
│   └── requirements.txt
│
├── frontend/               # Vue.js Web Interface
│   ├── src/
│   │   ├── components/
│   │   │   └── ReportExtractor.vue  # Main component
│   │   ├── plugins/
│   │   ├── router/
│   │   └── store/
│   └── package.json
│
└── sample_report.pdf      # Test with this!
```

## 🎯 What It Does

### 1. Upload PDF
Upload surveillance reports from monitoring platforms

### 2. Extract KPIs
Automatically extracts:
- Volume (mentions count, % change)
- Reach (impressions, % change)
- Sentiment (positive, negative, neutral)
- Emotions (joy, anger, sadness, etc.)
- Sources (Facebook, Instagram, Twitter, etc.)
- Languages (French, English, etc.)
- Topics (top discussed subjects)
- Hashtags (trending tags)
- Influencers (top accounts by engagement)

### 3. Generate Word Document
Creates professionally formatted Word document with:
- Executive summary table
- Sentiment distribution table
- Emotion analysis table
- Sources breakdown
- Language distribution
- Top topics (ranked)
- Popular hashtags
- Key influencers

### 4. Download & Archive
- Download generated Word documents
- Download original PDFs
- View complete history
- Search and filter reports

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/` | Upload PDF report |
| GET | `/api/reports/` | List all reports |
| GET | `/api/reports/{id}/` | Get report details |
| GET | `/api/reports/{id}/download-docx/` | Download Word doc |
| GET | `/api/reports/{id}/download-pdf/` | Download original PDF |
| POST | `/api/reports/{id}/reprocess/` | Retry failed processing |
| DELETE | `/api/reports/{id}/` | Delete report |

## 🧪 Testing

Test the application with the included `sample_report.pdf`:

1. Start all services (backend, celery, redis, frontend)
2. Open http://localhost:8080
3. Upload `sample_report.pdf` with title "Test Report"
4. Wait for processing (10-30 seconds)
5. Download the generated Word document

Expected results:
- 257 mentions (-92.74% change)
- Sentiment: 147 positive, 75 negative, 35 neutral
- Top hashtags: #paulbiya, #biya2025, #cameroon
- Multiple formatted tables in Word document

## 🛠️ Customization

### Extract Different KPIs
Edit `backend/reports/services/pdf_extractor.py`:
```python
def _extract_custom_metric(self, text: str) -> Dict[str, Any]:
    pattern = r'YourPattern\s+(\d+)'
    match = re.search(pattern, text)
    if match:
        return {'value': int(match.group(1))}
    return {}
```

### Modify Word Templates
Edit `backend/reports/services/word_generator.py`:
```python
def _add_custom_section(self, data: Dict[str, Any]):
    self._add_section_heading("CUSTOM SECTION")
    # Add your tables/content
```

### Customize UI
Edit `frontend/src/components/ReportExtractor.vue`:
```vue
<template>
  <!-- Modify layout here -->
</template>

<script>
export default {
  methods: {
    // Add new methods
  }
}
</script>
```

## 📊 Tech Stack

### Backend
- Django 5.0 + Django REST Framework
- Celery + Redis (async processing)
- pdfplumber + PyPDF2 (PDF extraction)
- python-docx (Word generation)
- PostgreSQL (production database)

### Frontend
- Vue.js 2.7 + Vuetify 2.7
- Axios (HTTP client)
- Vue Router + Vuex

## 🚨 Troubleshooting

### Port already in use
```bash
# Backend: different port
python manage.py runserver 8001

# Frontend: edit package.json
"serve": "vue-cli-service serve --port 8081"
```

### Redis connection error
```bash
# Check Redis
redis-cli ping  # Should return: PONG

# Install Redis if missing
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS
```

### Module not found
```bash
# Ensure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

### CORS errors
- Ensure backend runs on port 8000
- Ensure frontend runs on port 8080
- Check `backend/config/settings.py` CORS settings

### PDF extraction fails
```bash
# Install system dependencies
sudo apt-get install tesseract-ocr poppler-utils  # Ubuntu
brew install tesseract poppler                     # macOS
```

## 🔐 Security Notes

**For Development:**
- Default settings use DEBUG=True
- CORS is open to localhost:8080
- SECRET_KEY is in .env file

**For Production:**
- Set DEBUG=False
- Update SECRET_KEY
- Configure CORS_ALLOWED_ORIGINS properly
- Use HTTPS
- Set up proper authentication
- Use PostgreSQL instead of SQLite
- Configure Gunicorn + Nginx

## 📦 Deployment

### Backend (Django + Celery)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Celery worker
celery -A config worker --loglevel=info
```

### Frontend (Vue.js)
```bash
# Build for production
npm run build

# Serve dist/ folder with Nginx
```

### Docker (Optional)
```bash
docker-compose up -d
```

## 🤝 Integration

This module integrates with your larger surveillance system:

1. **Data Integration Module** → Feeds PDFs to this module
2. **NLP Analysis Module** → Enhances sentiment/emotion analysis
3. **Dashboard Module** → Displays processing status
4. **Alert Module** → Triggers on completed reports
5. **Archive Module** → Stores historical reports

## 📝 License

Proprietary - ANTIC (Agence Nationale des Technologies de l'Information et de la Communication)

## 📞 Support

For issues or questions:
1. Check SETUP_GUIDE.md for detailed instructions
2. Check PROJECT_STRUCTURE.md for architecture details
3. Check API documentation in code comments
4. Contact ANTIC development team

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready ✅

Made with ❤️ for ANTIC

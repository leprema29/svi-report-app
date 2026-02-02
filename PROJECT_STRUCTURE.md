# 📁 Project Structure Explained

## Overview
```
surveillance-report-extractor/
├── backend/          ← Django REST API
├── frontend/         ← Vue.js Web Interface  
├── QUICK_START.md    ← Start here!
├── SETUP_GUIDE.md    ← Detailed guide
└── README.md         ← Full documentation
```

---

## 🔧 Backend Structure

```
backend/
│
├── config/                      # Django project configuration
│   ├── __init__.py             # Celery initialization
│   ├── settings.py             # Main settings (DB, apps, middleware)
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # WSGI config for deployment
│   └── celery.py               # Celery task queue config
│
├── reports/                     # Main application
│   │
│   ├── models.py               # DATABASE MODELS
│   │   └── SurveillanceReport  # Stores: PDF, DOCX, KPIs, status
│   │
│   ├── serializers.py          # JSON API SERIALIZERS
│   │   ├── SurveillanceReportSerializer
│   │   ├── SurveillanceReportCreateSerializer
│   │   └── SurveillanceReportListSerializer
│   │
│   ├── views.py                # API ENDPOINTS
│   │   └── SurveillanceReportViewSet
│   │       ├── POST   /api/reports/           Upload PDF
│   │       ├── GET    /api/reports/           List all
│   │       ├── GET    /api/reports/{id}/      Get details
│   │       ├── GET    /api/reports/{id}/download-docx/
│   │       ├── POST   /api/reports/{id}/reprocess/
│   │       └── DELETE /api/reports/{id}/      Delete
│   │
│   ├── tasks.py                # ASYNC TASKS (Celery)
│   │   └── process_surveillance_report()
│   │       1. Extract KPIs from PDF
│   │       2. Generate Word document
│   │       3. Update database
│   │
│   ├── urls.py                 # App URL routing
│   │
│   ├── admin.py                # Django admin configuration
│   │
│   └── services/               # BUSINESS LOGIC (Core!)
│       │
│       ├── pdf_extractor.py    # PDF → Data
│       │   └── PDFKPIExtractor
│       │       ├── _extract_title()
│       │       ├── _extract_period()
│       │       ├── _extract_volume_data()
│       │       ├── _extract_reach_data()
│       │       ├── _extract_sentiment_data()
│       │       ├── _extract_emotion_data()
│       │       ├── _extract_sources_data()
│       │       ├── _extract_languages_data()
│       │       ├── _extract_topics()
│       │       ├── _extract_hashtags()
│       │       └── _extract_influencers()
│       │
│       └── word_generator.py   # Data → Word Document
│           └── WordReportGenerator
│               ├── _add_summary_table()
│               ├── _add_sentiment_table()
│               ├── _add_emotion_table()
│               ├── _add_sources_table()
│               ├── _add_topics_table()
│               ├── _add_hashtags_table()
│               └── _add_influencers_table()
│
├── media/                      # Uploaded/Generated files
│   └── reports/
│       ├── pdf/               # Original PDFs
│       └── docx/              # Generated Word docs
│
├── manage.py                   # Django CLI
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

---

## 🎨 Frontend Structure

```
frontend/
│
├── public/
│   ├── index.html             # HTML template
│   └── favicon.ico            # App icon
│
├── src/
│   │
│   ├── components/            # Vue Components
│   │   └── ReportExtractor.vue   # MAIN COMPONENT
│   │       │
│   │       ├── Upload Section
│   │       │   ├── Title input
│   │       │   ├── PDF file picker
│   │       │   └── Upload button
│   │       │
│   │       ├── Reports Table
│   │       │   ├── Title, Status, Period, KPIs
│   │       │   ├── Search & filter
│   │       │   └── Action buttons
│   │       │
│   │       ├── Details Dialog
│   │       │   ├── Period display
│   │       │   ├── KPI cards
│   │       │   ├── Sentiment chips
│   │       │   └── Topics/hashtags
│   │       │
│   │       └── Methods
│   │           ├── uploadReport()
│   │           ├── loadReports()
│   │           ├── viewDetails()
│   │           ├── downloadDocx()
│   │           ├── downloadPdf()
│   │           └── deleteReport()
│   │
│   ├── plugins/
│   │   ├── vuetify.js         # UI framework config
│   │   └── axios.js           # HTTP client config
│   │
│   ├── router/
│   │   └── index.js           # URL routing
│   │
│   ├── store/
│   │   └── index.js           # State management (Vuex)
│   │
│   ├── App.vue                # Root component
│   │   ├── App bar (header)
│   │   └── Main content area
│   │
│   └── main.js                # Entry point
│       ├── Vue instance
│       ├── Router
│       ├── Store
│       └── Vuetify
│
├── package.json               # Node dependencies
├── vue.config.js              # Vue CLI config
├── babel.config.js            # JS transpiler config
└── .env.local                 # Frontend environment vars
```

---

## 🔄 Data Flow

### Upload & Processing Flow
```
1. USER (Browser)
   │
   ├─→ Upload PDF via Vue.js form
   │
2. FRONTEND (ReportExtractor.vue)
   │
   ├─→ POST /api/reports/ (FormData)
   │
3. BACKEND (views.py)
   │
   ├─→ Save PDF to media/reports/pdf/
   ├─→ Create SurveillanceReport record (status: pending)
   ├─→ Trigger Celery task: process_surveillance_report.delay()
   │
4. CELERY WORKER (tasks.py)
   │
   ├─→ Update status to 'processing'
   │
   ├─→ CALL: pdf_extractor.py
   │   └─→ Extract all KPIs using regex patterns
   │
   ├─→ CALL: word_generator.py
   │   └─→ Generate formatted Word document
   │
   ├─→ Save generated DOCX to media/reports/docx/
   ├─→ Update database with extracted data
   └─→ Update status to 'completed'
   │
5. FRONTEND (Auto-refresh every 10s)
   │
   ├─→ GET /api/reports/
   └─→ Display updated status to user
   │
6. USER
   │
   └─→ Click download → GET /api/reports/{id}/download-docx/
```

---

## 📊 Database Schema

```
SurveillanceReport Model
├── id (PK)
├── title (string)
├── status (pending|processing|completed|failed)
├── original_pdf (file)
├── generated_docx (file)
│
├── Extracted KPIs:
│   ├── period_start (date)
│   ├── period_end (date)
│   ├── total_mentions (int)
│   ├── mentions_change_percent (decimal)
│   ├── total_reach (bigint)
│   ├── reach_change_percent (decimal)
│   ├── sentiment_data (JSON)
│   ├── emotion_data (JSON)
│   ├── sources_data (JSON)
│   ├── languages_data (JSON)
│   ├── topics_data (JSON array)
│   ├── hashtags_data (JSON array)
│   └── influencers_data (JSON array)
│
├── created_by (FK → User)
├── created_at (datetime)
└── updated_at (datetime)
```

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/reports/` | List all reports | - | Array of reports |
| POST | `/api/reports/` | Upload PDF | FormData (title, pdf) | Report object |
| GET | `/api/reports/{id}/` | Get details | - | Full report data |
| GET | `/api/reports/{id}/download-docx/` | Download Word | - | File download |
| GET | `/api/reports/{id}/download-pdf/` | Download PDF | - | File download |
| POST | `/api/reports/{id}/reprocess/` | Retry failed | - | Status message |
| DELETE | `/api/reports/{id}/` | Delete report | - | 204 No Content |

---

## 🛠️ Key Technologies

### Backend Stack
- **Django 5.0** - Web framework
- **Django REST Framework** - API framework
- **Celery** - Async task queue
- **Redis** - Message broker
- **pdfplumber** - PDF text extraction
- **python-docx** - Word document generation
- **PostgreSQL** - Production database (optional)

### Frontend Stack
- **Vue.js 2.7** - JavaScript framework
- **Vuetify 2.7** - Material Design UI
- **Axios** - HTTP client
- **Vue Router** - Routing
- **Vuex** - State management

---

## 📝 File Naming Conventions

### Backend (Python)
- **Models**: `singular_noun` → `SurveillanceReport`
- **Views**: `PascalCase` + `ViewSet` → `SurveillanceReportViewSet`
- **Serializers**: `PascalCase` + `Serializer` → `SurveillanceReportSerializer`
- **Tasks**: `snake_case` + `_task` → `process_surveillance_report`
- **Services**: `PascalCase` → `PDFKPIExtractor`

### Frontend (JavaScript)
- **Components**: `PascalCase.vue` → `ReportExtractor.vue`
- **Methods**: `camelCase` → `uploadReport()`
- **Variables**: `camelCase` → `selectedReport`
- **Constants**: `UPPER_SNAKE_CASE` → `API_BASE_URL`

---

## 🎯 Important Files to Customize

### For Different PDF Formats
📄 **`backend/reports/services/pdf_extractor.py`**
- Modify regex patterns in each `_extract_*()` method
- Add new extraction methods for custom KPIs

### For Custom Word Templates
📄 **`backend/reports/services/word_generator.py`**
- Modify `_add_*_table()` methods
- Change colors, fonts, table styles

### For UI Changes
📄 **`frontend/src/components/ReportExtractor.vue`**
- Modify template for layout changes
- Update methods for new features
- Change colors in Vuetify theme

---

## 🚀 Development Workflow

1. **Start all services** (4 terminals)
2. **Make changes** to code
3. **Backend**: Django auto-reloads
4. **Frontend**: Vue hot-reloads
5. **Celery**: Restart manually (Ctrl+C, then start again)
6. **Test changes** in browser

---

This structure separates concerns clearly:
- **Models** = Data structure
- **Serializers** = Data transformation
- **Views** = HTTP handlers
- **Services** = Business logic
- **Tasks** = Background jobs
- **Components** = UI elements

Each part has ONE responsibility, making it easy to understand and modify!

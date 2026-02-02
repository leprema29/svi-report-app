# 📘 Complete Setup Guide - Surveillance Report Extractor

## Project Overview

This guide will walk you through creating a complete application that:
1. Uploads surveillance PDFs (from Mention, Brand24, etc.)
2. Extracts KPI data automatically
3. Generates formatted Word documents with tables
4. Provides a web interface for management

---

## 🗂️ Final Project Structure

```
surveillance-report-extractor/
│
├── backend/                          # Django Backend
│   ├── config/                       # Project configuration
│   │   ├── __init__.py
│   │   ├── settings.py              # Django settings
│   │   ├── urls.py                  # Root URL configuration
│   │   ├── wsgi.py
│   │   └── celery.py                # Celery configuration
│   │
│   ├── reports/                      # Main app
│   │   ├── __init__.py
│   │   ├── models.py                # Database models
│   │   ├── serializers.py           # DRF serializers
│   │   ├── views.py                 # API endpoints
│   │   ├── urls.py                  # App URLs
│   │   ├── tasks.py                 # Celery async tasks
│   │   ├── admin.py                 # Django admin
│   │   │
│   │   └── services/                # Business logic
│   │       ├── __init__.py
│   │       ├── pdf_extractor.py     # PDF KPI extraction
│   │       └── word_generator.py    # Word document generation
│   │
│   ├── media/                        # Uploaded files
│   │   ├── reports/
│   │   │   ├── pdf/
│   │   │   └── docx/
│   │
│   ├── manage.py                     # Django management
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables
│
├── frontend/                         # Vue.js Frontend
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── assets/                  # Images, styles
│   │   ├── components/              # Vue components
│   │   │   └── ReportExtractor.vue
│   │   ├── plugins/                 # Vuetify config
│   │   │   └── vuetify.js
│   │   ├── router/                  # Vue Router
│   │   │   └── index.js
│   │   ├── store/                   # Vuex store
│   │   │   └── index.js
│   │   ├── App.vue                  # Root component
│   │   └── main.js                  # Entry point
│   │
│   ├── package.json                 # Node dependencies
│   ├── vue.config.js                # Vue configuration
│   ├── babel.config.js
│   └── .env.local                   # Frontend env vars
│
├── docker-compose.yml               # Docker orchestration (optional)
├── .gitignore
└── README.md
```

---

## 🚀 PART 1: Backend Setup (Django)

### Step 1: Create Project Directory

```bash
# Create main directory
mkdir surveillance-report-extractor
cd surveillance-report-extractor

# Create backend directory
mkdir backend
cd backend
```

### Step 2: Setup Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

### Step 3: Install Django and Dependencies

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
# Django and DRF
Django==5.0.1
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.5

# PDF Processing
pdfplumber==0.10.3
PyPDF2==3.0.1
pytesseract==0.3.10
Pillow==10.2.0

# Word Document Generation
python-docx==1.1.0

# Celery for async tasks
celery==5.3.4
redis==5.0.1

# Database
psycopg2-binary==2.9.9

# Authentication
djangorestframework-simplejwt==5.3.1

# Utilities
python-dotenv==1.0.0

# Development
ipython==8.20.0
EOF

# Install all dependencies
pip install -r requirements.txt
```

### Step 4: Create Django Project

```bash
# Create Django project
django-admin startproject config .

# Your structure should now look like:
# backend/
# ├── config/
# │   ├── __init__.py
# │   ├── settings.py
# │   ├── urls.py
# │   └── wsgi.py
# ├── manage.py
# └── requirements.txt
```

### Step 5: Create Django App

```bash
# Create the reports app
python manage.py startapp reports

# Create services subdirectory
mkdir -p reports/services
touch reports/services/__init__.py
```

### Step 6: Configure Django Settings

```bash
# Edit config/settings.py
```

Add these changes to `config/settings.py`:

```python
# At the top, add:
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Update INSTALLED_APPS:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'reports',
]

# Update MIDDLEWARE (add corsheaders at the top):
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add at the end:
# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8080",
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### Step 7: Create Environment File

```bash
# Create .env file
cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
EOF
```

### Step 8: Configure Celery

```bash
# Create config/celery.py
cat > config/celery.py << 'EOF'
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
EOF

# Update config/__init__.py
cat > config/__init__.py << 'EOF'
from .celery import app as celery_app

__all__ = ('celery_app',)
EOF
```

### Step 9: Update Root URLs

```bash
# Edit config/urls.py
```

Replace with:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Step 10: Create Database Models

Now create the files I provided earlier. I'll create them step by step:

```bash
# Create reports/models.py
```

Copy the models.py content I provided earlier into this file.

### Step 11: Create Services (PDF Extractor)

```bash
# Create reports/services/pdf_extractor.py
```

Copy the pdf_extractor.py content.

### Step 12: Create Services (Word Generator)

```bash
# Create reports/services/word_generator.py
```

Copy the word_generator.py content.

### Step 13: Create Serializers

```bash
# Create reports/serializers.py
```

Copy the serializers.py content.

### Step 14: Create Views

```bash
# Create reports/views.py
```

Copy the views.py content.

### Step 15: Create URLs

```bash
# Create reports/urls.py
```

Copy the urls.py content.

### Step 16: Create Celery Tasks

```bash
# Create reports/tasks.py
```

Copy the tasks.py content.

### Step 17: Setup Admin

```bash
# Edit reports/admin.py
```

Add:

```python
from django.contrib import admin
from .models import SurveillanceReport

@admin.register(SurveillanceReport)
class SurveillanceReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']
```

### Step 18: Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin user
```

### Step 19: Test Backend

```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Start Redis (if not running)
redis-server

# Terminal 3: Start Celery
celery -A config worker -l info

# Visit http://localhost:8000/admin to verify Django works
# Visit http://localhost:8000/api/reports/ (should require login)
```

---

## 🎨 PART 2: Frontend Setup (Vue.js)

### Step 1: Navigate to Project Root

```bash
# Go back to project root
cd ..  # You should be in surveillance-report-extractor/
```

### Step 2: Create Vue.js Project

```bash
# Install Vue CLI globally (if not already installed)
npm install -g @vue/cli

# Create Vue project
vue create frontend

# When prompted, select:
# - Manually select features
# - Choose: Babel, Router, Vuex, Linter
# - Vue version: 2.x
# - Use history mode for router: Yes
# - Pick a linter: ESLint + Standard
# - Lint on save
# - Config in dedicated files

cd frontend
```

### Step 3: Install Vuetify

```bash
# Add Vuetify
vue add vuetify

# When prompted:
# - Choose: Default (recommended)
```

### Step 4: Install Additional Dependencies

```bash
# Install axios for HTTP requests
npm install axios

# Your package.json should now include vuetify and axios
```

### Step 5: Configure API Base URL

```bash
# Create .env.local file
cat > .env.local << 'EOF'
VUE_APP_API_URL=http://localhost:8000/api
EOF
```

### Step 6: Configure Vue to Proxy API Requests

```bash
# Create vue.config.js
cat > vue.config.js << 'EOF'
module.exports = {
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  transpileDependencies: ['vuetify']
}
EOF
```

### Step 7: Create Axios Instance

```bash
# Create src/plugins/axios.js
mkdir -p src/plugins
cat > src/plugins/axios.js << 'EOF'
import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
instance.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default instance;
EOF
```

### Step 8: Create Main Component

```bash
# Create src/components/ReportExtractor.vue
```

Copy the ReportExtractor.vue content I provided.

### Step 9: Update Router

```bash
# Edit src/router/index.js
```

Replace with:

```javascript
import Vue from 'vue'
import VueRouter from 'vue-router'
import ReportExtractor from '../components/ReportExtractor.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: ReportExtractor
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
```

### Step 10: Update Main App

```bash
# Edit src/App.vue
```

Replace with:

```vue
<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>
        <v-icon left>mdi-file-chart</v-icon>
        Surveillance Report Extractor
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>mdi-account-circle</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',
}
</script>
```

### Step 11: Update Main.js

```bash
# Edit src/main.js
```

Ensure it looks like:

```javascript
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import axios from './plugins/axios'

Vue.config.productionTip = false
Vue.prototype.$axios = axios

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
```

### Step 12: Test Frontend

```bash
# Start Vue dev server
npm run serve

# Visit http://localhost:8080
# You should see the Report Extractor interface
```

---

## 🧪 PART 3: Testing the Complete Application

### Step 1: Ensure All Services Are Running

You need 4 terminals:

**Terminal 1 - Django:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Celery:**
```bash
cd backend
source venv/bin/activate
celery -A config worker -l info
```

**Terminal 3 - Redis:**
```bash
redis-server
```

**Terminal 4 - Vue.js:**
```bash
cd frontend
npm run serve
```

### Step 2: Test Upload Flow

1. Visit `http://localhost:8080`
2. Enter a report title
3. Upload the PDF file I processed earlier
4. Click "Télécharger et Analyser"
5. Watch the status change: pending → processing → completed
6. Click the green Word icon to download the generated document

### Step 3: Verify Backend

1. Visit `http://localhost:8000/admin`
2. Login with your superuser credentials
3. Check "Surveillance reports" - you should see your uploaded report
4. Visit `http://localhost:8000/api/reports/` - should show JSON data

---

## 📦 PART 4: Project File Checklist

Use this checklist to ensure all files are created:

### Backend Files:
- [ ] `backend/requirements.txt`
- [ ] `backend/.env`
- [ ] `backend/manage.py` (auto-created)
- [ ] `backend/config/settings.py` (modified)
- [ ] `backend/config/urls.py` (modified)
- [ ] `backend/config/celery.py` (created)
- [ ] `backend/config/__init__.py` (modified)
- [ ] `backend/reports/models.py`
- [ ] `backend/reports/serializers.py`
- [ ] `backend/reports/views.py`
- [ ] `backend/reports/urls.py`
- [ ] `backend/reports/tasks.py`
- [ ] `backend/reports/admin.py`
- [ ] `backend/reports/services/__init__.py`
- [ ] `backend/reports/services/pdf_extractor.py`
- [ ] `backend/reports/services/word_generator.py`

### Frontend Files:
- [ ] `frontend/package.json`
- [ ] `frontend/.env.local`
- [ ] `frontend/vue.config.js`
- [ ] `frontend/src/main.js` (modified)
- [ ] `frontend/src/App.vue` (modified)
- [ ] `frontend/src/router/index.js` (modified)
- [ ] `frontend/src/plugins/axios.js`
- [ ] `frontend/src/components/ReportExtractor.vue`

---

## 🔧 PART 5: Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'reports'"

**Solution:**
```bash
# Make sure you're in backend directory
cd backend
# Ensure venv is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
# Reinstall requirements
pip install -r requirements.txt
```

### Issue 2: "CORS error" in frontend

**Solution:**
Check `backend/config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
]
```

### Issue 3: Celery not processing tasks

**Solution:**
```bash
# Make sure Redis is running
redis-cli ping
# Should return: PONG

# Restart Celery with verbose logging
celery -A config worker -l debug
```

### Issue 4: Frontend can't connect to backend

**Solution:**
- Ensure Django is running on port 8000
- Check `.env.local` has correct API URL
- Verify `vue.config.js` proxy settings

### Issue 5: PDF extraction errors

**Solution:**
Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
```

---

## 🚀 PART 6: Next Steps

### 1. Add Authentication

```bash
# In backend
pip install djangorestframework-simplejwt

# Update settings.py REST_FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# Add login endpoint in config/urls.py
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view()),
]
```

### 2. Deploy to Production

```bash
# Backend: Use Gunicorn
pip install gunicorn
gunicorn config.wsgi:application

# Frontend: Build for production
npm run build
# Serve the dist/ folder with Nginx
```

### 3. Add Docker Support

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: surveillance_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  celery:
    build: ./backend
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "8080:8080"

volumes:
  postgres_data:
```

---

## 📝 Quick Start Summary

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # Terminal 1

# 2. Celery (new terminal)
cd backend
source venv/bin/activate
celery -A config worker -l info  # Terminal 2

# 3. Redis (new terminal)
redis-server  # Terminal 3

# 4. Frontend (new terminal)
cd frontend
npm install
npm run serve  # Terminal 4

# 5. Visit http://localhost:8080
```

---

That's it! You now have a complete, working application. Follow the steps in order and you'll have everything running.

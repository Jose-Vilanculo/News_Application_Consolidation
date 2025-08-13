# Django News Application

A Django-based news platform for independent journalism and curated publications. Supports **role-based permissions**, article and newsletter publishing, subscriptions, and integrations with **email** and **X (Twitter)**.

## 📌 Features

- **Custom user roles**: Reader, Journalist, Editor
- **Reader subscriptions** to journalists or publishers
- **Journalist publishing**: articles & newsletters (independent or under a publisher)
- **Editor review** & approval workflow
- **Automatic email & X (Twitter) posting** for approved articles
- **REST API** for article retrieval
- **Responsive frontend** (Bootstrap)
- **MariaDB** database backend
- **Unit tests** included

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/django-news-app.git
cd django-news-app
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv vir-env
```
- **Windows**:  
  ```bash
  vir-env\Scripts\activate
  ```
- **macOS/Linux**:  
  ```bash
  source vir-env/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🗄️ MariaDB Setup

1. **Install MariaDB** → [Download](https://mariadb.org/download/)  
2. **Create Database & User**:
   ```sql
   CREATE DATABASE news_app CHARACTER SET utf8mb4;
   CREATE USER 'jose_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON news_app.* TO 'jose_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. **Configure `settings.py`**:
   ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': os.environ.get('DB_NAME', 'newsdb'),
          'USER': os.environ.get('DB_USER', 'newsuser'),
          'PASSWORD': os.environ.get('DB_PASSWORD', 'newspassword'),
          'HOST': os.environ.get('DB_HOST', 'db'),
          'PORT': os.environ.get('DB_PORT', '3306'),
          'OPTIONS': {
              'charset': 'utf8mb4',
          },
      }
  }
   ```
4. **Install MySQL client**:
   ```bash
   pip install mysqlclient
   ```

## 📧 Email Configuration

In `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yourprovider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```
> ⚠️ Keep credentials out of version control. Use environment variables.

## 🐦 Twitter Integration

In `settings.py`:
```python
TWITTER_API_KEY = 'your-api-key'
TWITTER_API_SECRET = 'your-api-secret'
TWITTER_ACCESS_TOKEN = 'your-access-token'
TWITTER_ACCESS_SECRET = 'your-access-secret'
```
> Obtain keys from the [Twitter Developer Portal](https://developer.twitter.com/). Secrets must **never** be committed.

## 🐳 Docker Setup

**`Dockerfile`**
- Uses `python:3.11-slim`
- Installs dependencies + MariaDB client libs
- Copies code to `/app` and exposes port `8000`

**`docker-compose.yml`**
- **db** service → MariaDB
- **web** service → Django app
- Environment variables loaded from `.env`:
  ```env
  DB_NAME=news_app
  DB_USER=jose_user
  DB_PASSWORD=your_password
  DB_HOST=db
  DB_PORT=3306
  ```
Open docker Desktop on your machine.

Run:
```bash
docker-compose up --build
```
USE: 8000:8000 port

## ▶️ Running Locally (Non-Docker)
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Visit: **http://127.0.0.1:8000**

## 🧪 Testing
```bash
python manage.py test
```

## 📡 REST API
- Get subscribed articles:  
  `GET /api/articles/`
- Use tools like Postman for authentication & queries.

## 📝 Notes
- Journalists can select a publisher when creating content.
- Readers see **only approved** articles.
- `.gitignore` should exclude `.env` and other secret files.

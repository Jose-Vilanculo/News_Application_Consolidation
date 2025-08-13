Django News Application
=======================

This is a Django-based news platform that supports independent journalism and curated publications. It includes role-based permissions, article and newsletter publishing, subscriptions, and integrations with email and X (Twitter).

Features
--------

- Custom user roles: Reader, Journalist, Editor
- Readers can subscribe to journalists or publishers
- Journalists can publish articles or newsletters independently or under a publisher
- Editors review and approve articles
- Approved articles are:
  - Emailed to subscribers
  - Tweeted via the X (Twitter) API
- REST API for retrieving articles
- Responsive frontend (Bootstrap)
- Uses MariaDB as the database
- Unit tests included

Setup Instructions
------------------

1. Clone the repository:
   git clone https://github.com/your-username/django-news-app.git
   cd django-news-app

2. Set up a virtual environment:
   python -m venv vir-env

   On Windows:
   vir-env\Scripts\activate

   On macOS/Linux:
   source vir-env/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

MariaDB Setup
-------------

1. Install MariaDB: https://mariadb.org/download/

2. Create the database and user:

   mysql -u root -p

   Then in the MariaDB shell:

   CREATE DATABASE news_app CHARACTER SET utf8mb4;
   CREATE USER 'jose_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON news_app.* TO 'jose_user'@'localhost';
   FLUSH PRIVILEGES;

3. In `settings.py`, configure the database:

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'news_app',
           'USER': 'jose_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
           }
       }
   }

4. Install MySQL client:
   pip install mysqlclient

Email Configuration
-------------------

In `settings.py`, configure your email backend:

   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.yourprovider.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your_email@example.com'
   EMAIL_HOST_PASSWORD = 'your_app_password'
   DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

Twitter Integration
-------------------

Tweet functionality is handled in `core/functions/tweet.py`. In `settings.py`, add:

   TWITTER_API_KEY = 'your-api-key'
   TWITTER_API_SECRET = 'your-api-secret'
   TWITTER_ACCESS_TOKEN = 'your-access-token'
   TWITTER_ACCESS_SECRET = 'your-access-secret'

Running the Project
-------------------

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Visit: http://127.0.0.1:8000

Testing
-------

Run unit tests:
   python manage.py test

REST API
--------

Use this endpoint to retrieve subscribed articles:

   /api/articles/

Use Postman or another API client to authenticate and retrieve content.

Final Notes
-----------

- Journalists can optionally choose a publisher when creating articles or newsletters.
- Readers only see approved content.

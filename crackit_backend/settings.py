import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present (recommended for secrets)
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-4a2!i_)^pi_nnqqom(7us3)k!l1zpbvg@20g@ykhc&)n6go=#0')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']  # Changed from [] to ['*'] for development, change to specific domains in production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crackit_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crackit_backend.wsgi.application'

# Database configuration - MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'newcrack'),
        'USER': os.getenv('MYSQL_USER', 'root'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', 'sabeesql@1730'),  # Use env for security
        'HOST': os.getenv('MYSQL_HOST', '127.0.0.1'),
        'PORT': os.getenv('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4'",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'

# Time zone configuration for India
TIME_ZONE = 'Asia/Kolkata'

# Internationalization settings
USE_I18N = True
USE_TZ = False  # Set to False to work with local time

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For production

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Use custom user model - ensure you have core/models.py with User model!
AUTH_USER_MODEL = 'core.User'

# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CSRF trusted origins for local testing and production
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://yourdomain.com',  # Add your production domain here
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Increase max number of uploaded form fields
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Cache configuration (for better performance)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Email configuration (for password reset, notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
# For production, use SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Daily Quiz Settings
DAILY_QUIZ_SETTINGS = {
    'MAX_QUESTIONS_PER_DAY': 10,  # Maximum questions per daily quiz
    'AUTO_CLEANUP_DAYS': 30,      # Auto-delete old quiz attempts after 30 days
    'TIMEZONE': 'Asia/Kolkata',   # Timezone for quiz scheduling
}

# Custom settings for your application
CRACKIT_SETTINGS = {
    'APP_NAME': 'Crack_it',
    'APP_VERSION': '1.0.0',
    'SUPPORT_EMAIL': 'support@crackit.com',
    'MAX_MOCK_TEST_ATTEMPTS': 5,
    'DAILY_QUIZ_ENABLED': True,
}

# Production settings (uncomment these for production)
if not DEBUG:
    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Database connection pooling for production
    DATABASES['default'].update({
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4'",
            'sql_mode': 'traditional',
        },
    })
    
    # Static files for production
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    
    # Allowed hosts for production (update with your domain)
    ALLOWED_HOSTS = [
        'web-production-93466.up.railway.app',
        '127.0.0.1',
        'localhost',
    ]
USE_TZ = True
TIME_ZONE = 'Asia/Kolkata'  # Or your timezone

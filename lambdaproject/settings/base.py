import os

# Path to your LambdaCast instance (no / behind the path)
try:
    from local import ABSOLUTE_PATH
except ImportError:
    ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../.."

# Domain your instance should use, for example: 'http://example.com' (no / behind the path)
try:
    from local import DOMAIN
except ImportError:
    DOMAIN = 'http://localhost:8000'

# Domain of your website, for example: 'http://example.com' (no / behind the path)
WEBSITE_URL = 'http://example.com'

# Name of your website, will be displayed in title, header and opengraph
SITE_NAME = 'LambdaCast'

# Name of the author of the rss feed
AUTHOR_NAME = 'Author Name'

# E-mail adress for the contact link in the sidebar on index page
CONTACT_EMAIL = 'root@example.com'

# URL or path to your logo that will be displayed above the right sidebar
LOGO_URL = DOMAIN + '/static/logo.png'

# Django settings for lambdaproject.project
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# If you use an virtualenv (you schould) enter it here
VIRTUALENV = ABSOLUTE_PATH + '/.venv/lib/pythons2-7/site-packages'

# The guys who will get an email if something is wrong
ADMINS = (
    ('name', 'root@localhost'),
)

# Your database settings, sqlite is good for development and testing, not for deployment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'lambda.sql',            # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de_DE'

LOCALE_PATHS = (
    ABSOLUTE_PATH + '/locale',
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
try:
    from local import MEDIA_ROOT
except ImportError:
    MEDIA_ROOT = ABSOLUTE_PATH + '/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = DOMAIN + '/media/'

# Where do you want your upload cache to live (there should be some space left)
FILE_UPLOAD_TEMP_DIR = ABSOLUTE_PATH + '/upload/'
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ABSOLUTE_PATH + '/static_files/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = DOMAIN + '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ABSOLUTE_PATH + '/lambdaproject/static/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ThisOneIsNotUniqeSoPleaseChange'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lambdaproject.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'lambdaproject.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ABSOLUTE_PATH + '/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django_admin_bootstrapped',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.markup',
    'taggit',
    'portal',
    'livestream',
    'pages',
    'djangotasks',
    'south',
    'taggit_templatetags',
    'simple_open_graph',
    'captcha',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


# ehemalig "portal/appsettings.py"
# Transloadit.com Settings

# Should we use transloadit? Otherwise we will try ffmpeg
USE_TRANLOADIT = False

# Our transloadit auth key and secret
TRANSLOAD_AUTH_KEY = ''
TRANSLOAD_AUTH_SECRET = ''
TRANSLOAD_TEMPLATE_VIDEO_ID = ''
TRANSLOAD_TEMPLATE_AUDIO_ID = ''
TRANSLOAD_TEMPLATE_VIDEO_AUDIO_ID = ''

# The URL Transloadit should notify if it was done (please remember the trailing slash)
TRANSLOAD_NOTIFY_URL = DOMAIN + '/encodingdone/'

TRANSLOAD_MP4_ENCODE = 'encode_iphone'
TRANSLOAD_WEBM_ENCODE = 'encode_webm'
TRANSLOAD_MP3_ENCODE = 'encode_mp3'
TRANSLOAD_OGG_ENCODE = 'encode_ogg'
TRANSLOAD_THUMB_ENCODE = 'create_thumb'

ENCODING_OUTPUT_DIR = MEDIA_ROOT + '/encoded/'
# How can we reach this files (public access is needed)
ENCODING_VIDEO_BASE_URL = DOMAIN + '/media/encoded/'

ENABLE_LIVESTREAMS = False

ENABLE_AUDIO_FEEDS = True
ENABLE_VIDEO_FEEDS = True

USE_BITTORRENT = False
# example: "udp://tracker.example.com:80"
BITTORRENT_TRACKER_ANNOUNCE_URL = ''
# example: "udp://tracker.example1.com:80,udp://tracker.example2.com:80,udp://tracker.example3.com:80"
BITTORRENT_TRACKER_BACKUP = ''
BITTORRENT_FILES_DIR = MEDIA_ROOT + '/torrents/'
# Where does transmission expects the original files? (This directory must be writeable for both transmission and LambdaCast!)
BITTORRENT_DOWNLOADS_DIR = ''
# What is the URL of the BITTORRENT_FILES_DIR?
BITTORRENT_FILES_BASE_URL = DOMAIN + '/media/torrents/'

# Host and port Transmission is listining on (probably localhost
TRANSMISSION_HOST = '127.0.0.1'
TRANSMISSION_PORT = 9091

# Base-Dir vor Hotfolders, example: "/opt/hotfolder/" 
HOTFOLDER_BASE_DIR = ''
HOTFOLDER_MOVE_TO_DIR = MEDIA_ROOT + '/raw/'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


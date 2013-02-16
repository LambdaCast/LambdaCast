import os
import site
import sys

sys.path.append('/data/srv/OwnTube')
sys.path.append('/data/srv/OwnTube/owntube')

site.addsitedir('/data/srv/OwnTube/.venv/lib/python2.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'owntube.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

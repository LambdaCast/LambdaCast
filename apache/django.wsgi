import os
import site
import sys

sys.path.append('/data/srv/LambdaCast')

site.addsitedir('/data/srv/LambdaCast/.venv/lib/python2.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'lambdaproject.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

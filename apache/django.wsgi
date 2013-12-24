import os
import site
import sys

sys.path.append('/opt/LambdaCast')

site.addsitedir('/opt/LambdaCast/.venv/lib/python2.7/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'lambdaproject.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

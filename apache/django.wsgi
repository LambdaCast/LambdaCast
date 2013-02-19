import os
import site
import sys

sys.path.append(os.path.abspath(os.pardir))

site.addsitedir('/opt/lambdaproject.lib/python2.7/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'lambdaproject.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

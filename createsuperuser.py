import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdvr_plus.settings')
import django
django.setup()

from django.contrib.auth.models import User

try:
    User.objects.create_superuser('admin', password='admin', email='default@email.com')
except:
    pass
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

def create_superuser():
    User = get_user_model()
    if not User.objects.filter(email=os.getenv('DJANGO_SUPERUSER_EMAIL')).exists():
        User.objects.create_superuser(
            email=os.getenv('DJANGO_SUPERUSER_EMAIL'),
            password=os.getenv('DJANGO_SUPERUSER_PASSWORD')
        )
        print('Superuser created successfully')
    else:
        print('Superuser already exists') 
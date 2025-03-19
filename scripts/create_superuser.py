import os
import logging
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

# Get logger instance
logger = logging.getLogger(__name__)

def create_superuser():
    User = get_user_model()
    try:
        if not User.objects.filter(email=os.getenv('DJANGO_SUPERUSER_EMAIL')).exists():
            User.objects.create_superuser(
                email=os.getenv('DJANGO_SUPERUSER_EMAIL'),
                password=os.getenv('DJANGO_SUPERUSER_PASSWORD')
            )
            logger.info('Superuser created successfully')
        else:
            logger.info('Superuser already exists')
    except Exception as e:
        logger.error(f'Error creating superuser: {str(e)}')

class Command(BaseCommand):
    help = 'Creates a superuser'

    def handle(self, *args, **options):
        create_superuser() 
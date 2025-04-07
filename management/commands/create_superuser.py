import os
import logging
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

# Get logger instance
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
        if not email or not password:
            self.stdout.write("Superuser credentials not provided in environment.")
            return

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password
            )
            logger.info('Superuser created successfully')
            self.stdout.write("Superuser created successfully.")
        else:
            logger.info('Superuser already exists')
            self.stdout.write("Superuser already exists.") 
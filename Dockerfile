FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Set work directory
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a startup script
RUN echo '#!/bin/sh\n\
python manage.py migrate\n\
python manage.py shell -c "from scripts.create_superuser import create_superuser; create_superuser()"\n\
gunicorn --bind 0.0.0.0:10000 stockease.wsgi:application' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
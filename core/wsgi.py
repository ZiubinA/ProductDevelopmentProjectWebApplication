"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""
import os
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
from django.core.wsgi import get_wsgi_application
from django.conf import settings

application = get_wsgi_application()

db = settings.DATABASES.get("default", {})
engine = db.get("ENGINE")
name = db.get("NAME")
host = db.get("HOST") or "localhost"
port = db.get("PORT") or ""
user = db.get("USER") or ""

logging.getLogger("django").info(
    "DB connected: engine=%s name=%s host=%s port=%s user=%s",
    engine, name, host, port, user
)

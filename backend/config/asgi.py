"""
ASGI config for config project.
"""

import os

from django.core.asgi import get_asgi_application

default_settings = "config.settings.prod" if os.getenv("DYNO") else "config.settings.dev"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)

application = get_asgi_application()

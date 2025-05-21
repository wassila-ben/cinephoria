import os
import django
from django.conf import settings
from django.core.files.storage import default_storage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinephoria_app.settings.prod')
django.setup()

print("\n==== CHECK STORAGE BACKEND ====")
print("DJANGO_SETTINGS_MODULE =", os.getenv("DJANGO_SETTINGS_MODULE"))
print("DJANGO_ENV =", os.getenv("DJANGO_ENV"))
print("DEFAULT_FILE_STORAGE =", getattr(settings, "DEFAULT_FILE_STORAGE", "(non défini)"))
print("default_storage =", default_storage.__class__)
print("CLOUDINARY_STORAGE =", getattr(settings, "CLOUDINARY_STORAGE", "(non défini)"))
print("MEDIA_URL =", settings.MEDIA_URL)
print("================================\n")

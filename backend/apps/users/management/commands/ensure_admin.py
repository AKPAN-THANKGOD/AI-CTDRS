# LOCATION: SAVE AS backend/apps/users/management/commands/ensure_admin.py  (also create empty __init__.py in management/ and management/commands/)
# Save as: apps/users/management/commands/ensure_admin.py
# (create empty __init__.py in management/ and management/commands/)
# Replaces the public create_demo_admin URL. Add to the Render start command:
#   python manage.py migrate && python manage.py ensure_admin && daphne ...
# Set ADMIN_EMAIL and ADMIN_PASSWORD as Render environment variables.
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create the admin user from environment variables if it does not exist."

    def handle(self, *args, **opts):
        User = get_user_model()
        email, pw = os.environ.get('ADMIN_EMAIL'), os.environ.get('ADMIN_PASSWORD')
        if not email or not pw:
            self.stdout.write("ADMIN_EMAIL / ADMIN_PASSWORD not set; skipping.")
            return
        if User.objects.filter(email=email).exists():
            self.stdout.write("Admin already exists.")
            return
        User.objects.create_superuser(email=email, username=email.split('@')[0],
                                      password=pw, full_name='System Admin', role='admin')
        self.stdout.write("Admin created.")
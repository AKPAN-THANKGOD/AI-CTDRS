# LOCATION: SAVE AS backend/apps/users/management/commands/ensure_admin.py  (also create empty __init__.py in management/ and management/commands/)
# Creates the admin from environment variables, or repairs an existing account.
#   ADMIN_EMAIL, ADMIN_PASSWORD        required
#   ADMIN_RESET_PASSWORD=True          also reset the password of an EXISTING account
#                                      (set it for one deploy, then delete it)
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or repair the admin user from environment variables."

    def handle(self, *args, **opts):
        User = get_user_model()
        email = (os.environ.get('ADMIN_EMAIL') or '').strip().lower()
        pw = os.environ.get('ADMIN_PASSWORD')
        if not email or not pw:
            self.stdout.write("ADMIN_EMAIL / ADMIN_PASSWORD not set; skipping.")
            return

        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            User.objects.create_superuser(
                email=email, username=email.split('@')[0], password=pw,
                full_name='System Admin', role='admin')
            self.stdout.write(f"Admin created: {email}")
            return

        # Existing account: make sure it can actually act as an admin
        changed = []
        if user.role != 'admin':
            user.role = 'admin'; changed.append('role')
        if not user.is_active:
            user.is_active = True; changed.append('is_active')
        if not (user.is_staff and user.is_superuser):
            user.is_staff = user.is_superuser = True; changed.append('staff/superuser')
        if os.environ.get('ADMIN_RESET_PASSWORD', '').lower() == 'true':
            user.set_password(pw); changed.append('password')
        if changed:
            user.save()
        self.stdout.write(f"Admin already exists: {email}. Updated: {', '.join(changed) or 'nothing'}.")
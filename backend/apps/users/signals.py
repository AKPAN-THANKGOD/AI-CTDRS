import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_migrate)
def ensure_superadmin_exists(sender, **kwargs):
    """
    Automatically creates or updates a hidden superadmin account 
    based on Render environment variables after every migration.
    """
    app_name = getattr(sender, 'name', '')
    if 'users' in app_name:
        # .strip() removes accidental trailing spaces from Render env vars
        admin_email = os.environ.get('SUPERADMIN_EMAIL', '').strip()
        admin_password = os.environ.get('SUPERADMIN_PASSWORD', '').strip()
        
        if admin_email and admin_password:
            user, created = User.objects.get_or_create(
                email=admin_email,
                defaults={
                    'username': admin_email.split('@')[0],
                    'full_name': 'System Administrator',
                    'role': 'admin',
                    'is_active': True,
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                user.set_password(admin_password)
                user.save()
                print(f"✅ [AUTO-DEPLOY] Created hidden superadmin: {admin_email}")
            else:
                if not user.is_superuser or not user.check_password(admin_password):
                    user.is_superuser = True
                    user.is_staff = True
                    user.role = 'admin'
                    user.set_password(admin_password)
                    user.save()
                    print(f"✅ [AUTO-DEPLOY] Ensured superadmin credentials for: {admin_email}")
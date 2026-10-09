"""
Quick script to create an admin user.
Run this in Render Web Shell or locally.

Usage:
    python create_admin.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 👇 CHANGE THESE TO YOUR DESIRED CREDENTIALS
ADMIN_EMAIL = 'admin@ctdrs.com'
ADMIN_PASSWORD = 'Admin1234!'
ADMIN_USERNAME = 'admin'
ADMIN_FULL_NAME = 'System Administrator'
ADMIN_ROLE = 'admin'

def create_admin():
    """Create or update admin user"""
    
    # Check if user already exists
    existing_user = User.objects.filter(email=ADMIN_EMAIL).first()
    
    if existing_user:
        print(f"⚠️  User {ADMIN_EMAIL} already exists!")
        print(f"   Resetting password and ensuring admin role...")
        
        existing_user.set_password(ADMIN_PASSWORD)
        existing_user.role = ADMIN_ROLE
        existing_user.is_active = True
        existing_user.is_staff = True
        existing_user.is_superuser = True
        existing_user.save()
        
        print(f"✅ Password reset and admin role confirmed")
        print(f"✅ You can now login with:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
    else:
        print(f"📝 Creating new admin user...")
        
        user = User.objects.create_superuser(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            full_name=ADMIN_FULL_NAME,
            role=ADMIN_ROLE
        )
        
        print(f"✅ Admin user created successfully!")
        print(f"✅ Login credentials:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
    
    print(f"\n🔐 You can now login at your Netlify site with these credentials.")

if __name__ == '__main__':
    create_admin()
# LOCATION: backend/apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()
ROLES = ('admin', 'analyst')


class RegisterSerializer(serializers.ModelSerializer):
    """Self-registration. 'role' is NOT accepted: new accounts are always analysts.
    Admins promote users through /auth/management/."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_confirm']

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        email = validated_data['email']
        base = email.split('@')[0]
        username, n = base, 1
        while User.objects.filter(username=username).exists():
            username, n = f"{base}{n}", n + 1
        return User.objects.create_user(
            username=username, email=email, password=password,
            full_name=validated_data.get('full_name', ''), role='analyst',
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        # Same message for unknown user / wrong password (no account enumeration)
        if user is None or not user.check_password(attrs['password']):
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")
        attrs['user'] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """role is read-only: users cannot change their own role."""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'date_joined', 'last_login']
        read_only_fields = ['id', 'email', 'role', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'email', 'full_name', 'is_active', 'date_joined', 'last_login']
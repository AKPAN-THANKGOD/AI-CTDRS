from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    ProfileSerializer, 
    ChangePasswordSerializer, 
    UserListSerializer
)
from apps.core.permissions import IsAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed successfully'})


class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response({'error': 'Cannot delete yourself'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        if 'role' in request.data:
            user.role = request.data['role']
            user.save()
            return Response(UserListSerializer(user).data)
        return Response({'error': 'Only role can be updated'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def create_demo_admin(request):
    """
    Bulletproof endpoint to create or reset the admin account.
    Uses create_user to avoid TypeError with custom fields.
    """
    email = 'admin@ctdrs.com'
    password = 'Admin123!'
    
    # 1. Try to find existing user by email (case-insensitive)
    user = User.objects.filter(email__iexact=email).first()
    
    if not user:
        # 2. Generate a guaranteed unique username
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        # 3. Create the user safely (this hashes the password and accepts custom fields)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name='System Admin',
            role='admin'
        )
        
        # 4. Manually elevate to superuser
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        return Response({"message": f"✅ Admin account created successfully! (Username: {username})"})
    
    # 5. If user exists, just reset password and ensure admin privileges
    user.set_password(password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.role = 'admin'
    user.save()
    
    return Response({"message": "✅ Admin account password reset successfully!"})
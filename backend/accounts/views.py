"""
Views for accounts authentication, profiles, and addresses.
"""
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.permissions import IsAdminUser, IsOwnerOrAdmin
from .models import User, UserProfile, Address
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserDetailSerializer,
    UserProfileSerializer,
    AddressSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


@extend_schema(tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    """
    Register a new customer account.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens immediately upon registration
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role
        refresh['is_admin'] = user.is_admin

        return Response({
            'message': 'Registration successful! Welcome to SmartCart.',
            'user': UserDetailSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'])
class LoginView(generics.GenericAPIView):
    """
    Authenticate with email/password and obtain JWT access + refresh tokens.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        return Response({
            'message': 'Login successful.',
            'user': UserDetailSerializer(data['user']).data,
            'access': data['access'],
            'refresh': data['refresh'],
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Auth'])
class LogoutView(generics.GenericAPIView):
    """
    Logout customer or admin by invalidating/blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update current authenticated user profile.
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        # Handle user fields
        user_fields = ['first_name', 'last_name', 'phone_number']
        for field in user_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()

        # Handle profile fields
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile_serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if profile_serializer.is_valid(raise_exception=True):
            profile_serializer.save()

        return Response({
            'message': 'Profile updated successfully.',
            'user': UserDetailSerializer(user).data
        })


@extend_schema(tags=['Auth'])
class ChangePasswordView(generics.GenericAPIView):
    """
    Change user password while logged in.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Auth'])
class PasswordResetRequestView(generics.GenericAPIView):
    """
    Initiate password reset flow by sending instructions/token.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # In production, an email is sent. For development, we return the reset link token info.
            return Response({
                'message': 'Password reset instructions have been generated.',
                'dev_info': {
                    'uid': uid,
                    'token': token,
                    'reset_link': f"/reset-password/{uid}/{token}/"
                }
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Don't leak user existence for security
            return Response({
                'message': 'If an account exists with this email, reset instructions have been sent.'
            }, status=status.HTTP_200_OK)


@extend_schema(tags=['Auth'])
class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm password reset with uid and token.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid reset link or user not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, serializer.validated_data['token']):
            return Response({'detail': 'Invalid or expired reset token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password has been reset successfully. You can now login.'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Auth'])
class AddressViewSet(viewsets.ModelViewSet):
    """
    CRUD for customer shipping and billing addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()
        if self.request.user.is_staff:
            return Address.objects.all()
        return Address.objects.filter(user=self.request.user)


@extend_schema(tags=['Admin'])
class AdminUserListView(generics.ListAPIView):
    """
    Admin-only endpoint to list registered customers and users.
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by('-date_joined')

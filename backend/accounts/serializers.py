"""
Serializers for accounts authentication, profiles, and addresses.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile, Address


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile.
    """
    class Meta:
        model = UserProfile
        fields = ['avatar', 'date_of_birth', 'gender', 'bio', 'created_at', 'updated_at']


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for customer addresses.
    """
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'full_name', 'phone_number',
            'street_address', 'landmark', 'city', 'state',
            'postal_code', 'country', 'is_default', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for User including profile and primary address.
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    is_admin = serializers.ReadOnlyField()
    is_customer = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'phone_number', 'is_email_verified',
            'is_admin', 'is_customer', 'profile', 'date_joined',
        ]
        read_only_fields = ['id', 'email', 'role', 'is_email_verified', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration serializer with password confirmation and validation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password confirmation does not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(
            email=validated_data['email'].lower(),
            username=validated_data.get('username') or validated_data['email'].split('@')[0],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=User.Role.CUSTOMER,
        )
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Custom login serializer returning JWT tokens and user payload.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')

        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            # Also try matching by username if entered instead of email
            try:
                user_obj = User.objects.get(username=email)
                user = authenticate(request=self.context.get('request'), username=user_obj.email, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled."})

        refresh = RefreshToken.for_user(user)
        # Include custom claims in token payload
        refresh['email'] = user.email
        refresh['role'] = user.role
        refresh['is_admin'] = user.is_admin

        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for authenticated user changing password.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect current password.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer to request a password reset email/token.
    """
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer to reset password using confirmation token and uid.
    """
    token = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])

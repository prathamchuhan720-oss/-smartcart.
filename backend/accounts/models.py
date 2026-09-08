"""
User, UserProfile, and Address models for SmartCart accounts app.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import TimeStampedModel


class User(AbstractUser):
    """
    Custom user model for SmartCart with email login and role management.
    """
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField('email address', unique=True, db_index=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'role']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        name = f'{self.first_name} {self.last_name}'.strip()
        return name if name else self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER


class UserProfile(TimeStampedModel):
    """
    User profile storing auxiliary information and avatars.
    """
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'
        PREFER_NOT_TO_SAY = 'N', 'Prefer not to say'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=2,
        choices=Gender.choices,
        default=Gender.PREFER_NOT_TO_SAY,
    )
    bio = models.TextField(blank=True, max_length=500)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.email}"


class Address(TimeStampedModel):
    """
    Addresses for shipping and billing.
    """
    class AddressType(models.TextChoices):
        SHIPPING = 'shipping', 'Shipping'
        BILLING = 'billing', 'Billing'
        BOTH = 'both', 'Both'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
    )
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.SHIPPING,
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.postal_code}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default address exists per user and type
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

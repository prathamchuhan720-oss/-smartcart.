from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Address


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_email_verified', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_email_verified', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    inlines = [UserProfileInline, AddressInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone_number')}),
        ('Role & Verification', {'fields': ('role', 'is_email_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'date_of_birth', 'created_at']
    search_fields = ['user__email', 'user__username']
    list_filter = ['gender']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'state', 'postal_code', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default', 'state', 'country']
    search_fields = ['user__email', 'full_name', 'city', 'postal_code', 'phone_number']

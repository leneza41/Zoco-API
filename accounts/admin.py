from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Zoco', {
            'fields': ('role', 'phone', 'address', 'preferred_language', 'avatar')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Zoco', {
            'fields': ('role', 'phone', 'address', 'preferred_language')
        }),
    )

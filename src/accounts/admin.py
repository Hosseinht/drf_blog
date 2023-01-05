from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


class AdminUser(UserAdmin):
    model = User
    list_display = ["id", "email", "full_name", "is_staff", "is_active", "is_verified"]
    ordering = ["email"]
    list_display_links = ["id", "email"]
    list_filter = ["email", "is_staff", "is_active", "is_verified"]
    readonly_fields = ["last_login", "created_date", "modified_date"]
    fieldsets = (
        ("Password", {"fields": ("password",)}),
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions and Groups",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {"fields": ("last_login", "created_date", "modified_date")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                ),
            },
        ),
    )


admin.site.register(User, AdminUser)
admin.site.register(Profile)

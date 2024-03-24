from django.contrib import admin

from apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone_number", "is_active", "is_staff", "is_superuser"]
    search_fields = ["email", "phone_number"]
    list_filter = ["is_active", "is_staff", "is_superuser"]

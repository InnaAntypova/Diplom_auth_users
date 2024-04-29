from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'phone', 'email', 'telegram_id', 'city', 'is_active')
    list_filter = ('city', 'is_active')

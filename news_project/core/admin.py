from django.contrib import admin
from .models import CustomUser, Publisher, Article, Newsletter
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Role Information", {'fields': (
            'role',
            'subscribed_publishers',
            'subscribed_journalists'
        )}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)

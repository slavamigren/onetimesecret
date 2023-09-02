from django.contrib import admin

from secret.models import Secret


@admin.register(Secret)
class SecretAdmin(admin.ModelAdmin):
    list_display = ('secret_phrase', 'message', 'expiration_time', )
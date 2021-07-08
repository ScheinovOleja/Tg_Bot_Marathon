from django.contrib import admin

# Register your models here.

from .models import User, Measurement, Photo


@admin.register(User, Measurement, Photo)
class MarathonAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin
from .models import Center, Offering


class OfferingInline(admin.TabularInline):
    model = Offering
    extra = 1


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    inlines = [OfferingInline]
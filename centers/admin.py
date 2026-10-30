from django.contrib import admin
from .models import Center, Offering, Teacher


class OfferingInline(admin.TabularInline):
    model = Offering
    extra = 1


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    inlines = [OfferingInline]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "center")
    list_filter = ("center",)
    filter_horizontal = ("offerings",)
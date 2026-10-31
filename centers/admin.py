from django.contrib import admin
from .models import Center, Offering, Teacher, AvailabilitySlot, Enrollment


class OfferingInline(admin.TabularInline):
    model = Offering
    extra = 1


class SlotInline(admin.TabularInline):
    model = AvailabilitySlot
    extra = 1


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    inlines = [OfferingInline]
    filter_horizontal = ("admins",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "center")
    list_filter = ("center",)
    filter_horizontal = ("offerings",)
    inlines = [SlotInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("display_name", "teacher", "status", "rating")
    list_filter = ("status", "teacher")
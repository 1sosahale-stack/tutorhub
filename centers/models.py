from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Center(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)

    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="administered_centers",
        help_text="Users who can manage this center's teachers and schedules.",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Offering(models.Model):
    center = models.ForeignKey(
        Center, on_delete=models.CASCADE, related_name="offerings"
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.center.name})"

class Teacher(models.Model):
    center = models.ForeignKey(
        Center, on_delete=models.CASCADE, related_name="teachers"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Login account for this teacher (used later for schedule editing).",
    )
    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    offerings = models.ManyToManyField(
        Offering, related_name="teachers", blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.center.name})"

    def can_be_edited_by(self, user):
        if not user.is_authenticated:
            return False
        return (
            user.is_superuser
            or self.user_id == user.id
            or self.center.admins.filter(pk=user.pk).exists()
        )   
    def is_moderator(self, user):
        return user.is_authenticated and (
            user.is_superuser or self.center.admins.filter(pk=user.pk).exists()
        )
    

from django.core.exceptions import ValidationError


class AvailabilitySlot(models.Model):
    DAYS = [
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"),
        (4, "Friday"), (5, "Saturday"), (6, "Sunday"),
    ]

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="slots"
    )
    day = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["day", "start_time"]

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def __str__(self):
        return f"{self.teacher.name}: {self.get_day_display()} {self.start_time}-{self.end_time}"

class Enrollment(models.Model):
    STATUS = [("current", "Current"), ("past", "Past")]

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="enrollments"
    )
    tutee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollments",
        help_text="Tutee's login account, needed to leave a review.",
    )
    display_name = models.CharField(max_length=120)
    status = models.CharField(max_length=10, choices=STATUS, default="current")
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def stars(self):
        if not self.rating:
            return ""
        return "★" * self.rating + "☆" * (5 - self.rating)

    def __str__(self):
        return f"{self.display_name} with {self.teacher.name}"
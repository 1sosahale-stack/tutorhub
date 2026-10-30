from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Center(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)

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
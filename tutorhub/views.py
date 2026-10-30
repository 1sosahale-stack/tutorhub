from django.shortcuts import render, get_object_or_404
from .models import Center


def home(request):
    centers = Center.objects.all()
    return render(request, "centers/home.html", {"centers": centers})


def center_detail(request, slug):
    center = get_object_or_404(Center, slug=slug)
    return render(request, "centers/center_detail.html", {"center": center})
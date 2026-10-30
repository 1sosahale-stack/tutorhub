from django.shortcuts import render, get_object_or_404
from .models import Center, Offering, Teacher


def home(request):
    centers = Center.objects.all()
    return render(request, "centers/home.html", {"centers": centers})


def center_detail(request, slug):
    center = get_object_or_404(Center, slug=slug)
    return render(request, "centers/center_detail.html", {"center": center})


def offering_detail(request, pk):
    offering = get_object_or_404(Offering, pk=pk)
    return render(request, "centers/offering_detail.html", {"offering": offering})


def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "centers/teacher_detail.html", {"teacher": teacher})
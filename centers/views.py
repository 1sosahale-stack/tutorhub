from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EnrollmentForm, ReviewForm
from .models import Center, Offering, Teacher, AvailabilitySlot, Enrollment
from .schedule import (
    DAY_NAMES, block_starts, blocks_to_ranges, build_rows,
    slots_to_blocks, to_time,
)


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
    blocks = slots_to_blocks(teacher.slots.all())
    enrollments = teacher.enrollments.all()
    stats = enrollments.aggregate(avg=Avg("rating"), n=Count("rating"))
    my_enrollments = []
    if request.user.is_authenticated:
        my_enrollments = list(enrollments.filter(tutee=request.user))
    return render(request, "centers/teacher_detail.html", {
        "teacher": teacher,
        "rows": build_rows(blocks),
        "days": DAY_NAMES,
        "can_edit": teacher.can_be_edited_by(request.user),
        "current": enrollments.filter(status="current"),
        "past": enrollments.filter(status="past"),
        "avg_rating": stats["avg"],
        "rating_count": stats["n"],
        "my_enrollments": my_enrollments,
    })


@login_required
def schedule_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if not teacher.can_be_edited_by(request.user):
        raise PermissionDenied

    if request.method == "POST":
        valid_starts = set(block_starts())
        chosen = set()
        for value in request.POST.getlist("cells"):
            try:
                day, minutes = (int(x) for x in value.split("-"))
            except ValueError:
                continue
            if 0 <= day <= 6 and minutes in valid_starts:
                chosen.add((day, minutes))

        with transaction.atomic():
            teacher.slots.all().delete()
            AvailabilitySlot.objects.bulk_create([
                AvailabilitySlot(
                    teacher=teacher, day=day,
                    start_time=to_time(start), end_time=to_time(end),
                )
                for day, start, end in blocks_to_ranges(chosen)
            ])
        return redirect("teacher_detail", pk=teacher.pk)

    blocks = slots_to_blocks(teacher.slots.all())
    return render(request, "centers/schedule_edit.html", {
        "teacher": teacher,
        "rows": build_rows(blocks),
        "days": DAY_NAMES,
    })


@login_required
def tutees_manage(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if not teacher.can_be_edited_by(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.teacher = teacher
            enrollment.tutee = form.cleaned_data["username"]
            enrollment.save()
            return redirect("tutees_manage", pk=teacher.pk)
    else:
        form = EnrollmentForm()

    return render(request, "centers/tutees_manage.html", {
        "teacher": teacher,
        "form": form,
        "enrollments": teacher.enrollments.all(),
        "is_moderator": teacher.is_moderator(request.user),
    })


@login_required
def enrollment_action(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    teacher = enrollment.teacher
    if not teacher.can_be_edited_by(request.user):
        raise PermissionDenied

    if request.method == "POST":
        action = request.POST.get("action")
        if action in ("current", "past"):
            enrollment.status = action
            enrollment.save(update_fields=["status"])
        elif action == "delete":
            has_review = bool(enrollment.rating or enrollment.comment)
            if has_review and not teacher.is_moderator(request.user):
                raise PermissionDenied
            enrollment.delete()
    return redirect("tutees_manage", pk=teacher.pk)


@login_required
def review_edit(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, tutee=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            return redirect("teacher_detail", pk=enrollment.teacher_id)
    else:
        form = ReviewForm(instance=enrollment)
    return render(request, "centers/review_edit.html", {
        "enrollment": enrollment,
        "form": form,
    })
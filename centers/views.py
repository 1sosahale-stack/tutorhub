from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Center, Offering, Teacher, AvailabilitySlot
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
    return render(request, "centers/teacher_detail.html", {
        "teacher": teacher,
        "rows": build_rows(blocks),
        "days": DAY_NAMES,
        "can_edit": teacher.can_be_edited_by(request.user),
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
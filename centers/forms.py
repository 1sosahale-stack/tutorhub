from django import forms
from .models import AvailabilitySlot


class SlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ["day", "start_time", "end_time"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }
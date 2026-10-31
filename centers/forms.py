from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Enrollment


class EnrollmentForm(forms.ModelForm):
    username = forms.CharField(
        required=False,
        help_text="Optional: the tutee's TutorHub username, so they can leave a review.",
    )

    class Meta:
        model = Enrollment
        fields = ["display_name", "status"]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not username:
            return None
        try:
            return get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise ValidationError("No user with that username.")


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[("", "No rating")]
        + [(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)],
        coerce=int,
        empty_value=None,
        required=False,
    )

    class Meta:
        model = Enrollment
        fields = ["rating", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"rows": 4})}
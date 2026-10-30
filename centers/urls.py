from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("centers/<slug:slug>/", views.center_detail, name="center_detail"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("centers/<slug:slug>/", views.center_detail, name="center_detail"),
    path("offerings/<int:pk>/", views.offering_detail, name="offering_detail"),
    path("teachers/<int:pk>/", views.teacher_detail, name="teacher_detail"),
]
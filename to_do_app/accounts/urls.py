from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path("accounts/signup/", views.SignUpView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]

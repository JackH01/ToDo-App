from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("add_todo", views.add_todo, name="add_todo"),
]

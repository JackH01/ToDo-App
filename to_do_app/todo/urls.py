from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add_todo", views.add_todo, name="add_todo"),
]

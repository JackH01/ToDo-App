from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("_remove<int:toDoId>", views.remove_todo, name="remove_todo"),
    path("_unshare<int:toDoId>_<int:sharedUserId>", views.unshare_todo, name="unshare_todo"),
    path("add_todo", views.add_todo, name="add_todo"),
    path("edit_todo/<int:toDoId>", views.edit_todo, name="edit_todo"),
    path("view_todo/<int:toDoId>", views.view_todo, name="view_todo"),
    path("view_todo/add_task/<int:toDoId>", views.add_task, name="add_task"),
    path("view_todo/<int:toDoId>_complete<int:taskId>", views.view_todo, name="view_todo_complete"),
    path("view_todo/<int:toDoId>_remove<int:taskId>", views.remove_task, name="remove_task"),
    path("view_todo/edit_task/<int:taskId>", views.edit_task, name="edit_task"),
    path("share_todo/<int:toDoId>", views.share_todo, name="share_todo"),
]

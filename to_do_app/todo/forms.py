from django import forms

from .models import AccessLevel

class ToDoForm(forms.Form):
    title = forms.CharField(label="Title", max_length=255)
    desc = forms.CharField(label="Description", max_length=2550)

class TaskForm(forms.Form):
    title = forms.CharField(label="Title", max_length=255)

class ShareForm(forms.Form):
    username = forms.CharField(label="username", max_length=255)
    access = forms.ChoiceField(choices=AccessLevel.choices)
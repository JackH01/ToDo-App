from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ToDo(models.Model):
    title = models.CharField(max_length=255)
    desc = models.CharField(max_length=2550)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255) # TODO remove this later
    # Each ToDo can be reordered either:
    # ... manually
    position = models.IntegerField() 
    # ... or automatically
    dateCreated = models.DateTimeField(auto_now_add=True)
    # Should be the same as the task that was last modified.
    lastModified = models.DateTimeField()
    numOfTasks = models.IntegerField(default=0)

class Task(models.Model):
    title = models.CharField(max_length=255)
    belongsTo = models.ForeignKey(ToDo, on_delete=models.CASCADE)
    done = models.BooleanField()
    dateCreated = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    position = models.IntegerField() 

    # TODO maybe add on_save method to update belongsTo last modified.
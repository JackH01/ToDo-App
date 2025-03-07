from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ToDo(models.Model):
    title = models.CharField(max_length=255)
    desc = models.CharField(max_length=2550)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Each ToDo can be reordered either:
    # ... manually
    position = models.IntegerField() 
    # ... or automatically
    dateCreated = models.DateTimeField(auto_now_add=True)
    # Should be the same as the task that was last modified.
    lastModified = models.DateTimeField() 

class Task(models.Model):
    title = models.CharField(max_length=255)
    belongsTo = models.ForeignKey(ToDo, on_delete=models.CASCADE)
    done = models.BooleanField()
    dateCreated = models.DateField(auto_now_add=True)
    lastModified = models.DateField(auto_now=True)
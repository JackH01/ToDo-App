from django.db import models
from django.contrib.auth.models import User

import datetime

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
    numOfTasks = models.IntegerField(default=0)

    # Modifying the save method to update the last modified when saving.
    def save(self, *args, **kwargs):
        self.lastModified = datetime.datetime.now()

        super(ToDo, self).save(*args, **kwargs)
        

class Task(models.Model):
    title = models.CharField(max_length=255)
    belongsTo = models.ForeignKey(ToDo, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    position = models.IntegerField() 

    # Modifying the save method to update the last modified and number of tasks
    # of the ToDo that the task belongs to.
    def save(self, *args, **kwargs):
        toDo = ToDo.objects.get(id=self.belongsTo.id)
        toDo.lastModified = datetime.datetime.now()
        
        # Checking if the current task exists in the database
        isNewTask = False
        try:
            task = Task.objects.get(id=self.id)

            # If this isn't a new task, then change the last modified field.
            self.lastModified = datetime.datetime.now()
        except:
            isNewTask = True
        
        # If this is a new task, then also increase the numOfTasks of the 
        # todo.
        if isNewTask:
            numTasks = toDo.numOfTasks
            toDo.numOfTasks = numTasks + 1

        toDo.save()

        super(Task, self).save(*args, **kwargs)

    # Modifying the delete method to update the last modified and number of tasks
    # of the ToDo that the task belongs to.
    def delete(self, *args, **kwargs):
        toDo = ToDo.objects.get(id=self.belongsTo.id)
        toDo.lastModified = datetime.datetime.now()

        numTasks = toDo.numOfTasks
        toDo.numOfTasks = numTasks - 1

        toDo.save()

        super(Task, self).delete(*args, **kwargs)

class SharedWith(models.Model):
    """
    An intermediate table/model to allow for the many-to-many relationship
    between the User and ToDo model.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo = models.ForeignKey(ToDo, on_delete=models.CASCADE)
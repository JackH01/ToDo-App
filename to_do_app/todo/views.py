from django.shortcuts import render
from django.shortcuts import redirect

import datetime

from .forms import ToDoForm, TaskForm
from .models import ToDo, Task
from .utils import validate_user_todo, validate_user_task

def home(request, toDoId=None, remove=False):
    id = request.user.id
    toDos = None
    errorMessage = None

    if toDoId == None:
        # Getting all the ToDos that belong to this user.
        id = request.user.id
        toDos = ToDo.objects.filter(user=id)

    elif remove:

        # Checking that the user has access to remove this todo.
        toDo, errorMessage = validate_user_todo(id, toDoId)
        if errorMessage == None:
            toDo = ToDo.objects.get(id=toDoId)
            toDo.delete()

            # Updating the list of toDos.
            toDos = ToDo.objects.filter(user=id)

    context = {
        "toDos": toDos,
        "errorMessage": errorMessage,
    }

    return render(request, "home.html", context)

def add_todo(request):
    errorMessage = None
    id = request.user.id
    username = request.user.username

    # If this is a POST request, process the form data
    if request.method == "POST":
        form = ToDoForm(request.POST)

        if form.is_valid():

            formData = form.cleaned_data
            title = formData["title"]
            desc = formData["desc"]

            toDos = ToDo.objects.filter(user=id)

            # Check if an identical ToDo exists for this user.
            matchingToDos = ToDo.objects.filter(user=id, title=title, desc=desc)
            isToDoUnique = len(matchingToDos) == 0
            # If the ToDo is unique then add it to the database.
            if isToDoUnique:
                position = len(toDos)
                toDo = ToDo(title=title, desc=desc, position=position, user_id=id)
                toDo.save()

                # Redirect back to home page.
                return redirect("/")
            
            # Otherwise let the user know what the problem is.
            else:
                errorMessage = """
                You already have a TODO with this title and combination, 
                please alter at least one of these values and try again.
                """

    # If a GET (or any other method) create a blank form.
    else:
        form = ToDoForm()

    context = {
        "form": form,
        "errorMessage": errorMessage,
    }

    return render(request, "add_todo.html", context)

def edit_todo(request, toDoId):
    form = None
    id = request.user.id

    # Checking that the user has access to edit this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
   
    if errorMessage == None:
        # If this is a POST request, process the form data
        if request.method == "POST":
            form = ToDoForm(request.POST)

            if form.is_valid():

                formData = form.cleaned_data
                title = formData["title"]
                desc = formData["desc"]

                # Edit relevant fields.
                toDo.title = title
                toDo.desc = desc

                toDo.save()

                # Redirect back to home page.
                return redirect("/")
                
        # If a GET (or any other method) create a form with the todo details.
        else:
            # Get current todo details
            form = ToDoForm({"title": toDo.title, "desc": toDo.desc})

    context = {
        "form": form,
        "errorMessage": errorMessage,
    }

    return render(request, "edit_todo.html", context)

def view_todo(request, toDoId, taskId=None, remove=False):
    id = request.user.id
    tasks = None
    
    # Checking that the user has access to view this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
    if errorMessage == None and taskId == None:
        tasks = Task.objects.filter(belongsTo=toDoId)

    # If a task id was specified, then we want to mark the task as complete.
    elif errorMessage == None and taskId != None:

        # Checking that the user has access to complete this task.
        task, errorMessage = validate_user_task(id, taskId)
        if errorMessage == None:
            
            if remove:
                task.delete()
            
            # Toggling the task as done/not done.
            else:
                task.done = not task.done
                task.save()

        # The last modified and (posibly the) number of tasks will have been 
        # changed, so get the todo from the database again.
        toDo = ToDo.objects.get(id=toDoId)

        # Get new list of tasks with the current task updated/deleted.
        tasks = Task.objects.filter(belongsTo=toDoId)

    context = {
        "errorMessage": errorMessage,
        "toDo": toDo,
        "tasks": tasks,
    }

    return render(request, "view_todo.html", context)

def remove_todo(request, toDoId):
    return home(request, toDoId, remove=True)

def add_task(request, toDoId):
    form = None
    id = request.user.id

    # Checking that the user has access to add to this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
    if errorMessage == None:
        # If this is a POST request, process the form data
        if request.method == "POST":
            form = TaskForm(request.POST)

            if form.is_valid():

                formData = form.cleaned_data
                title = formData["title"]

                tasks = Task.objects.filter(belongsTo=toDoId)
                # Check if an identical task exists for this todo.
                matchingTasks = Task.objects.filter(belongsTo=toDoId, 
                    title=title)
                isTaskUnique = len(matchingTasks) == 0
                # If the task is unique then add it to the database.
                if isTaskUnique:
                    position = len(tasks)
                    task = Task(title=title, position=position, 
                        lastModified=datetime.datetime.now(), belongsTo=toDo)
                    task.save()

                    # Redirect back to view todo page.
                    return redirect(f"/view_todo/{toDoId}")
                
                # Otherwise let the user know what the problem is.
                else:
                    errorMessage = """
                    You already have a Task with this title and combination, 
                    please alter at least one of these values and try again.
                    """

        # If a GET (or any other method) create a blank form.
        else:
            form = TaskForm()

    context = {
        "form": form,
        "toDo": toDo,
        "errorMessage": errorMessage,
    }

    return render(request, "add_task.html", context)

def remove_task(request, toDoId, taskId):
    return view_todo(request, toDoId, taskId, remove=True)

def edit_task(request, taskId):
    id = request.user.id
    errorMessage = None

    # Checking that the user has access to this task (and that the task exists).
    task, errorMessage = validate_user_task(id, taskId)
    if errorMessage == None:
        # If this is a POST request, process the form data
        if request.method == "POST":
            form = TaskForm(request.POST)

            if form.is_valid():

                formData = form.cleaned_data
                title = formData["title"]

                # Edit relevant fields.
                task.title = title
                task.save()

                # Redirect back to the view todo page.
                toDoId = task.belongsTo.id
                return redirect(f"/view_todo/{toDoId}")
                
        # If a GET (or any other method) create a form with the task details.
        else:
            # Get current task details
            form = TaskForm({"title": task.title})

    context = {
        "form": form,
        "errorMessage": errorMessage,
        "task": task,
    }

    return render(request, "edit_task.html", context)

# TODO add ability to share todos with other users
# ^ add linker table to allow sharing, only author can share, let
# ^^ user see all their tasks and the ones shared with them.
from django.shortcuts import render
from django.shortcuts import redirect

import datetime

from .forms import ToDoForm, TaskForm
from .models import ToDo, Task
from .utils import validate_user_todo

def home(request):

    # Getting all the ToDos that belong to this user.
    id = request.user.id
    toDos = ToDo.objects.filter(user=id).values()
    context = {
        "toDos": toDos,
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
                toDo = ToDo(title=title, desc=desc, position=position, 
                    lastModified=datetime.datetime.now(), user_id=id,
                    username=username)
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
                toDo.lastModified=datetime.datetime.now()

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

def view_todo(request, toDoId):
    id = request.user.id
    tasks = None
    
    # Checking that the user has access to view this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
    if errorMessage == None:
        tasks = Task.objects.filter(belongsTo=toDoId)

    
    context = {
        "errorMessage": errorMessage,
        "toDo": toDo,
        "tasks": tasks,
    }

    return render(request, "view_todo.html", context)

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
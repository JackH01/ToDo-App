from django.shortcuts import render
from django.shortcuts import redirect

import datetime

from .forms import ToDoForm, TaskForm, ShareForm
from .models import ToDo, Task, User, SharedWith
from .utils import validate_user_todo, validate_user_task, validate_write_access

def home(request):
    id = request.user.id
    toDos = None

    # Getting all the ToDos that belong to this user.
    toDos = ToDo.objects.filter(user=id)

    # Getting all the ToDos that are shared with this user.
    sharedWithUser = SharedWith.objects.filter(user=id)
    sharedToDoIds = list(sharedWithUser.values_list("todo", flat=True))
    sharedToDos = ToDo.objects.filter(pk__in=sharedToDoIds)

    # Combining both query sets.
    toDos = toDos | sharedToDos

    # If this is the owner of the todo, generate a list of users
    # the todo is shared with.
    for toDo in toDos:
        if id == toDo.user.id:
            toDo.genShareUserList()
        else:
            toDo.updateSharedAccessLevel(id)
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

    # Checking if the user has write access to the todo.
    if errorMessage == None:
        toDo, errorMessage = validate_write_access(id, toDoId)
   
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

        # Go to edit todo page if have write access.
        context = {
            "form": form,
            "errorMessage": errorMessage,
        }
        return render(request, "edit_todo.html", context)

    # If don't have access redirect to home page.
    else:
        return redirect("/")
    
def view_todo(request, toDoId):
    id = request.user.id
    tasks = None

    # Checking that the user has access to view this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
    if errorMessage == None:
        # Update the access level if the todo is shared.
        toDo.updateSharedAccessLevel(id)

        tasks = Task.objects.filter(belongsTo=toDoId)

    context = {
        "errorMessage": errorMessage,
        "toDo": toDo,
        "tasks": tasks,
    }

    return render(request, "view_todo.html", context)

def remove_todo(request, toDoId):
    id = request.user.id
    
    # Checking that the user has access to this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)

    # Checking if the user has write access to the todo.
    if errorMessage == None:
        toDo, errorMessage = validate_write_access(id, toDoId)

    if errorMessage == None:
        toDo = ToDo.objects.get(id=toDoId)
        toDo.delete()

    return redirect("/")

def share_todo(request, toDoId):
    id = request.user.id

     # Checking that the user has access to share this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
    if errorMessage == None:
        
        if request.method == "POST":

            form = ShareForm(request.POST)

            if form.is_valid():

                formData = form.cleaned_data
                shareUsername = formData["username"]
                shareAccess = formData["access"]

                # Make sure the user isn't trying to share the todo with themself.
                isSharingWithSelf = shareUsername == toDo.user.username

                if not isSharingWithSelf:
                    # Check if a user with this username exists
                    try:
                        shareUser = User.objects.get(username=shareUsername)

                        # If the todo is already shared with this user, then do nothing
                        sharedWithUser = SharedWith.objects.filter(user=shareUser.id, todo=toDo.id)

                        if not sharedWithUser: # The query set is empty
                            sharedWith = SharedWith(user=shareUser, todo=toDo, access=shareAccess)
                            sharedWith.save()
                        else:
                            errorMessage = f"This todo has already been shared with {shareUsername}"

                    except (User.DoesNotExist):
                        errorMessage = f"There is no user with username {shareUsername}"
                else:
                    errorMessage = "You cannot share a ToDo with yourself"
                    
        # GET request
        else:
            form = ShareForm()

    # Empty form is the todo has been successfully shared with the user.
    if errorMessage == None:
        form = ShareForm()

    context = {
        "form": form,
        "toDo": toDo,
        "errorMessage": errorMessage,
    }

    return render(request, "share_todo.html", context)

def unshare_todo(request, toDoId, sharedUserId):
    id = request.user.id

    # Checking that the user has access to unshare this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
    if errorMessage == None:

        # Checking that the todo is shared with the specified user.
        sharedWithUser = SharedWith.objects.filter(user=sharedUserId, todo=toDoId)

        if not sharedWithUser: # The query set is empty
            errorMessage = f"The todo specified is not shared with the user"
        else:
            sharedWithUser[0].delete()

    return redirect("/")

def add_task(request, toDoId):
    form = None
    id = request.user.id

    # TODO dont let user add task if they don't have write access.

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
                    user = User.objects.get(id=id)
                    task = Task(title=title, position=position, 
                        lastModified=datetime.datetime.now(), belongsTo=toDo, createdBy=user)
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
    id = request.user.id

    # Checking if the user has write access to the todo.
    toDo, errorMessage = validate_write_access(id, toDoId)
    if errorMessage == None:

     # Checking that the user has access to complete this task.
        task, errorMessage = validate_user_task(id, taskId)
        if errorMessage == None:
            task.delete()

    return redirect(f"/view_todo/{toDoId}")

def complete_task(request, toDoId, taskId):
    id = request.user.id
    tasks = None

    # Checking that the user has access to view this todo.
    toDo, errorMessage = validate_user_todo(id, toDoId)
    if errorMessage == None:

        # Checking that the user has access to complete this task.
        task, errorMessage = validate_user_task(id, taskId)
        if errorMessage == None:
            # Toggling the task as done/not done.
            task.done = not task.done
            task.save()

    return redirect(f"/view_todo/{toDoId}")

    

def edit_task(request, taskId):
    id = request.user.id
    toDoId = Task.objects.get(id=taskId).belongsTo.id
    errorMessage = None

    # Checking that the user has access to this task (and that the task exists).
    task, errorMessage = validate_user_task(id, taskId)

    # Checking if the user has write access to the todo.
    if errorMessage == None:
        toDo, errorMessage = validate_write_access(id, toDoId)

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

        # Go to edit task page if have write access.
        context = {
            "form": form,
            "errorMessage": errorMessage,
            "task": task,
        }

        return render(request, "edit_task.html", context)

    # If don't have access redirect to view todo page.
    else:
        return redirect(f"/view_todo/{toDoId}")
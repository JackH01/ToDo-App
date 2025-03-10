from django.shortcuts import render
from django.shortcuts import redirect

import datetime

from .forms import ToDoForm
from .models import ToDo

# Create your views here.
def home(request):

    # Getting all the ToDos that belong to this user.
    id = request.user.id
    toDos = ToDo.objects.filter(user=id).values()
    print(toDos)
    print(toDos[0]["title"])

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

        # TODO when add edit button add auto fill based on values in database 
        # if they exist

    context = {
        "form": form,
        "errorMessage": errorMessage,
    }

    return render(request, "add_todo.html", context)
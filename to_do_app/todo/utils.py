from .models import ToDo, Task, SharedWith, AccessLevel

def validate_user_todo(userId, toDoId):
    """
    Used to validate whether a user should have access to a given todo.
    Prevents users from accessing other todos by specifying their id in the
    url.

    Params:
        - userId: int
        - toDoId: int

    returns: (toDo, errorMessage)
        - toDo
            - models.ToDo if the todo esixts
            - None if it doesn't
        - errorMessage
            - A string with the error message if the user cannot access the 
            todo.
            - None if the user should be able to access the todo.
    """

    errorMessage = None
    toDo = None
    
    # Making sure a todo with the id specified exists.
    try:
        toDo = ToDo.objects.get(id=toDoId)
    # If the id passed via the url is invalid, raise an error.
    except:
        errorMessage = f"""
        There is no ToDo with id {toDoId}.
        Please go back to the home page and try again.
        """
    else:
        # Making sure the user has access to the todo.
        userIdFromToDo = toDo.user.id
        # - Checking they either own the todo or...
        userOwnsToDo = userId == userIdFromToDo
        # - ... have the todo shared with them.
        sharedWith = SharedWith.objects.filter(todo=toDoId, user=userId)
        toDoSharedWithUser = sharedWith.exists()

        if (not userOwnsToDo) and (not toDoSharedWithUser):
            errorMessage = f"""
            You don't have access to this ToDo.
            Please go back to the home page and try a different one.
            """
    
    return (toDo, errorMessage)

def validate_user_task(userId, taskId):
    """
    Used to validate whether a user should have access to a given task.
    Prevents users from accessing other tasks by specifying their id in the
    url.

    Params:
        - userId: int
        - taskId: int

    returns: (task, errorMessage)
        - task
            - models.Task if the task esixts
            - None if it doesn't
        - errorMessage
            - A string with the error message if the user cannot access the 
            task.
            - None if the user should be able to access the task.
    """

    errorMessage = None
    task = None

    # Making sure a task with the id specified exists.
    try:
        task = Task.objects.get(id=taskId)
    # If the id passed via the url is invalid, raise an error.
    except:
        errorMessage = f"""
        There is no Task with id {taskId}.
        Please go back to the home page and try again.
        """
    else:
        # Making sure the user has access to the task.
        # Every task shares the same access level as its parent todo, 
        # so we can just call validate_user_todo.
        todo_id = task.belongsTo.id
        _, errorMessage = validate_user_todo(userId, todo_id)
    
    return (task, errorMessage)

def validate_write_access(userId, toDoId):
    """
    Used to validate whether a user has write access to a given todo and its
    tasks.
    NOTE: todos and their tasks share access levels, so we only need to check
    the users access to the todo.

    Params:
        - userId: int
        - taskId: int

    returns: (todo, errorMessage)
        - todo
            - the todo with write access updated.
        - errorMessage
            - A string with the error message if the user does not have write 
            access to the todo.
            - None otherwise.
    """
    todo = ToDo.objects.get(id=toDoId)
    errorMessage = None

    todo.updateSharedAccessLevel(userId)
    if (todo.accessLevel != AccessLevel.WRITE):
        errorMessage = "You do not have write access to this ToDo."

    return (todo, errorMessage)
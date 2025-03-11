from .models import ToDo

def validate_user_todo(userId, toDoId):
    """
    Used to validate whether a user should have access to a given todo.
    Prevents users from accessing other todos by specifying their id in the
    url.

    Params:
        - userId: int
        - toDoId: int

    returns: (errorMessage, toDo)
        - errorMessage
            - A string with the error message if the user cannot access the 
            todo.
            - None if the user should be able to access the todo.
        - toDo
            - models.ToDo if the todo esixts
            - None if it doesn't
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
        if userId != userIdFromToDo:
            errorMessage = f"""
            You don't have access to this ToDo.
            Please go back to the home page and try a different one.
            """
    
    return (toDo, errorMessage)
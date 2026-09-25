from kanban_app.models import Task, Comment
"""
Utility functions for task validation.
Functions:
    - checkTaskIdIsValid(self, task_id): Checks if the provided task ID is valid (not None and is a digit).
    - checkTaskIdExists(self, task_id): Checks if a task with the provided ID exists in the database.
"""

def checkTaskIdIsValid(self, task_id):
        task_id_not_none = task_id is not None
        task_id_is_digit = str(task_id).isdigit()
        return task_id_not_none and task_id_is_digit

def checkTaskIdExists(self, task_id):
    return Task.objects.filter(id=task_id).exists()

def checkCommentIdIsValid(self, comment_id):
        print(f"Checking validity of comment ID: {comment_id}")
        comment_id_not_none = comment_id is not None
        comment_id_is_digit = str(comment_id).isdigit()
        print(f"Comment ID not None: {comment_id_not_none}, Comment ID is digit: {comment_id_is_digit}")
        return comment_id_not_none and comment_id_is_digit

def checkCommentIdExists(self, comment_id):
    return Comment.objects.filter(id=comment_id).exists()
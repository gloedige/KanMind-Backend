from kanban_app.models import Task
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
    return Task.objects.filter(pk=task_id).exists()
from kanban_app.models import Task, Comment, Board
"""
Utility functions for task, comment, and board validation.
"""
def checkIdIsValid(id):
        """
        Checks if the provided ID is valid (not None and is a digit).
        """
        id_not_none = id is not None
        id_is_digit = str(id).isdigit()
        return id_not_none and id_is_digit

def checkTaskIdExists(task_id):
        """
        Checks if a task with the provided ID exists in the database.
        """
        return Task.objects.filter(id=task_id).exists()

def checkCommentIdExists(comment_id):
        """
        Checks if a comment with the provided ID exists in the database.
        """
        return Comment.objects.filter(id=comment_id).exists()

def checkBoardIdExists(board_id):
        """
        Checks if a board with the provided ID exists in the database.
        """
        return Board.objects.filter(id=board_id).exists()
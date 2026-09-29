from django.db import models

from core import settings

class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Member', blank=True, related_name='boards')

    def __str__(self):
        return f"{self.title}"

    
class Member(models.Model):
    # email = models.EmailField(unique=True)
    # fullname = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, blank=False, null=False, related_name='board_members')

    class Meta:
        unique_together = ('user', 'board')

    def __str__(self):
        return f"{self.user.username}"


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('review', 'Review'), ('done', 'Done')], default='todo')
    priority = models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    assignee = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_tasks')
    reviewer = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_tasks')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='owned_tasks')
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=30)
    content = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True, related_name='comments')

    def __str__(self):
        return f"{self.author} - {self.content[:20]}"

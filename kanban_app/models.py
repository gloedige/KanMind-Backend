import email

from django.db import models
from django.contrib.auth.models import User as Owner


class Member(models.Model):
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.fullname}"


class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    members = models.ManyToManyField(Member, blank=True, related_name='boards')

    def __str__(self):
        return f"{self.title}"


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('review', 'Review'), ('done', 'Done')], default='todo')
    priority = models.CharField(max_length=50, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    assignee = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_tasks')
    reviewer = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_tasks')
    due_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}"

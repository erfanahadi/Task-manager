from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    COLUMN_TODO = "To Do"
    COLUMN_IN_PROGRESS = "In Progress"
    COLUMN_COMPLETED = "Completed"
    COLUMN_CHOICES = [
        (COLUMN_TODO, "To Do"),
        (COLUMN_IN_PROGRESS, "In Progress"),
        (COLUMN_COMPLETED, "Completed"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    progress = models.PositiveSmallIntegerField(default=0)
    column = models.CharField(max_length=20, choices=COLUMN_CHOICES, default=COLUMN_TODO)
    creator = models.ForeignKey(
        User, related_name="created_tasks", on_delete=models.CASCADE
    )
    assignee = models.ForeignKey(
        User,
        related_name="assigned_tasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    indexes = [
            models.Index(fields=['column']),        # for filtering by column
            models.Index(fields=['assignee']),      # for filtering by assignee
            models.Index(fields=['creator']),       # for filtering by creator
        ]

    def save(self, *args, **kwargs):
        # Automatic column update based on progress
        if self.progress >= 100:
            self.progress = 100
            self.column = self.COLUMN_COMPLETED
        elif self.column == self.COLUMN_IN_PROGRESS and self.progress < 1:
            self.progress = 1
        elif self.column == self.COLUMN_TODO:
            self.progress = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


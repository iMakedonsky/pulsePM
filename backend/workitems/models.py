from datetime import date
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from organizations.models import Member, WorkSpace


def validate_not_past(value: date) -> None:
    if value < timezone.localdate():
        raise ValidationError('Value cannot be in the past.')


class WorkItem(models.Model):
    class Status(models.TextChoices):
        TODO = 'to do'
        IN_PROGRESS = 'in progress'
        REVIEW = 'review'
        DONE = 'done'
        TEST = 'test'
        TEST_PASS = 'test done'  # noqa: S105 - a workflow status, not a credential

    class Priority(models.TextChoices):
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'
        MAJOR = 'major'

    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='report_by')
    assigned_to = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='assigned_to')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, default='')
    status = models.CharField(choices=Status.choices, max_length=11, default=Status.TODO)
    priority = models.CharField(choices=Priority.choices, max_length=11, default=Priority.HIGH)
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(validators=[validate_not_past])
    estimated_time = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    time_spent = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    last_update = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

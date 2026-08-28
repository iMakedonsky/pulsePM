from datetime import date
from typing import Any

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


def validate_not_past(value: date) -> None:
    """
    Validate that value is not past
    Method use datetime.date to validate if value is not past
    :return: None | ValidationError if value is a past date.
    """
    if value < date.today():
        raise ValidationError('Value cannot be in the past.')


class Organization(models.Model):
    """
    Store Organization data.
    """

    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(max_length=500, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Member(models.Model):
    """
    Store Organization member data. Also class inherit Account data.
    """

    class OrgRoles(models.TextChoices):
        OWNER = 'owner'
        PM = 'project-manager'
        CONTRIBUTOR = 'contributor'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=False, related_name='members')
    role = models.CharField(choices=OrgRoles.choices, max_length=100, default=OrgRoles.CONTRIBUTOR)
    position = models.CharField(max_length=200, null=True, default='', blank=True)
    location = models.CharField(max_length=200, null=True, default='', blank=True)
    time_zone = models.CharField(max_length=200, null=True, default='', blank=True)
    avatar_url = models.CharField(max_length=200, null=True, default='', blank=True)
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'organization'], name='unique_user_org')]

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Careful save, that checks constraints [UniqueConstraint].
        It refuse connect the same 'account' if account belongs in the same org as member already.
        :return: might save items but if full_clean() catch some  brake constraint it will return exeption ERR
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.user.username


class WorkSpace(models.Model):
    """
    Store Work space (project) data.
    """

    id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, null=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False)
    space_code = models.CharField(max_length=5, unique=True, null=False)
    description = models.TextField(max_length=500, null=True, default='')
    icon_url = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name


class WorkItem(models.Model):
    """
    Store Work item data.
    """

    class Status(models.TextChoices):
        TODO = 'to do'
        IN_PROGRESS = 'in progress'
        REVIEW = 'review'
        DONE = 'done'
        TEST = 'test'
        TEST_PASS = 'test done'

    class Priority(models.TextChoices):
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'
        MAJOR = 'major'

    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='report_by')
    assigned_to = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='assigned_to')
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, default='')
    status = models.CharField(choices=Status.choices, max_length=11, default=Status.TODO)
    priority = models.CharField(choices=Priority.choices, max_length=11, default=Priority.HIGH)
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(validators=[validate_not_past], null=False)
    estimated_time = models.IntegerField(validators=[MinValueValidator(0)], null=False, default=0)
    time_spent = models.IntegerField(validators=[MinValueValidator(0)], null=False, default=0)
    last_update = models.DateTimeField(default=timezone.now)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Inhirited method witch will call to check validation in ORM.
        :return: validation errors if due date would be in the past.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

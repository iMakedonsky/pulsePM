import datetime

from django.db import models
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class TestUser(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin'
        USER = 'user'

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200)
    email = models.EmailField()
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.id} {self.username} {self.email} {self.role} {self.created_at}'

class TestOrganizationMember(models.Model):
    id = models.AutoField(primary_key=True)
    department = models.CharField(max_length=200)
    user_id = models.ForeignKey(TestUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id} {self.department}'
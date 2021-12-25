from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db.models import PositiveIntegerField
import uuid

from .utilities import get_timestamp_path


class PostUser(AbstractUser):
    username = models.CharField(max_length=20, unique=False, null=True)

    name = models.CharField(max_length=20, null=True)
    surname = models.CharField(max_length=20, null=True)
    fname = models.CharField(max_length=20, null=True)

    phoneNumber = PositiveIntegerField(unique=True, null=True, blank=False)
    email = models.EmailField('email', unique=True)
    age = models.PositiveIntegerField(null=True)

    passport = models.CharField(max_length=20, unique=True, null=True)

    date_last_request = models.DateTimeField(auto_now_add=True, db_index=True, null=True,
                                             verbose_name='Last request to server')
    is_activated = models.BooleanField(default=True, db_index=True, null=True,
                                       verbose_name='Is this account activated?')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class QueueConscripts(models.Model):
    choices = (('dar', 'Дарницький військовий комісаріат'),
               ('dec', 'Деснянський військовий комісаріат'),
               ('dni', 'Дніпровський військовий комісаріат'))
    department = models.CharField(max_length=3, choices=choices)
    week_day = models.CharField(max_length=2, choices=(('tu', 'tuesday'), ('th', 'thursday')))
    time = models.CharField(max_length=20)
    people = models.ForeignKey(PostUser, on_delete=models.PROTECT)
    busy = models.CharField(max_length=20, choices=(('', 'Вільно'), ('Зайнято', 'Зайнято')), default='Вільно')

    USERNAME_FIELD = 'department'

    def __str__(self):
        return str(self.department + " " + self.week_day + " " + str(self.time))


class Test(models.Model):
    aaa = models.CharField(max_length=20)

    def ste(self):
        return self.aaa


from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from .utilities import get_timestamp_path

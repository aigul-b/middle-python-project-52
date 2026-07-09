# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from statuses.models import Status

User = get_user_model()


class Task(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name='Статус',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='author_tasks',
    )

    executor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='executor_tasks',
        verbose_name='Исполнитель',
        null=True,
        blank=True

    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
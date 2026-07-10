# tasks/filters.py
import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from statuses.models import Status
from labels.models import Label
from .models import Task

User = get_user_model()


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label=_('Статус'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label=_('Исполнитель'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        label=_('Метка'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    own_tasks = django_filters.BooleanFilter(
        method='filter_own_tasks',
        label=_('Только свои задачи'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels']

    def filter_own_tasks(self, queryset, name, value):
        if value:
            return queryset.filter(author=self.request.user)
        return queryset
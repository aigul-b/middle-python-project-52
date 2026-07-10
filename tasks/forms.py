from django.forms import ModelForm
from tasks.models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'status', 'executor', 'labels']
        labels = {
            'name': 'Имя',
            'description':'Описание',
            'status': 'Статус',
            'executor' : 'Исполнитель',
            'labels': 'Метки',
        }
        error_messages = {
            'name': {
                'unique': 'Задача с таким именем уже существует.'
            }
        }

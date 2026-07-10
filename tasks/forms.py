from django.forms import ModelForm, ModelChoiceField
from tasks.models import Task
from django.contrib.auth.models import User

class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, user):
        return f'{user.first_name} {user.last_name}'.strip() or user.username

class TaskForm(ModelForm):
    executor = UserModelChoiceField(
        queryset=User.objects.all(),
        label='Исполнитель',
    )
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

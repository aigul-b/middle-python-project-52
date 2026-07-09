from django.forms import ModelForm
from labels.models import Label


class LabelForm(ModelForm):
    class Meta:
        model = Label
        fields = ['name']
        labels = {
            'name': 'Имя',
        }
        error_messages = {
            'name': {
                'unique': 'Метка с таким именем уже существует.',
            }
        }
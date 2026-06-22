from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']
        labels =  {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя'
        }
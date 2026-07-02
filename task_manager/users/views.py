from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect

from .forms import UserRegistrationForm

class IndexView(TemplateView):
    template_name = 'index.html'

class UsersListView(ListView):
    model = User
    template_name = 'users/index.html'
    context_object_name = 'users'


class UserCreateView(SuccessMessageMixin, CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/create.html'
    success_url = reverse_lazy('login')
    success_message = 'Пользователь успешно зарегистрирован'


class UserPermissionMixin(LoginRequiredMixin):
    """Разрешаем менять/удалять только самого себя."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Вы не авторизованы! Пожалуйста, выполните вход.')
            return redirect('login')
        if request.user.pk != self.get_object().pk:
            messages.error(request, 'У вас нет прав для изменения.')
            return redirect('users')
        return super().dispatch(request, *args, **kwargs)


class UserUpdateView(UserPermissionMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/update.html'
    success_url = reverse_lazy('users')
    success_message = 'Пользователь успешно изменен'


class UserDeleteView(UserPermissionMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users')
    success_message = 'Пользователь успешно удален'


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = 'users/login.html'
    next_page = reverse_lazy('home')
    success_message = 'Вы залогинены'


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы разлогинены')
        return super().dispatch(request, *args, **kwargs)
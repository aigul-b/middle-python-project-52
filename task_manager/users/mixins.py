from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated:
        return super().dispatch(request, *args, **kwargs)
    if request.user.pk != kwargs['pk']:
        messages.error(request, 'У вас нет прав для изменения')
        return redirect(reverse_lazy('users_index'))
    return super().dispatch(request, *args, **kwargs)
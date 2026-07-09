from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Task
from statuses.models import Status


class UserCRUDTest(TestCase):
    fixtures = ['users.json']

    def test_create(self):
        data = {
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'username': 'ivan',
            'password1': 'SuperPass123',
            'password2': 'SuperPass123',
        }
        response = self.client.post(reverse('user_create'), data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='ivan').exists())

    def test_update(self):
        user = User.objects.first()
        self.client.force_login(user)
        data = {
            'first_name': 'Updated',
            'last_name': user.last_name,
            'username': user.username,
            'password1': 'SuperPass123',
            'password2': 'SuperPass123',
        }
        response = self.client.post(
            reverse('user_update', kwargs={'pk': user.pk}), data
        )
        if response.status_code == 200:
            self.fail(f"Форма не прошла. Ошибки: {response.context['form'].errors.as_json()}")
        self.assertRedirects(response, reverse('users'))
        
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')

    def test_delete(self):
        user = User.objects.first()
        self.client.force_login(user)
        response = self.client.post(
            reverse('user_delete', kwargs={'pk': user.pk})
        )
        self.assertRedirects(response, reverse('users'))
        self.assertFalse(User.objects.filter(pk=user.pk).exists())

    def test_update_other_user_forbidden(self):
        users = User.objects.all()
        user1, user2 = users[0], users[1]
        self.client.force_login(user1)  
        response = self.client.post(
            reverse('user_update', kwargs={'pk': user2.pk}),
            {'first_name': 'Hacked', 'last_name': user2.last_name,
            'username': user2.username,
            'password1': 'SuperPass123', 'password2': 'SuperPass123'}
    )
        self.assertRedirects(response, reverse('users'))
        user2.refresh_from_db()
        self.assertNotEqual(user2.first_name, 'Hacked')   # не изменился

    def test_delete_user_with_tasks_blocked(self):
        user = User.objects.first()
        status = Status.objects.create(name='В работе')
        Task.objects.create(
            name='Задача',
            status=status,
            author=user,
        )
        self.client.force_login(user)
        response = self.client.post(
            reverse('user_delete', kwargs={'pk': user.pk}), follow=True
        )
        self.assertTrue(User.objects.filter(pk=user.pk).exists())
        self.assertContains(response, 'Невозможно удалить пользователя')

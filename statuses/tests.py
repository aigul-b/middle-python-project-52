from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .models import Status
from tasks.models import Task

User = get_user_model()


class StatusCRUDTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)
        self.status = Status.objects.create(name='В работе')

    def test_index_view(self):
        response = self.client.get(reverse_lazy('statuses_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'В работе')

    def test_create_view(self):
        response = self.client.post(reverse_lazy('statuses_create'), {'name': 'Новый'})
        self.assertRedirects(response, reverse_lazy('statuses_index'))
        self.assertTrue(Status.objects.filter(name='Новый').exists())

    def test_create_duplicate_name(self):
        response = self.client.post(reverse_lazy('statuses_create'), {'name': 'В работе'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Статус с таким именем уже существует')

    def test_update_view(self):
        response = self.client.post(
            reverse_lazy('statuses_update', args=[self.status.pk]),
            {'name': 'Изменено'},
        )
        self.assertRedirects(response, reverse_lazy('statuses_index'))
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Изменено')

    def test_delete_view(self):
        response = self.client.post(reverse_lazy('statuses_delete', args=[self.status.pk]))
        self.assertRedirects(response, reverse_lazy('statuses_index'))
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())

    def test_index_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('statuses_index'))
        self.assertEqual(response.status_code, 302)
    
    def test_delete_status_with_related_task(self):
        Task.objects.create(
            name='Тестовая задача',
            status=self.status,
            author=self.user,
        )
        response = self.client.post(reverse_lazy('statuses_delete', args=[self.status.pk]))
        self.assertRedirects(response, reverse_lazy('statuses_index'))
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())
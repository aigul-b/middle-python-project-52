from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from labels.models import Label
from statuses.models import Status
from tasks.models import Task

User = get_user_model()


class LabelCRUDTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='author', password='testpass123')
        self.client.force_login(self.user)

        self.label = Label.objects.create(name='Баг')


    def test_index_view(self):
        response = self.client.get(reverse_lazy('labels:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Баг')


    def test_create_view(self):
        response = self.client.post(reverse_lazy('labels:create'), {
            'name': 'Фича',
        })
        self.assertRedirects(response, reverse_lazy('labels:list'))
        self.assertTrue(Label.objects.filter(name='Фича').exists())


    def test_create_duplicate_name(self):
        response = self.client.post(reverse_lazy('labels:create'), {
            'name': 'Баг',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')


    def test_update_view(self):
        response = self.client.post(
            reverse_lazy('labels:update', args=[self.label.pk]),
            {'name': 'Критический баг'},
        )
        self.assertRedirects(response, reverse_lazy('labels:list'))
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'Критический баг')


    def test_delete_view_without_tasks(self):
        response = self.client.post(reverse_lazy('labels:delete', args=[self.label.pk]))
        self.assertRedirects(response, reverse_lazy('labels:list'))
        self.assertFalse(Label.objects.filter(pk=self.label.pk).exists())


    def test_delete_view_with_related_task(self):
        status = Status.objects.create(name='В работе')
        task = Task.objects.create(
            name='Задача с меткой',
            status=status,
            author=self.user,
        )
        task.labels.add(self.label)

        response = self.client.post(
            reverse_lazy('labels:delete', args=[self.label.pk]),
            follow=True,
        )
        self.assertRedirects(response, reverse_lazy('labels:list'))
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())
        self.assertContains(response, 'Невозможно удалить метку')


    def test_index_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('labels:list'))
        self.assertEqual(response.status_code, 302)


    def test_create_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('labels:create'))
        self.assertEqual(response.status_code, 302)


    def test_update_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('labels:update', args=[self.label.pk]))
        self.assertEqual(response.status_code, 302)


    def test_delete_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('labels:delete', args=[self.label.pk]))
        self.assertEqual(response.status_code, 302)
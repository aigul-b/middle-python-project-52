from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from statuses.models import Status
from tasks.models import Task
from labels.models import Label

User = get_user_model()


class TaskCRUDTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='testpass123')
        self.other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.force_login(self.author)

        self.status = Status.objects.create(name='В работе')

        self.task = Task.objects.create(
            name='Тестовая задача',
            description='Описание задачи',
            status=self.status,
            author=self.author,
        )


    def test_index_view(self):
        response = self.client.get(reverse_lazy('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')


    def test_detail_view(self):
        response = self.client.get(reverse_lazy('tasks:detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
        self.assertContains(response, 'Описание задачи')


    def test_create_view(self):
        response = self.client.post(reverse_lazy('tasks:create'), {
            'name': 'Новая задача',
            'description': 'Описание',
            'status': self.status.pk,
        })
        self.assertRedirects(response, reverse_lazy('tasks:list'))
        self.assertTrue(Task.objects.filter(name='Новая задача').exists())

        new_task = Task.objects.get(name='Новая задача')
        self.assertEqual(new_task.author, self.author)


    def test_create_duplicate_name(self):
        response = self.client.post(reverse_lazy('tasks:create'), {
            'name': 'Тестовая задача',
            'description': 'Другое описание',
            'status': self.status.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')


    def test_update_view(self):
        response = self.client.post(
            reverse_lazy('tasks:update', args=[self.task.pk]),
            {
                'name': 'Изменённая задача',
                'description': self.task.description,
                'status': self.status.pk,
            },
        )
        self.assertRedirects(response, reverse_lazy('tasks:list'))
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Изменённая задача')


    def test_delete_view_by_author(self):
        response = self.client.post(reverse_lazy('tasks:delete', args=[self.task.pk]))
        self.assertRedirects(response, reverse_lazy('tasks:list'))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())


    def test_delete_view_by_non_author(self):
        self.client.force_login(self.other_user)
        response = self.client.post(reverse_lazy('tasks:delete', args=[self.task.pk]),follow=True)
        self.assertRedirects(response, reverse_lazy('tasks:list'))
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
        self.assertContains(response, 'Задачу может удалить только ее автор')


    def test_index_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('tasks:list'))
        self.assertEqual(response.status_code, 302)


    def test_create_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('tasks:create'))
        self.assertEqual(response.status_code, 302)

    def test_detail_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('tasks:detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)


    def test_update_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('tasks:update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)


    def test_delete_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('tasks:delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)



class TaskFilterTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='testpass123')
        self.other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.force_login(self.author)

        self.status1 = Status.objects.create(name='В работе')
        self.status2 = Status.objects.create(name='Готово')

        self.label1 = Label.objects.create(name='Баг')
        self.label2 = Label.objects.create(name='Фича')

        self.task1 = Task.objects.create(
            name='Задача автора',
            description='Описание',
            status=self.status1,
            author=self.author,
            executor=self.author,
        )
        self.task1.labels.add(self.label1)

        self.task2 = Task.objects.create(
            name='Задача другого пользователя',
            description='Описание',
            status=self.status2,
            author=self.other_user,
            executor=self.other_user,
        )
        self.task2.labels.add(self.label2)

    def test_filter_by_status(self):
        response = self.client.get(reverse_lazy('tasks:list'), {'status': self.status1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Задача автора')
        self.assertNotContains(response, 'Задача другого пользователя')

    def test_filter_by_executor(self):
        response = self.client.get(reverse_lazy('tasks:list'), {'executor': self.other_user.pk})
        self.assertContains(response, 'Задача другого пользователя')
        self.assertNotContains(response, 'Задача автора')

    def test_filter_by_label(self):
        response = self.client.get(reverse_lazy('tasks:list'), {'labels': self.label1.pk})
        self.assertContains(response, 'Задача автора')
        self.assertNotContains(response, 'Задача другого пользователя')

    def test_filter_own_tasks(self):
        response = self.client.get(reverse_lazy('tasks:list'), {'own_tasks': 'on'})
        self.assertContains(response, 'Задача автора')
        self.assertNotContains(response, 'Задача другого пользователя')

    def test_no_filter_returns_all_tasks(self):
        response = self.client.get(reverse_lazy('tasks:list'))
        self.assertContains(response, 'Задача автора')
        self.assertContains(response, 'Задача другого пользователя')

    def test_combined_filters(self):
        response = self.client.get(
            reverse_lazy('tasks:list'),
            {'status': self.status1.pk, 'labels': self.label1.pk},
        )
        self.assertContains(response, 'Задача автора')
        self.assertNotContains(response, 'Задача другого пользователя')

    def test_filter_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse_lazy('tasks:list'), {'status': self.status1.pk})
        self.assertEqual(response.status_code, 302)
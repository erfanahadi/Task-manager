
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Task

class TaskCreationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )

    def test_task_creation(self):
        response = self.client.post(
            reverse('task-create'),
            {
                'title': 'Test Task',
                'description': 'Test Description'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 1)

        task = Task.objects.first()
        self.assertEqual(task.progress, 0)
        self.assertEqual(task.column, 'To Do')
        self.assertEqual(task.creator, self.user)
        self.assertIsNone(task.assignee)

    def test_task_creation_requires_authentication(self):
        self.client.credentials()  # remove token

        response = self.client.post(
            reverse('task-create'),
            {'title': 'Test', 'description': 'Test'},
            format='json'
        )

        self.assertEqual(response.status_code, 401)

class TaskMoveTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpassword2'
        )
        self.token = Token.objects.create(user=self.user2)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            creator=self.user,
            )

      # test when the task is moved to "In Progress" the progress is 1
    def test_task_move_to_in_progress(self):
        response = self.client.post(
            reverse('task-start', args=[self.task.id]),
            {'column': 'In Progress'},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.column, 'In Progress')
        self.assertEqual(self.task.progress, 1)
        self.assertEqual(self.task.assignee, self.user2)

    # test when the task is moved to "Completed" the progress is 100
    def test_task_move_to_completed(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-move', args=[self.task.id]),
            {'column': 'Completed'},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.column, 'Completed')
        self.assertEqual(self.task.progress, 100)

    # test when the task is moved to "To Do" the progress is 0
    def test_task_move_to_to_do(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-move', args=[self.task.id]),
            {'column': 'To Do'},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.column, 'To Do')
        self.assertEqual(self.task.progress, 0)
        self.assertIsNone(self.task.assignee)

    # test when the task is moved to an invalid column the response is 400
    def test_task_move_to_invalid_column(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-move', args=[self.task.id]),
            {'column': 'Invalid Column'},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.task.column, 'To Do')
        self.assertEqual(self.task.progress, 0)

    # test when the task is moved to a valid column the response is 200
    def test_task_move_to_valid_column(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-move', args=[self.task.id]),
            {'column': 'In Progress'},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.column, 'In Progress')
        self.assertEqual(self.task.progress, 1)

    # test when the progress is updated to 100 the column is "Completed"
    def test_task_progress_update_to_100(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-progress-update', args=[self.task.id]),
            {'progress': 100},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.column, 'Completed')
        self.assertEqual(self.task.progress, 100)

    # test when the progress is updated to 1 the column is "In Progress"
    def test_task_progress_update_to_1(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-progress-update', args=[self.task.id]),
            {'progress': 1},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.column, 'In Progress')
        self.assertEqual(self.task.progress, 1)

    # test when the task is moved to "To Do" the assignee is None and the progress is 0
    def test_task_progress_update_to_0(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-move', args=[self.task.id]),
            {'column': 'To Do'},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.column, 'To Do')
        self.assertEqual(self.task.progress, 0)
        self.assertIsNone(self.task.assignee)

    # test when the progress is updated to a number less than 1 the response is 400
    def test_task_progress_update_to_less_than_1(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-progress-update', args=[self.task.id]),
            {'progress': -1},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.task.column, 'To Do')
        self.assertEqual(self.task.progress, 0)

    # test when the progress is updated to a number greater than 100 the response is 400
    def test_task_progress_update_to_greater_than_100(self):
        self.task.assignee = self.user2
        self.task.save()
        response = self.client.patch(
            reverse('task-progress-update', args=[self.task.id]),
            {'progress': 101},
            format='json'
        )
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.task.column, 'To Do')
        self.assertEqual(self.task.progress, 0)

    # test only creator can delete the task
    def test_only_creator_can_delete_the_task(self):

        response = self.client.delete(
            reverse('task-detail', args=[self.task.id]),
            format='json'
        )
        self.assertNotEqual(response.status_code, 204)
        self.assertEqual(Task.objects.count(), 1)

    # test updating the task
    def test_updating_the_task(self):
        self.task2 = Task.objects.create(
            title='Test Task',
            description='Test Description',
            creator=self.user,
        )
        self.task2.refresh_from_db()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        response = self.client.patch(
            reverse('task-detail', args=[self.task2.id]),
            {'title': 'Updated Task', 'description': 'Updated Description'},
            format='json'
        )
        self.task2.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task2.title, 'Updated Task')
        self.assertEqual(self.task2.description, 'Updated Description')

    # test only the creator can update the task
    def test_only_the_creator_can_update_the_task(self):

        response = self.client.patch(
            reverse('task-detail', args=[self.task.id]),
            {'title': 'Updated Task', 'description': 'Updated Description'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'Test Description')

    # test that creator of a task cannot assign the task to another user
    def test_creator_cannot_assign_the_task_to_another_user(self):
        response = self.client.patch(
            reverse('task-detail', args=[self.task.id]),
            {'assignee': self.user2.id},
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.task.assignee, None)
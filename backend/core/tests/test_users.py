
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth.models import User


class UserCreationTestCase(APITestCase):
    def test_user_creation(self):
        response = self.client.post(
            reverse('register'),
            {'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
        self.assertTrue(User.objects.first().check_password('testpassword'))

    #test user creation requires a username and a password
    def test_user_creation_requires_a_username_and_a_password(self):
        response = self.client.post(
            reverse('register'),
            {'username': 'testuser'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['password'], ['This field is required.'])

    #test user creation requires a unique username
    def test_user_creation_requires_a_unique_username(self):
        User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        response = self.client.post(
            reverse('register'),
            {'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
        self.assertTrue(User.objects.first().check_password('testpassword'))

    #test authenticated user can obtain a token
    def test_authenticated_user_can_obtain_a_token(self):
        User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.token = Token.objects.create(user=User.objects.first())
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        response = self.client.post(
            reverse('api-token-auth'),
            {'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token'], Token.objects.first().key)

    #test unauthenticated user cannot obtain a token
    def test_unauthenticated_user_cannot_obtain_a_token(self):

        response = self.client.post(
            reverse('api-token-auth'),
            {'username': 'testuser', 'password': 'testpassword'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    #test authenticated user can logout
    def test_authenticated_user_can_logout(self):
        User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.token = Token.objects.create(user=User.objects.first())
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        response = self.client.post(
            reverse('logout'),
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'User logged out')
        self.assertEqual(Token.objects.count(), 0)

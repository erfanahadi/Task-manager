from django.urls import path
from .views import RegisterView, logoutView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='api-token-auth'),
    path('logout/', logoutView.as_view(), name='logout'),
]
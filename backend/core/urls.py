from django.urls import path
from .views import RegisterView, LogoutView, CustomObtainAuthToken


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomObtainAuthToken.as_view(), name='api-token-auth'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
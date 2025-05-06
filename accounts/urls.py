from django.urls import path
from . import views
from .views import custom_login, custom_logout,delete_account

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),  # Use custom_logout view
    path('delete-account/', delete_account, name='delete_account'),
]
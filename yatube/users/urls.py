from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordResetView, PasswordChangeView

from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(), name='password_reset'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view
        (template_name='users/password_change_form.html'),
        name='password_change'
    ),
]

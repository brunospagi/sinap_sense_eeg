# projeto/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from analysis.views import CustomLoginView, register

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticação
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register, name='register'),
    
    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'), 
        name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), 
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), 
        name='password_reset_complete'),
    
    # App Analysis
    path('', include('analysis.urls', namespace='analysis')),
]
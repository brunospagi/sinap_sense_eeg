# analysis/urls.py
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('upload/', views.upload_eeg, name='upload'),
    path('dashboard/<int:eeg_id>/', views.dashboard, name='dashboard'),
    path('channel/<int:channel_id>/', views.channel_detail, name='channel_detail'),
    path('update-topomap/', views.update_topomap, name='update_topomap'),
    path('eeg-list/', views.EEGList.as_view(), name='eeg_list'),
]
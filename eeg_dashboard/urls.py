from django.contrib import admin
from django.urls import path
from analysis import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_eeg, name='upload'),
    path('dashboard/<int:eeg_id>/', views.dashboard, name='dashboard'),
    path('channel/<int:channel_id>/', views.channel_detail, name='channel_detail'),
    path('update-topomap/', views.update_topomap, name='update_topomap'),

]
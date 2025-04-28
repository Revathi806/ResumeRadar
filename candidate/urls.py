from django.urls import path
from . import views

app_name = 'candidate' 
urlpatterns = [
    path('candidate-dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),  # Must match exactly
    path('apply-job/', views.apply_job, name='apply_job'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('applied-jobs/', views.applied_jobs, name='applied-jobs'),
    path('delete-notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]
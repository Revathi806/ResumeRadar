from django.urls import path
from . import views
app_name = 'HR'
urlpatterns = [
    path('', views.hr_dashboard, name='hr_dashboard'),  # Make this the home
    path('upload-resumes/', views.upload_resumes, name='upload_resumes'),
    path('create-job/', views.create_job, name='create_job'),
    
    path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('job-list/', views.job_list, name='job_list'),
    path('delete_job/<int:id>/', views.delete_job, name='delete_job'),
    path('selected-applicants/', views.view_selected_applicants, name='view_selected_applicants'),
    path('delete-all-rejected/', views.delete_all_rejected, name='delete_all_rejected'),
    path('save-delete-selected/', views.save_delete_selected, name='save_delete_selected'),
    path('received-applications/', views.received_applications, name='received_applications'),
    path('auto_evaluate_applications/', views.auto_evaluate_applications, name='auto_evaluate_applications'),
    path('settings/', views.settings_page, name='settings'),
    path('update_application_status/', views.update_application_status, name='update_application_status'),
    path('logout/', views.logout_view, name='logout'),
    path('applications/', views.received_applications, name='received_applications'),
    path('applications/update-status/', views.update_application_status, name='update_application_status'),
    path('applications/notify-selected/', views.notify_selected, name='notify_selected'),
    path('applications/notify-rejected/', views.notify_rejected, name='notify_rejected'),
    path('applications/delete/<int:app_id>/', views.delete_application, name='delete_application'),
]
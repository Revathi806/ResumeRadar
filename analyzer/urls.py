from django.urls import path
from .views import IndexView, home, analyze_for_job
app_name = 'analyzer'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
   
    path('home/', home, name='home'),
    path('analyze/<int:job_id>/', analyze_for_job, name='analyze_for_job'),
   
]
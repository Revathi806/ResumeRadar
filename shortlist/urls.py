from django.contrib import admin
from django.urls import path
from shortlist import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('get-job-keywords/', views.get_job_keywords, name='get_job_keywords'),
]
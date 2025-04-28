from django.db import models
from django.conf import settings
# Create your models here.
from django.db import models

from HR.models import Job

class Resume_shortlist(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    name = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    ats_score = models.FloatField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.job.title} ({self.ats_score}%)"
    

class ApplicationShortlist(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shortlisted_applications'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='shortlisted_applications',
    )
    job_role = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    resume_file = models.FileField(upload_to='applications_shortlist/resumes/')
    overall_score = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s shortlisted application #{self.id} for {self.job_role} (Status: {self.get_status_display()})"
from django.db import models
from django.contrib.auth import get_user_model  # Add this import
from django.conf import settings
# Get the User model
from django.core.exceptions import ValidationError
User = get_user_model()

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # This associates each job with a user
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=100, choices=JOB_TYPE_CHOICES)
    job_description = models.TextField()
    keywords = models.CharField(max_length=255, help_text="Comma-separated keywords")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"




class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    job_role = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    resume_file = models.FileField(upload_to='applications/resumes/')
    overall_score = models.FloatField(default=0.0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'job')  # Prevent duplicate applications

    def __str__(self):
        return f"{self.user.username}'s application for {self.job_role} (Status: {self.get_status_display()})"
    
    
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
        
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()
    
    @classmethod
    def create_notification(cls, user, message, application=None):
        """Helper method to create a notification"""
        return cls.objects.create(
            user=user,
            message=message,
            application=application
        )
    
class SelectedApplicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='selected_resumes/')
    overall_score = models.FloatField()
    status = models.CharField(max_length=20, default='selected')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job.job_title}"
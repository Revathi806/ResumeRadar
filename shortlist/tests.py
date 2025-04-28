from django.test import TestCase

# Create your tests here.
from django.db import models


class Job_shortlist(models.Model):
    title = models.CharField(max_length=200)
    keywords = models.TextField(help_text="Comma-separated keywords for this job")
    
    def __str__(self):
        return self.title

class Resume(models.Model):
    job = models.ForeignKey(Job_shortlist, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    name = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    ats_score = models.FloatField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.job.title} ({self.ats_score}%)"
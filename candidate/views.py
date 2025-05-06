from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from datetime import datetime
from django.http import JsonResponse
import json
from HR.models import Job
from HR.models import Application
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from HR.models import Notification  


@login_required
def candidate_dashboard(request):
    
    # Get all active job listings
    job_listings = Job.objects.all()

    
    # Get unique companies for the filter dropdown
    unique_companies = Job.objects.values_list('company_name', flat=True).distinct()
    
    # Get user's applications with related job data
    my_applications = Application.objects.filter(
        user=request.user
    ).select_related('job').order_by('-created_at')
    
    # Get notification data
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]

    context = {
        'user': request.user,
        'job_listings': job_listings,
        'unique_companies': unique_companies,
        'my_applications': my_applications,
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'candidate/candidates_dashboard.html', context)
    
    
logger = logging.getLogger(__name__)

from shortlist.models import Resume_shortlist 

def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        try:
            resume_file = request.FILES['resume']
            job_id = request.POST.get('job_id')
            user = request.user
            
            
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Job not found'})
            
            
            resume = Resume_shortlist(
                job=job,
                user=user,  
                file=resume_file,
                description=f"Resume for {job.job_title} uploaded by {user.username}"
            )
            resume.save()
            
            
            application = Application(
                user=user,
                job=job,
                job_role=job.job_title,
                resume_file=resume.file,  
                description=f"Application for {job.job_title} at {job.company_name}",
                status='pending'
            )
            application.save()
            
            return JsonResponse({
                'success': True,
                'resume_id': resume.id,
                'application_id': application.id,
                'file_url': resume.file.url
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
def apply_job(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_id = data.get('job_id')
            user = request.user
            
            if not job_id:
                return JsonResponse({'success': False, 'error': 'Job ID missing'})
            
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Job not found'})
            
            
            resume = Resume_shortlist.objects.filter(job=job, file__isnull=False).order_by('-uploaded_at').first()
            if not resume:
                return JsonResponse({'success': False, 'error': 'No resume uploaded for this job'})
            
            
            Application.objects.create(
                user=user,
                job=job,
                resume_file=resume.file.url,
                job_role=job.job_title,
                status='pending'
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, "Notification deleted successfully.")
    return redirect('candidate_dashboard')

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success', 'count': updated})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def applied_jobs(request):
    applications = Application.objects.filter(user=request.user)
    context = {'applications': applications}
    return render(request, 'candidate/applied_jobs.html', context)
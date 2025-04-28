from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Job
from .forms import JobForm 
from shortlist.models import Resume_shortlist
from .forms import ResumeUploadForm
from .models import Application,Notification, SelectedApplicant
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from shortlist.models import ApplicationShortlist
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from HR.models import Application
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import logout
@login_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user  
            job.save()
            return redirect('HR:job_list')
    else:
        form = JobForm()
    return render(request, 'HR/create_job.html', {'form': form})

@login_required
def hr_dashboard(request):
    total_jobs = Job.objects.count()
    total_applicants = Application.objects.count()
    ai_matches = Application.objects.filter(status='accepted').count() 

    context = {
        'job_count': total_jobs,
        'application_count': total_applicants,
        'selected_count': ai_matches,
    }
    return render(request, 'HR/hr_dashboard.html', context)

@login_required
def job_list(request):
    jobs = Job.objects.filter(user=request.user)
    return render(request, 'HR/job_list.html', {'jobs': jobs})


def delete_job(request, id):  
    job = get_object_or_404(Job, id=id)
    job.delete()
    return redirect('job_list')

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('HR:job_list')
    else:
        form = JobForm(instance=job)
    return render(request, 'HR/edit_job.html', {'form': form, 'job': job})



def upload_resumes(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('hr_dashboard')
    else:
        form = ResumeUploadForm()
    return render(request, 'HR/upload_resumes.html', {'form': form})

@login_required
def settings_page(request):
    return render(request, 'HR/settings.html')



@login_required
def received_applications(request):
    
    applications = Application.objects.filter(job__user=request.user)
    shortlisted_applications = ApplicationShortlist.objects.filter(job__user=request.user)
    
    if request.method == 'POST':
        
        for app in applications:
            new_status = request.POST.get(f'status_{app.id}')
            if new_status and new_status != app.status:
                app.status = new_status
                app.save()
                create_notification(app, new_status)
        
       
        for app in shortlisted_applications:
            new_status = request.POST.get(f'shortlist_status_{app.id}')
            if new_status and new_status != app.status:
                app.status = new_status
                app.save()
                create_notification(app, new_status)
        
        messages.success(request, "Statuses updated successfully!")
        return redirect('HR:received_applications')
    
   
    selected_applications = list(applications.filter(status='accepted')) + \
                          list(shortlisted_applications.filter(status='accepted'))
   
    rejected_applications = list(applications.filter(status='rejected')) + \
                          list(shortlisted_applications.filter(status='rejected'))
    
    selected_count = len(selected_applications)
    rejected_count = len(rejected_applications)
    
    context = {
        'applications': applications,
        'shortlisted_applications': shortlisted_applications,
        'selected_applications': selected_applications,
        'rejected_applications': rejected_applications,
        'selected_count': selected_count,
        'rejected_count': rejected_count
    }
    return render(request, 'HR/received_applications.html', context)

def create_notification(application, new_status):
    message = (
        f"Your application for '{application.job.job_title}' has been {new_status.lower()}."
        if new_status == 'accepted' else
        f"Your application for '{application.job.job_title}' was not successful."
    )
    Notification.objects.create(user=application.user, message=message)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt  
@require_POST
def update_application_status(request):
    if request.method == 'POST':
       
        for key, value in request.POST.items():
            if key.startswith('status_'):
                app_id = key.split('_')[1]
                try:
                    app = Application.objects.get(id=app_id)
                    app.status = value
                    app.save()
                except Application.DoesNotExist:
                    try:
                        
                        app = ApplicationShortlist.objects.get(id=app_id)
                        app.status = value
                        app.save()
                    except ApplicationShortlist.DoesNotExist:
                        pass
        
        
        for key, value in request.POST.items():
            if key.startswith('shortlist_status_'):
                app_id = key.split('_')[2]
                try:
                    app = ApplicationShortlist.objects.get(id=app_id)
                    app.status = value
                    app.save()
                except ApplicationShortlist.DoesNotExist:
                    try:
                        
                        app = Application.objects.get(id=app_id)
                        app.status = value
                        app.save()
                    except Application.DoesNotExist:
                        pass
        
        messages.success(request, 'Application statuses updated successfully!')
        return redirect('HR:received_applications')
@login_required
def upload_resumes(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('hr_dashboard')
    else:
        form = ResumeUploadForm()
    
    jobs = Job.objects.all()  
    return render(request, 'HR/upload_resumes.html', {'form': form, 'jobs': jobs})
@csrf_exempt
@require_POST
def auto_evaluate_applications(request):
    try:
        
        pending_apps = Application.objects.filter(
            job__user=request.user,
            status='pending'
        )
        
        updated_count = 0
        
        for app in pending_apps:
            
            if app.overall_score >= 70:
                app.status = 'accepted'
            else:
                app.status = 'rejected'
            app.save()
            updated_count += 1
            
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)





def logout_view(request):
    logout(request)  
    return render(request, 'accounts/login.html')  
from django.contrib import messages

from django.contrib import messages

def notify_selected(request):
    if request.method == 'POST':
        selected_apps = Application.objects.filter(status='accepted')
        
        for app in selected_apps:
            subject = f"Application Update for {app.job.job_title}"
            message = (
                f"Dear {app.user.username},\n\n"
                f"We are pleased to inform you that your application for the position of "
                f"{app.job.job_title} has been selected for the next stage of our hiring process.\n\n"
                f"We will contact you shortly with further details.\n\n"
                f"Best regards,\n"
                f"HR Team"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [app.user.email],
                fail_silently=False,
            )
        
        messages.success(request, f'Notification emails sent to {selected_apps.count()} selected candidates!')
        return redirect('HR:received_applications')
    
    return redirect('HR:received_applications')

def notify_rejected(request):
    if request.method == 'POST':
        rejected_apps = Application.objects.filter(status='rejected')
        
        for app in rejected_apps:
            subject = f"Application Update for {app.job.job_title}"
            message = (
                f"Dear {app.user.username},\n\n"
                f"Thank you for your interest in the {app.job.job_title} position at our company.\n\n"
                f"After careful consideration, we regret to inform you that we have decided to "
                f"pursue other candidates whose qualifications more closely match our requirements "
                f"for this particular role.\n\n"
                f"We appreciate the time and effort you invested in your application and encourage "
                f"you to apply for future openings that may be a better fit for your skills and experience.\n\n"
                f"Best regards,\n"
                f"HR Team"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [app.user.email],
                fail_silently=False,
            )
        
        messages.success(request, f'Notification emails sent to  rejected candidates!')
        return redirect('HR:received_applications')
    
    return redirect('HR:received_applications')
def delete_application(request, app_id):
    if request.method == 'GET':
        application = get_object_or_404(Application, id=app_id)
        application.delete()
        messages.success(request, "Application deleted successfully!")
    return redirect('received_applications')


@login_required
def save_delete_selected(request):
    if request.method == 'POST':
        selected_apps = Application.objects.filter(job__user=request.user, status='accepted')
        shortlisted_selected = ApplicationShortlist.objects.filter(job__user=request.user, status='accepted')
        
        for app in selected_apps:
            SelectedApplicant.objects.create(
                user=app.user,
                job=app.job,
                resume_file=app.resume_file,
                overall_score=app.overall_score,
                status='selected'
            )
            app.delete()
        
        for app in shortlisted_selected:
            SelectedApplicant.objects.create(
                user=app.user,
                job=app.job,
                resume_file=app.resume_file,
                overall_score=app.overall_score,
                status='selected'
            )
            app.delete()
        
        messages.success(request, "Selected applicants saved and removed from current list!")
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def delete_all_rejected(request):
    if request.method == 'POST':
        rejected_apps = Application.objects.filter(job__user=request.user, status='rejected')
        shortlisted_rejected = ApplicationShortlist.objects.filter(job__user=request.user, status='rejected')
        
        count = rejected_apps.count() + shortlisted_rejected.count()
        rejected_apps.delete()
        shortlisted_rejected.delete()
        
        messages.success(request, f"Deleted {count} rejected applications!")
        return JsonResponse({'success': True, 'deleted_count': count})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def view_selected_applicants(request):
    selected_applicants = SelectedApplicant.objects.filter(job__user=request.user).order_by('job__id')
    
    
    jobs = {}
    for applicant in selected_applicants:
        job_id = applicant.job.id
        if job_id not in jobs:
            jobs[job_id] = {
                'job_title': applicant.job.job_title,
                'applicants': []
            }
        jobs[job_id]['applicants'].append(applicant)
    
    context = {
        'grouped_applicants': jobs
    }
    return render(request, 'HR/view_selected_applicants.html', context)
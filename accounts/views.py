from django.shortcuts import render

# Create your views here.



from django.contrib import messages
'''new'''
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse

'''new'''
from django.contrib.auth.views import LoginView


from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from .forms import UserRegistrationForm
from .models import User



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return JsonResponse({'success': True, 'redirect_url': reverse('login')})  
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def home(request):
    return render(request, 'accounts/home.html')

def logout_view(request):
    logout(request)
    return redirect('login')
'''new function'''



def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            
            if user.user_type == 'Candidate':
                return redirect('candidate:candidate_dashboard')  
            elif user.user_type == 'HR':
                return redirect('HR:hr_dashboard')
            else:
                return redirect('home')
        else:
            
            return render(request, 'accounts/login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'accounts/login.html')

class CustomLoginView(LoginView):
    def get_success_url(self):
        
        user = self.request.user

        
        if user.user_type == 'Candidate':
            return reverse('candidate_dashboard')  
        elif user.user_type == 'HR':
            return reverse('base')  

       
        return reverse('home')
    
def custom_logout(request):
    logout(request)  
    messages.success(request, 'You have been logged out successfully.')  
    return redirect('login') 
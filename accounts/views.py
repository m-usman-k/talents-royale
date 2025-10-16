from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from .forms import SignupForm, LoginForm, UserSettingsForm, PasswordChangeForm, DeleteAccountForm
from .models import CustomUser


def home_view(request):
    return render(request, "home.html")

def arenas_view(request):
    return render(request, "arenas.html")

def contestants_view(request):
    return render(request, "contestants.html")

def howitworks_view(request):
    return render(request, "how-it-works.html")

def finaleroyale_view(request):
    return render(request, "finale-royale.html")

@login_required(login_url='/login')
def profile_view(request):
    settings_form = UserSettingsForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    delete_form = DeleteAccountForm(request.user)
    
    if request.method == 'POST':
        if 'update_settings' in request.POST:
            settings_form = UserSettingsForm(request.POST, instance=request.user)
            if settings_form.is_valid():
                user = settings_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password1']
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully! Please log in again.')
                return redirect('login')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif 'delete_account' in request.POST:
            delete_form = DeleteAccountForm(request.user, request.POST)
            if delete_form.is_valid():
                # Send goodbye email before deletion
                try:
                    send_mail(
                        'Account Deleted - Talents Royale',
                        f'Hello {request.user.username},\n\nYour Talents Royale account has been successfully deleted.\n\nWe\'re sorry to see you go! If you change your mind, you\'re always welcome to create a new account.\n\nBest regards,\nThe Talents Royale Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass  # Continue with deletion even if email fails
                
                username = request.user.username
                request.user.delete()
                messages.success(request, f'Account for {username} has been permanently deleted.')
                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
    
    context = {
        'settings_form': settings_form,
        'password_form': password_form,
        'delete_form': delete_form,
    }
    
    return render(request, "profile.html", context)

def signin_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to next page if specified, otherwise to profile
            next_page = request.GET.get('next', 'profile')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, "signin.html", {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login on signup; no email verification
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    
    return render(request, "signup.html", {'form': form})

## Email verification removed per request; confirmation and resend endpoints deleted

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

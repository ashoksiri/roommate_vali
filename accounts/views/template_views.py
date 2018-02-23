from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate , logout
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from ..models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from datetime import datetime
import logging

log = logging.getLogger(__name__)


from oauth2_provider.models import Application


@receiver(user_logged_in)
def call_user_status(sender, user, request, **kwargs):

    if user.is_active:
        application = Application.objects.filter(user=user).first()
        if not application:
            Application.objects.create(user=user,
                                   client_type=Application.CLIENT_CONFIDENTIAL,
                                   authorization_grant_type=Application.GRANT_PASSWORD,
                                   name=user.email)

@login_required
def home(request):
    return render(request, 'home.html')


def login_view(request):
    
    if request.user.is_authenticated():
        return redirect('home')

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                return render(request,'login.html',{'warning':'Your acoount is Inactive'})
        else:
            return render(request,'login.html',{'error':'Invalid Username Or Password..'})

    return render(request,'login.html')


def register_view(request):

    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_data = {}
            user_data['username'] = email
            user_data['email'] = email
            user_data['password'] = password
            User.objects._create_user(**user_data)
            user = authenticate(username=email,password=password)
            if user:
                login(request, user)
                return redirect('home')
        except:
            return render(request, 'login.html', {'register': True, 'error': 'user already exists ...'})

def logout_view(request):
    logout(request)
    return redirect('login')
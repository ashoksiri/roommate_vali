from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate , logout
from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token
from django.http.response import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from datetime import datetime

# @receiver(user_logged_in)
# def call_user_status(sender, user, request, **kwargs):
#     if not user.last_login:
#         user.last_login = datetime.now()
#         user.save()

from rest_framework.viewsets import ModelViewSet

@login_required
def home(request):
    return render(request, 'home.html',
                  {'page':1})


@login_required
def profile(request):
    return render(request, 'roommate/profile.html',{'page':4})

@login_required
def mail(request):
   
    return render(request, 'roommate/mail.html',{'page':3})

@login_required
def analysis(request):
    
    return render(request, 'roommate/charts.html',{'page':2})



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


# def register(request):
#
#     if request.user.is_authenticated():
#         return redirect('home')
#
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             user.refresh_from_db()  # load the profile instance created by the signal
#             user.profile.birth_date = form.cleaned_data.get('birth_date')
#             user.save()
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=user.username, password=raw_password)
#             login(request, user)
#             return redirect('home')
#     else:
#         form = SignUpForm()
#     return render(request, 'roommate/register.html', {'form': form})

def register(request):

    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_data = {}
            user_data['username'] = email
            user_data['email'] = email
            user_data['password'] = password
            User._default_manager.db_manager().create_user(**user_data)
            user = authenticate(username=email,password=password)
            if user:
                return render(request,'home.html')

        except:
            return render(request, 'login.html', {'register': True, 'error': 'user already exists ...'})



        # try:
        #     user_data = {}
        #     user_data['username'] = request.data.get('username')
        #     user_data['email'] = request.data.get('username')
        #     user_data['password'] = request.data.get('password1')
        #     User._default_manager.db_manager().create_user(**user_data)
        # except:
        #     context = {
        #         'error':'username already exists'
        #     }
        #     return render(request,'login.html',context)
        #
        # return render('home.html',context= {"status_code": 201, "status_message": "User {} Created Successfully".format(email)})

    return render(request,'login.html',{'register':True})

def logout_view(request):
    logout(request)
    return redirect('login')
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate , logout
from django.shortcuts import render, redirect
from django.http import *
from accounts.forms import SignUpForm,LoginForm
from rest_framework.authtoken.models import Token
from django.http.response import JsonResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes,authentication_classes

@login_required
def home(request):
    return render(request, 'home.html',{'page':1})

@login_required
@permission_classes((IsAuthenticated,))
def get_access_token(request):
    token = Token.objects.get(user=request.user)
    return JsonResponse({'access_key':token.key})


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
        
    username = password = ''
    context = {
        'form':LoginForm(),
        'title':'RoomMate'
    }
    
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                d = login(request, user)
                try:
                    token = Token.objects.get(user=user)
                except :
                    token = Token.objects.create(user=user)
                    print(token)
                return redirect('home')
            else:
                context.update({'warning':'Your acoount is Inactive'})
                return render(request,'roommate/login.html',context) 
        else:
            context.update({'error':'Invalid Username Or Password..'})
            return render(request,'roommate/login.html',context)        

    return render(request,'roommate/login.html',context)


def register(request):
    
    if request.user.is_authenticated():
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'roommate/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView ,ListCreateAPIView
from ..serializers import ProfileSerializer,Profile
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from rest_framework import  status
from oauth2_provider.models import Application
from django.shortcuts import render , redirect

import logging

log = logging.getLogger(__name__)


class UsersView(ListCreateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = AllowAny,

    def list(self, request, *args, **kwargs):
        return render(request,'login.html',{'register':True})

    def create(self, request, *args, **kwargs):

        email = request.data.get('username')

        try:
            user_data = {}
            user_data['username'] = request.data.get('username')
            user_data['email'] = request.data.get('username')
            user_data['password'] = request.data.get('password')
            User._default_manager.db_manager().create_user(**user_data)
            user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
            print(user)
        except :
            return render(request, 'login.html', {'register': True,'error':'user already exists ...'})

        return redirect('home')


class LoginView(CreateAPIView):

    permission_classes = AllowAny,
    serializer_class = ProfileSerializer


    def create(self, request, *args, **kwargs):

        username = request.data['email']
        password = request.data['password']

        user = authenticate(email=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # return Response ("LOGGED")
            else:
                data = {"status_code": 400, "status_message": "BAD REQUEST", "error": "User is Blocked"}
                return Response(data=data,status=status.HTTP_400_BAD_REQUEST,template_name='login.html')
        else:
            data = {"status_code": 400, "status_message": "BAD REQUEST", "error": "Invalid Username or Password"}
            return Response(data=data,status=status.HTTP_400_BAD_REQUEST,template_name='login.html')

        user = self.request.user
        a = None
        try:
            a = Application.objects.get(user=user)
        except ObjectDoesNotExist:
            a = Application.objects.create(user=user,
                                           client_type=Application.CLIENT_CONFIDENTIAL,
                                           authorization_grant_type=Application.GRANT_PASSWORD,
                                           name=user.username)

        data= {}
        data['username'] = user.email
        data['user_id'] = user.id
        data['grant_type'] = Application.GRANT_PASSWORD
        data['client_id'] = a.client_id
        data['client_secret'] = a.client_secret
        data['statuc_code'] = 200
        data['user_type'] = 'admin' if user.is_staff else 'user'

        return Response(data=data,status=status.HTTP_200_OK)




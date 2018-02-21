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


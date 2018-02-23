
from .template_views import *
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_framework.generics import CreateAPIView ,ListCreateAPIView
from ..serializers import ProfileSerializer,Profile
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import  status
from ..models import User,Profile

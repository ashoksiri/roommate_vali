from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from ..serializers import ProfileSerializer,Profile
from rest_framework.response import Response
from django.contrib.auth.models import User

class UsersView(CreateAPIView):

    serializer_class = ProfileSerializer

    def create(self, request, *args, **kwargs):

        email = request.data.get('username')

        try:
            user_data = {}
            user_data['username'] = request.data.get('username')
            user_data['email'] = request.data.get('username')
            user_data['password'] = request.data.get('password1')
            User._default_manager.db_manager().create_user(**user_data)
        except :
            return Response({"response": {"status_code": 400, "status_message": "User Already Exists"}})

        return Response({"response": {"status_code": 201, "status_message": "User Created Successfully"}})







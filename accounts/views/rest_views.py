
from ..views import *

import logging

log = logging.getLogger(__name__)


class RegisterView(CreateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = AllowAny,

    def create(self, request, *args, **kwargs):

        email = request.data.get('email')
        password = request.data.get('password')

        print(email,password)

        try:
            User.objects.get(email=email)
            return Response(data={'status_message':'user name already exists ...'},status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist :
            User.objects._create_user(email=email,password=password)
            return Response(data={'status_message': 'User created Successfully'}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(data={'status_message': 'some thing went wrong'}, status=2000)


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
                data = {"status_code": 400, "status_message": "User is Blocked"}
                return Response(data=data,status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {"status_code": 400,"status_message": "invalid username or password"}
            return Response(data=data,status=status.HTTP_400_BAD_REQUEST)

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
        data['status_code'] = 200
        data['user_type'] = 'admin' if user.is_staff else 'user'

        return Response(data=data,status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class RevokeTokenView(OAuthLibMixin, View):
    """
    Implements an endpoint to revoke access or refresh tokens
    """
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS
    permissions_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        logout(request)
        url, headers, body, status = self.create_revocation_response(request)

        response = {"status_message": "logged out successfully"}
        #
        for k, v in headers.items():
            response[k] = v

        return JsonResponse(data=response, safe=False)

# api/authentication.py

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import CustomToken

class CustomTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            token = CustomToken.objects.get(key=key)
        except CustomToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if token.is_expired():
            raise AuthenticationFailed('Token has expired.')

        return (token.user, token)

from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class UsuarioBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .voice_utils.voice_validation import is_valid_voice_for_user

class UsernameEmailOnlyAuthBackend(ModelBackend):
    
    #Authenticate the user using his email or username
    def authenticate(self, request=None, username=None,email = None, audio_file=None,**kwargs):
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        elif email and (user is None):
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return None
        try: 
            if not is_valid_voice_for_user(user,audio_file):
                return None
            else:
                user.statement.delete()
        except Exception as ex:
            print(ex)
            return None
        return user

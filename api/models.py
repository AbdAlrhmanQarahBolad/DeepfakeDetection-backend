from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

def deactivate_user(user_id,is_active):
    """
    Deactivate a user by setting their is_active status to False.

    Args:
        user_id (int): The ID of the user to deactivate.

    Raises:
        User.DoesNotExist: If no user with the given ID exists.
    """
    try:
        user = User.objects.get(id=user_id)
        user.is_active = is_active
        user.save()
    except User.DoesNotExist:
        raise ObjectDoesNotExist(f"No user found with ID {user_id}.")
    

class UserVoice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voice')
    filename = models.CharField(max_length=255,unique=True)
    
    def __str__(self):
        return self.filename
    
class UserStatement(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statement')
    words = models.CharField(max_length=255)
    
    

class CallStatus(models.IntegerChoices):
    CREATED = 0, 'Created'
    RUNNING = 1, 'Running'
    CLOSED = 2, 'Closed'

class FakeStatus(models.IntegerChoices):
    REAL = 0, 'Real'
    FAKE = 1, 'Fake'
    

class Call(models.Model):
    caller = models.ForeignKey(User, related_name='caller_calls', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient_calls', on_delete=models.CASCADE)
    status = models.IntegerField(choices=CallStatus.choices, default=CallStatus.CREATED)
    caller_status = models.IntegerField(choices=FakeStatus.choices, default=FakeStatus.REAL)
    recipient_status = models.IntegerField(choices=FakeStatus.choices, default=FakeStatus.FAKE)
    
class DeepAudioArchive(models.Model):
    call = models.ForeignKey(Call, related_name="deep_audio_archive",on_delete=models.CASCADE)
    filename = models.CharField(max_length=1000)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='deep_audio_archive')

def get_user_via_identifier(identifier:str):
    if User.objects.filter(email = identifier.strip().lower()).exists():
        return User.objects.filter(email = identifier.strip().lower()).get()
    if User.objects.filter(username = identifier).exists():
        return User.objects.filter(username = identifier).get()
    raise User.DoesNotExist(f"User doesn't exist!")    


def get_fake_status_name(value:int):
    return (dict(FakeStatus.choices))[value]
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

def deactivate_user(user_id,is_active):
    """
    Deactivate a user by setting their is_active status to False.

    Args:
        user_id (int): The ID of the user to deactivate.

    Raises:
        User.DoesNotExist: If no user with the given ID exists.
    """
    try:
        user = User.objects.get(id=user_id)
        user.is_active = is_active
        user.save()
    except User.DoesNotExist:
        raise ObjectDoesNotExist(f"No user found with ID {user_id}.")
    

class UserVoice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voice')
    filename = models.CharField(max_length=255,unique=True)
    
    def __str__(self):
        return self.filename
    
class UserStatement(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statement')
    words = models.CharField(max_length=255)
    
    

class CallStatus(models.IntegerChoices):
    CREATED = 0, 'Created'
    RUNNING = 1, 'Running'
    CLOSED = 2, 'Closed'

class FakeStatus(models.IntegerChoices):
    REAL = 0, 'Real'
    FAKE = 1, 'Fake'
    

class Call(models.Model):
    caller = models.ForeignKey(User, related_name='caller_calls', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient_calls', on_delete=models.CASCADE)
    status = models.IntegerField(choices=CallStatus.choices, default=CallStatus.CREATED)
    caller_status = models.IntegerField(choices=FakeStatus.choices, default=FakeStatus.REAL)
    recipient_status = models.IntegerField(choices=FakeStatus.choices, default=FakeStatus.FAKE)
    
class DeepAudioArchive(models.Model):
    call = models.ForeignKey(Call, related_name="deep_audio_archive",on_delete=models.CASCADE)
    filename = models.CharField(max_length=1000)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='deep_audio_archive')

def get_user_via_identifier(identifier:str):
    if User.objects.filter(email = identifier.strip().lower()).exists():
        return User.objects.filter(email = identifier.strip().lower()).get()
    if User.objects.filter(username = identifier).exists():
        return User.objects.filter(username = identifier).get()
    raise User.DoesNotExist(f"User doesn't exist!")    


def get_fake_status_name(value:int):
    return (dict(FakeStatus.choices))[value]
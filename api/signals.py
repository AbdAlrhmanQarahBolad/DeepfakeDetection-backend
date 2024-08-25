import os
from .models import DeepAudioArchive
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(signal=post_delete,sender = DeepAudioArchive)
def deep_audio_archive_post_delete(sender, instance, **kwargs):
    """_summary_
        deteles the audio file using the file path
    Args:
        sender (Model): _description_
        instance (DeepAudioArchive instance): the instance has been deleted from database
    """    
    try:
        os.remove(instance.filename)
    except FileNotFoundError:
        pass

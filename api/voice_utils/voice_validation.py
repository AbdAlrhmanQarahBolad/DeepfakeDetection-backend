import os
import magic
from django.core.exceptions import ValidationError
from .speech_recognition_utils import match_voice_statement
from rest_framework import serializers,status
from django.core.files.uploadedfile import InMemoryUploadedFile
import requests
from io import BytesIO
import json
from . import speaker_recognition_utils
import numpy as np
from .utils import save_file_into_temp_folder
from project2.settings import DEEPFAKE_DETECTION_MODEL_API_BASE_URL


def validate_is_audio_and_size(file: InMemoryUploadedFile, max_size_kb=1024 * 50):  # Default max size is 2MB
    mime_type_to_extension = {
        'audio/mpeg': '.mpg',
        'audio/mp3': '.mp3',
        'audio/wav': '.wav',
        'audio/aac': '.aac',
        'audio/ogg': '.ogg',
        'audio/m4a': '.m4a',
        'audio/x-wav': '.wav',
        'audio/flac': '.flac',  # Free Lossless Audio Codec
        'audio/oga': '.oga',   # Ogg Vorbis
        'audio/midi': '.mid',  # MIDI Audio Format
        'audio/wma': '.wma',   # Windows Media Audio
    }
    valid_file_extensions = []
    valid_mime_types = []
    
    for mime_type in mime_type_to_extension:
        valid_mime_types.append(mime_type)
        valid_file_extensions.append(mime_type_to_extension[mime_type])
        
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    
    file.seek(0)
    
    if file_mime_type not in valid_mime_types:
        print("file mime type: " + file_mime_type)
        raise ValidationError('Unsupported file type.')
    
    ext = os.path.splitext(file.name)[1].lower()
    if (ext not in valid_file_extensions) or (mime_type_to_extension[file_mime_type] != ext):
        raise ValidationError('Unacceptable file extension.')
    
    

    # Check file size
    if file.size > max_size_kb * 1024:  # Convert KB to bytes
        raise ValidationError(f'File size exceeds {max_size_kb} KB.')

def is_user_voice(user,file:InMemoryUploadedFile)->bool:
    file_path=save_file_into_temp_folder(file)
    
    known_embeddings = [speaker_recognition_utils.get_voice_embedding(speaker_recognition_utils.load_and_preprocess_wav(user.voice.filename))]
    test_embedding = speaker_recognition_utils.get_voice_embedding(speaker_recognition_utils.load_and_preprocess_wav(file_path))    
    best_match_idx, similarity = speaker_recognition_utils.recognize_speaker(known_embeddings, test_embedding)
    
    os.remove(file_path)
    
    if similarity<0.7 :
        return False
    return True

def is_valid_voice_for_user(user, file:InMemoryUploadedFile)->bool:
    statement:str = user.statement.words
    
    if not match_voice_statement(file,statement):
        raise serializers.ValidationError("words are not matching")

    return (not is_deep_fake_audio(file=file)) and (is_user_voice(user,file))
    



def is_deep_fake_audio(file:InMemoryUploadedFile):
    
    DEEPFAKE_DETECTION_API = DEEPFAKE_DETECTION_MODEL_API_BASE_URL + "predect"
    
    multipart_data = {
        'audio_file':(file.name,BytesIO(file.read()),file.content_type)
    }
    
    response = requests.post(DEEPFAKE_DETECTION_API, files=multipart_data)
    
    if response.status_code != status.HTTP_200_OK:
        return True
    data:dict = json.loads(response.text)[0]    
    
    
    message = data.get("detail","")+data.get("message","") + data.get("result")
    
    if "fake" in message:
        return True
    return False


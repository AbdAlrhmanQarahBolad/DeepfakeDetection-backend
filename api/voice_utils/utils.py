import os
import shutil
import uuid
from project2.settings import TEMP_FOLDER_PATH, PERMANENT_FOLDER_PATH

from django.core.files.uploadedfile import InMemoryUploadedFile

def make_unique_file_name(file:InMemoryUploadedFile,custom_extension = None):
    """
    Generates a unique file name for the given file object.
    """
    # Extract the original file name and extension from the InMemoryUploadedFile object
    original_name = file.name
    name, extension = os.path.splitext(original_name)
    if custom_extension is not None:
        extension = custom_extension
    # Generate a new unique file name
    unique_id = uuid.uuid4()  # Assuming you're using uuid for uniqueness
    new_name = f"{unique_id}{extension}"
    return new_name

def save_file_at_path(file:InMemoryUploadedFile, file_path):
    """
    Saves the given file at the specified file path.
    """
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the file at the specified path
    with open(file_path, 'wb') as out_file:
        shutil.copyfileobj(file, out_file)
        file.seek(0)



def save_file_into_temp_folder(file:InMemoryUploadedFile)->str:
    
    file_name = make_unique_file_name(file)
    file_abs_path = os.path.join(TEMP_FOLDER_PATH,file_name)
    save_file_at_path(file,file_abs_path)
    return file_abs_path

def save_file_into_permanent_folder(file:InMemoryUploadedFile)->str:
    
    file_name = make_unique_file_name(file)
    file_abs_path = os.path.join(PERMANENT_FOLDER_PATH,file_name)
    save_file_at_path(file,file_abs_path)
    return file_abs_path




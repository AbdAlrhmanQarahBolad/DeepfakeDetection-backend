import speech_recognition as sr
from pydub import AudioSegment
from .utils import save_file_into_temp_folder,make_unique_file_name
import os
import difflib



TRANSFORM = {
    'أ':'ا',
    'إ':'ا',
    'آ':'ا',
    'ة':'ه',
    'ي':'ى',
    'ئ':'ء',
    'ؤ':'و',
}
def standardize(word:str):
    for old_char in TRANSFORM:
        word = word.replace(old_char,TRANSFORM[old_char])
    return word

def equals(string1:str, string2:str):
    string1 = standardize(string1)
    string2 = standardize(string2)
    matcher = difflib.SequenceMatcher(None, string1, string2)
    similarity_ratio = matcher.ratio()
    return bool(similarity_ratio >= .80) #80% 


# Function to convert audio to WAV format if needed
def convert_to_wav(input_audio_path, output_wav_path):
    audio = AudioSegment.from_file(input_audio_path)
    audio.export(output_wav_path, format="wav")


def calculate_similarity_lists(original, recognized)->float:
    matches:int = 0
    start = 0
    for word in recognized:
        for index in range(start,len(original)):
            if equals(word,original[index]):
                start = index + 1
                matches += 1
    
    
    print(f"matched: {bool(matches/len(original) >= 0.8)}")
    return bool(matches/len(original) >= 0.8)


def recognize(file):
    # Path to your audio file
    audio_file_path = save_file_into_temp_folder(file)

    # Convert to WAV if the audio file is not in WAV format
    
    wav_file_path = make_unique_file_name(file,'.wav')
    if not audio_file_path.endswith(".wav"):
        convert_to_wav(audio_file_path, wav_file_path)
    else:
        wav_file_path = audio_file_path

    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Load audio file
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)

    # Recognize (convert from speech to text)
    try:
        text = recognizer.recognize_google(audio_data, language="ar-SA")
        print("Transcription: ", text)
    except sr.UnknownValueError:
        text = ""
        
    except sr.RequestError as e:
        text = ""
        
    
    for file_path in [wav_file_path,audio_file_path]:
        try:
            os.remove(file_path)
        except FileNotFoundError as ex:
            pass
    try:
        return text.split()
    except:
        return []
    
def match_voice_statement(file, statement:str):
    """
    Matches the statement and the voice file

    Parameters:
    file (InMemoryFile): the uploaded voice.
    statement (string): the statement stored for this user.

    Returns:
    True or False, depending on the file if it matches the registered statement
    """
    
    statement_list:list = statement.split()
    recognized_list:list = recognize(file)
    print(f"recognized: {recognized_list}")
    return calculate_similarity_lists(statement_list,recognized_list)
    
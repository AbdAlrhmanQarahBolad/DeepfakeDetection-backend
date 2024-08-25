from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np


def load_and_preprocess_wav(file_path):
    wav = preprocess_wav(file_path)
    return wav
encoder = VoiceEncoder()

def get_voice_embedding(wav):
    return encoder.embed_utterance(wav)
def cosine_similarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def recognize_speaker(known_embeddings, test_embedding):
    similarities = [cosine_similarity(test_embedding, known_emb) for known_emb in known_embeddings]
    best_match_idx = np.argmax(similarities)
    return best_match_idx, similarities[best_match_idx]

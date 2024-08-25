import random
import csv
import os

cwd = os.getcwd()
arabic_wordlist_csv_file_path = os.path.join(cwd,'static','api','static','arabic_words','arabic_wordlist.csv')
arabic_words = []
# Function to generate a random Arabic sentence
def generate_random_arabic_sentence(min_words=10, max_words=15):
    with open(arabic_wordlist_csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            for cell in row:
                arabic_words.append(cell)
    num_words = random.randint(min_words, max_words)
    
    sentence = ' '.join(random.choices(arabic_words, k=num_words))
    return sentence


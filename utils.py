import os
import re
import sys
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

def download_nltk_resources():
    """Ensure essential NLTK resources are available locally."""
    # Custom NLTK data path inside workspace to ensure portability and avoid write permission issues in system folders
    nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_dir)
        
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    for resource, path in [('corpora/stopwords', 'stopwords'), ('tokenizers/punkt', 'punkt'), ('tokenizers/punkt_tab', 'punkt_tab')]:
        try:
            nltk.data.find(resource)
        except LookupError:
            print(f"Downloading NLTK resource '{path}' to {nltk_data_dir}...")
            nltk.download(path, download_dir=nltk_data_dir, quiet=True)


# Download resources on import
download_nltk_resources()

class TextPreprocessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        # Keep standard English stopwords
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text):
        """
        Executes the required preprocessing pipeline:
        1. Clean/sanitize input text
        2. Remove URLs
        3. Remove Mentions (@user)
        4. Remove Hashtags (#topic)
        5. Remove Emojis
        6. Remove Punctuation
        7. Convert to lowercase
        8. Tokenization
        9. Stopword removal
        10. Porter Stemming
        """
        if not isinstance(text, str):
            return ""

        # 1. Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)

        # 2. Remove Mentions (@username)
        text = re.sub(r'@\w+', '', text)

        # 3. Remove Hashtags (#topic)
        text = re.sub(r'#\w+', '', text)

        # 4. Remove Emojis (removing high unicode characters and common emoji ranges)
        try:
            # Strip emojis using UTF-8 range matching
            text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
            # Remove other non-ASCII characters that might represent emojis/symbols
            text = text.encode('ascii', 'ignore').decode('ascii')
        except Exception:
            # Fallback to ascii replacement
            text = "".join(c for c in text if ord(c) < 128)

        # 5. Convert to lowercase
        text = text.lower()

        # 6. Remove Punctuation (replace with space to prevent sticking words together)
        text = re.sub(r'[^\w\s]', ' ', text)

        # 7. Tokenization
        tokens = word_tokenize(text)

        # 8. Remove stopwords and 9. Stemming
        processed_tokens = []
        for token in tokens:
            # Standard token cleanup (strip whitespaces)
            token = token.strip()
            if token and token not in self.stop_words:
                stemmed_token = self.stemmer.stem(token)
                if stemmed_token:
                    processed_tokens.append(stemmed_token)

        # Rejoin into space-separated string
        return " ".join(processed_tokens)

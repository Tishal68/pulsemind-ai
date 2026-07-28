import os
import sys

def print_dataset_missing_error():
    error_msg = f"""
======================================================================
ERROR: Dataset file 'dataset/twitter.csv' not found.
======================================================================
Please download a public sentiment dataset and place it at:
  dataset/twitter.csv

Recommended datasets (download and extract, then rename file to twitter.csv):
1. Sentiment140 Dataset (1.6 million records):
   URL: https://www.kaggle.com/datasets/kazanova/sentiment140
   - Rename 'training.1600000.processed.noemoticon.csv' to 'twitter.csv'

2. US Airline Sentiment Dataset:
   URL: https://www.kaggle.com/datasets/crowdflower/twitter-airline-sentiment
   - Rename 'Tweets.csv' to 'twitter.csv'

3. Kaggle Twitter Sentiment Dataset:
   URL: https://www.kaggle.com/datasets/jp797618/twitter-select-sentiment-dataset
   - Rename the main CSV file to 'twitter.csv'

Note: Ensure the CSV file contains text content and sentiment labels.
The script will automatically detect columns and map labels:
- Numeric labels: 0 -> Negative, 2 -> Neutral, 4 -> Positive
- Text labels: 'negative' -> Negative, 'neutral' -> Neutral, 'positive' -> Positive
======================================================================
"""
    print(error_msg, file=sys.stderr)

# --- CONFIGURATION ---
# If using a very large dataset (like Sentiment140 with 1.6M rows), preprocessing might take a long time.
# Set SAMPLE_SIZE to a number (e.g. 50000) to train on a subset, or None to use the entire dataset.
SAMPLE_SIZE = 50000
RANDOM_STATE = 42

def main():
    # Resolve paths relative to the script's actual directory rather than CWD
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(script_dir, "dataset")
    dataset_path = os.path.join(dataset_dir, "twitter.csv")
    
    # 1. Check if dataset exists
    if not os.path.exists(dataset_path):
        print_dataset_missing_error()
        sys.exit(1)

    # Delay imports until we confirm dataset exists to allow helpful error output even if dependencies are missing.
    print("Loading machine learning packages...")
    try:
        import time
        import joblib
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn import metrics
        from utils import TextPreprocessor
    except ImportError as e:
        print(f"\nERROR: Missing Python dependency: {e}", file=sys.stderr)
        print("Please install requirements using: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    print(f"Loading dataset from {dataset_path}...")

    
    # Try reading the dataset. Detect headers and format.
    try:
        # Check first line to see if we have headers
        first_line = ""
        with open(dataset_path, 'r', encoding='latin-1') as f:
            first_line = f.readline()
        
        # If Sentiment140 (no headers, 6 columns), we should read without headers
        # Sample Sentiment140 line: "0","1467810369","Mon Apr 06 22:19:45 PDT 2009","NO_QUERY","_TheSpecialOne_","@switchfoot http://..."
        cols = first_line.split(',')
        if len(cols) == 6 and not any(c.replace('"', '').isalpha() for c in cols):
            print("Detected raw Sentiment140 format (no header, 6 columns). Loading index-based columns...")
            df = pd.read_csv(dataset_path, header=None, encoding='latin-1')
            df.columns = ['target', 'id', 'date', 'flag', 'user', 'tweet']
            text_col = 'tweet'
            sentiment_col = 'target'
        else:
            df = pd.read_csv(dataset_path, encoding='latin-1')
            print(f"Loaded CSV. Columns: {list(df.columns)}")
            
            # Map common column names
            text_col = None
            for col in ['tweet', 'text', 'tweet_text', 'text_text', 'CleanText', 'selected_text', 'content']:
                if col.lower() in [c.lower() for c in df.columns]:
                    text_col = [c for c in df.columns if c.lower() == col.lower()][0]
                    break
            
            sentiment_col = None
            for col in ['sentiment', 'target', 'category', 'airline_sentiment', 'label', 'class']:
                if col.lower() in [c.lower() for c in df.columns]:
                    sentiment_col = [c for c in df.columns if c.lower() == col.lower()][0]
                    break
            
            if not text_col or not sentiment_col:
                # Fallback to column index 0 (sentiment/text) and 1 (text/sentiment) if column names don't match
                print("Could not auto-detect columns 'tweet' and 'sentiment'.")
                print("Defaulting: text = column 1, sentiment = column 0.")
                sentiment_col = df.columns[0]
                text_col = df.columns[1]
                
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
        
    print(f"Using text column: '{text_col}', sentiment column: '{sentiment_col}'")
    
    # Clean dataset to keep only text and sentiment columns, dropping NaNs
    df = df[[text_col, sentiment_col]].dropna()
    df.columns = ['tweet', 'sentiment']
    
    # 2. Standardize Sentiment Labels
    # Handle numeric mappings:
    # 0 -> Negative, 2 -> Neutral, 4 -> Positive
    # If 0 and 1 (binary classification), map 0 -> Negative, 1 -> Positive (or 0 -> Negative, 4 -> Positive)
    # Check unique values
    unique_vals = df['sentiment'].unique()
    print(f"Raw unique sentiment values: {unique_vals}")
    
    # Build a mapper
    label_map = {}
    for val in unique_vals:
        # Check numeric
        try:
            num_val = float(val)
            if num_val == 0.0:
                label_map[val] = "Negative"
            elif num_val == 2.0:
                label_map[val] = "Neutral"
            elif num_val == 4.0:
                label_map[val] = "Positive"
            elif num_val == 1.0:
                # If binary model has 0 and 1
                if len(unique_vals) == 2 and 0 in unique_vals:
                    label_map[val] = "Positive"
                else:
                    label_map[val] = "Neutral"
            else:
                label_map[val] = str(val)
        except ValueError:
            # Text values: standardise to Title Case
            str_val = str(val).strip().lower()
            if str_val in ['negative', 'neg', '0']:
                label_map[val] = "Negative"
            elif str_val in ['neutral', 'neut', '2']:
                label_map[val] = "Neutral"
            elif str_val in ['positive', 'pos', '4']:
                label_map[val] = "Positive"
            else:
                label_map[val] = str(val).capitalize()

    df['sentiment'] = df['sentiment'].map(label_map)
    
    # Filter to only keep Negative, Neutral, Positive (in case of garbage/other categories)
    df = df[df['sentiment'].isin(['Negative', 'Neutral', 'Positive'])]
    
    print(f"Standardized unique sentiment values: {df['sentiment'].value_counts().to_dict()}")
    
    # 3. Optional Sampling for speed
    if SAMPLE_SIZE and len(df) > SAMPLE_SIZE:
        print(f"Sampling dataset to {SAMPLE_SIZE} records for local training speed...")
        # Stratified sampling to preserve class distribution
        df = df.groupby('sentiment', group_keys=False).apply(
            lambda x: x.sample(min(len(x), SAMPLE_SIZE // len(df['sentiment'].unique())), random_state=RANDOM_STATE)
        )
        print(f"Sampled distribution: {df['sentiment'].value_counts().to_dict()}")

    # 4. Text Preprocessing
    print("Preprocessing text dataset. This might take a few minutes...")
    start_time = time.time()
    
    preprocessor = TextPreprocessor()
    df['cleaned_tweet'] = df['tweet'].apply(preprocessor.clean_text)
    
    # Drop rows that became empty after cleaning
    df = df[df['cleaned_tweet'].str.strip() != ""]
    
    print(f"Preprocessing completed in {time.time() - start_time:.2f} seconds. Total records remaining: {len(df)}")
    
    # 5. Train/Test Split
    X = df['cleaned_tweet']
    y = df['sentiment']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)
    
    # 6. TF-IDF Vectorization
    print("Vectorizing text using TF-IDF...")
    # Using ngram_range=(1, 2) to capture word combinations (e.g. "not good")
    vectorizer = TfidfVectorizer(max_features=15000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # 7. Model Training
    print("Training Logistic Regression model...")
    # C=1.0 is standard regularization. solver='lbfgs' is fast and supports multi-class classification
    model = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, C=1.0)
    model.fit(X_train_vec, y_train)
    
    # 8. Model Evaluation
    print("Evaluating model...")
    y_pred = model.predict(X_test_vec)
    
    accuracy = metrics.accuracy_score(y_test, y_pred)
    precision = metrics.precision_score(y_test, y_pred, average='weighted')
    recall = metrics.recall_score(y_test, y_pred, average='weighted')
    f1 = metrics.f1_score(y_test, y_pred, average='weighted')
    
    print("\n--- MODEL PERFORMANCE ---")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    print("\nClassification Report:")
    report_str = metrics.classification_report(y_test, y_pred)
    print(report_str)
    
    print("\nConfusion Matrix:")
    cm = metrics.confusion_matrix(y_test, y_pred, labels=model.classes_)
    print(cm)
    
    # Create evaluation directory and report
    reports_dir = os.path.join(script_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "evaluation.txt")
    with open(report_path, "w") as rf:
        rf.write("==================================================\n")
        rf.write("PulseMind AI - Model Evaluation Report\n")
        rf.write("==================================================\n")

        rf.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        rf.write(f"Dataset Size (Used): {len(df)}\n")
        rf.write(f"Train/Test Split: 80% / 20%\n")
        rf.write(f"Accuracy:  {accuracy:.4f}\n")
        rf.write(f"Precision: {precision:.4f}\n")
        rf.write(f"Recall:    {recall:.4f}\n")
        rf.write(f"F1 Score:  {f1:.4f}\n\n")
        rf.write("Classification Report:\n")
        rf.write(report_str)
        rf.write("\nConfusion Matrix:\n")
        rf.write(np.array2string(cm))
        rf.write(f"\nClasses order: {list(model.classes_)}\n")
    print(f"\nSaved evaluation report to '{report_path}'.")

    # 9. Save Model and Vectorizer
    print("Saving model and vectorizer...")
    joblib.dump(model, os.path.join(script_dir, "sentiment_model.pkl"))
    joblib.dump(vectorizer, os.path.join(script_dir, "vectorizer.pkl"))
    print("Saved 'sentiment_model.pkl' and 'vectorizer.pkl' to root directory.")
    print("Model training pipeline complete. Ready to run Flask server (app.py)!")

if __name__ == '__main__':
    main()

import os
import re
import sys
import uuid
import datetime
import sqlite3
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename

# Import our custom preprocessor
from utils import TextPreprocessor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pulsemind_session_secret_key_2026')

def get_user_session_id():
    """Retrieve or assign a unique session ID per visitor/device."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DATABASE_PATH = os.path.join(BASE_DIR, 'predictions.db')
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)

# Global variables for the ML model
model = None
vectorizer = None
preprocessor = None
model_loaded = False

def load_ml_model():
    """Attempt to load the pre-trained Logistic Regression model and TF-IDF Vectorizer."""
    global model, vectorizer, preprocessor, model_loaded
    model_path = os.path.join(BASE_DIR, "sentiment_model.pkl")
    vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")
    
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        try:
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            preprocessor = TextPreprocessor()
            model_loaded = True
            print("Successfully loaded sentiment model and vectorizer.")
        except Exception as e:
            print(f"Error loading saved model/vectorizer: {e}", file=sys.stderr)
            model_loaded = False
    else:
        print("WARNING: 'sentiment_model.pkl' or 'vectorizer.pkl' is missing.", file=sys.stderr)
        print("Please train the model by running: python train_model.py", file=sys.stderr)
        model_loaded = False

# Database setup
def init_db():
    """Initialize the SQLite database for prediction history with session isolation."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'global',
                tweet TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                confidence REAL NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        
        # Migration check: Ensure user_id column exists
        cursor.execute("PRAGMA table_info(predictions)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE predictions ADD COLUMN user_id TEXT NOT NULL DEFAULT 'global'")
            
        conn.commit()
        conn.close()
        print("SQLite Database initialized with session isolation support.")
    except Exception as e:
        print(f"Database initialization error: {e}", file=sys.stderr)

def get_db_connection():
    """Establish and return database connection with row representation."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize components
init_db()
load_ml_model()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    return render_template('index.html', model_loaded=model_loaded)

@app.route('/predict', methods=['POST'])
def predict():
    """Single tweet analysis endpoint."""
    if not model_loaded:
        return jsonify({
            'status': 'error',
            'message': 'Model is not trained. Please run "python train_model.py" in your terminal first.'
        }), 503
        
    data = request.get_json()
    if not data or 'tweet' not in data or not data['tweet'].strip():
        return jsonify({
            'status': 'error',
            'message': 'Tweet content cannot be empty.'
        }), 400
        
    tweet_text = data['tweet']
    
    try:
        # Preprocess
        cleaned_tweet = preprocessor.clean_text(tweet_text)
        
        # Check if preprocessing cleared everything
        if not cleaned_tweet.strip():
            # If nothing remains, label it neutral with low confidence
            sentiment = "Neutral"
            confidence = 50.0
        else:
            # Transform
            vec_tweet = vectorizer.transform([cleaned_tweet])
            
            # Predict probability
            probs = model.predict_proba(vec_tweet)[0]
            max_idx = probs.argmax()
            sentiment = model.classes_[max_idx]
            confidence = float(probs[max_idx] * 100) # Percentage
            
        # Log to Database with user session isolation
        user_id = get_user_session_id()
        now = datetime.datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO predictions (user_id, tweet, sentiment, confidence, date, time) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, tweet_text, sentiment, round(confidence, 2), date_str, time_str)
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'status': 'success',
            'id': row_id,
            'tweet': tweet_text,
            'prediction': sentiment,
            'confidence': round(confidence, 2),
            'date': date_str,
            'time': time_str
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"An error occurred during prediction: {str(e)}"
        }), 500

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Bulk CSV upload prediction handler."""
    if request.method == 'GET':
        return render_template('upload.html', model_loaded=model_loaded)
        
    if not model_loaded:
        return jsonify({'status': 'error', 'message': 'Model is not trained. Cannot perform batch predictions.'}), 503
        
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected.'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Invalid file format. Only CSV files are allowed.'}), 400
        
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        saved_name = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_name)
        file.save(file_path)
        
        # Read CSV safely with multiple fallback encodings and robust bad line filters
        df = None
        for encoding in ['utf-8', 'latin-1', 'utf-8-sig', 'cp1252']:
            try:
                df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip')
                break
            except Exception:
                continue
                
        if df is None or df.empty:
            return jsonify({'status': 'error', 'message': 'Failed to parse CSV file. Ensure it is a valid, non-empty comma-separated file.'}), 400
        
        # Auto-detect text column
        text_col = None
        for col in ['tweet', 'text', 'tweet_text', 'content', 'body', 'message']:
            if col.lower() in [c.lower() for c in df.columns]:
                text_col = [c for c in df.columns if c.lower() == col.lower()][0]
                break
        
        if not text_col:
            # Fallback to the first string column
            string_cols = df.select_dtypes(include=['object']).columns
            if len(string_cols) > 0:
                text_col = string_cols[0]
            else:
                text_col = df.columns[0]
                
        print(f"Batch prediction text column: {text_col}")
        
        results = []
        predictions_labels = []
        confidences = []
        
        now = datetime.datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for idx, row in df.iterrows():
            tweet_val = str(row[text_col])
            
            # Predict
            cleaned_tweet = preprocessor.clean_text(tweet_val)
            if not cleaned_tweet.strip():
                sentiment = "Neutral"
                confidence = 50.0
            else:
                vec = vectorizer.transform([cleaned_tweet])
                probs = model.predict_proba(vec)[0]
                max_idx = probs.argmax()
                sentiment = model.classes_[max_idx]
        db_rows = []
        
        for i in range(len(valid_rows)):
            max_idx = probs[i].argmax()
            sentiment = model.classes_[max_idx]
            confidence = round(float(probs[i][max_idx] * 100), 2)
            tweet_val = str(valid_rows[i][text_col])
            
            results.append({
                'tweet': tweet_val,
                'sentiment': sentiment,
                'confidence': confidence
            })
            
            db_rows.append((user_id, tweet_val, sentiment, confidence, date_str, time_str))
            
        cursor.executemany(
            'INSERT INTO predictions (user_id, tweet, sentiment, confidence, date, time) VALUES (?, ?, ?, ?, ?, ?)',
            db_rows
        )
        conn.commit()
        conn.close()
        
        # Create output CSV
        df['predicted_sentiment'] = predictions_labels
        df['prediction_confidence'] = confidences
        
        analyzed_filename = f"analyzed_{saved_name}"
        analyzed_path = os.path.join(app.config['UPLOAD_FOLDER'], analyzed_filename)
        df.to_csv(analyzed_path, index=False)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'download_url': f'/download/{analyzed_filename}',
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve the download of the analyzed CSV files."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    return render_template('error.html', 
                           error_code='FILE_NOT_FOUND',
                           error_title='File Not Found',
                           error_message='The analyzed CSV report you requested was not found. It may have been deleted or expired.'), 404

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', model_loaded=model_loaded)

@app.route('/dashboard/stats')
def dashboard_stats():
    """Retrieve database metrics and aggregate charts data filtered by user session."""
    try:
        user_id = get_user_session_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Basic Stats for current user session
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
        total_predictions = cursor.fetchone()[0]
        
        if total_predictions == 0:
            conn.close()
            return jsonify({
                'total': 0,
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'avg_confidence': 0.0,
                'line_chart': {'labels': [], 'data': []},
                'bar_chart': [0.0, 0.0, 0.0],
                'word_cloud': [],
                'recent': []
            })
            
        # Count by sentiment
        cursor.execute("SELECT sentiment, COUNT(*), AVG(confidence) FROM predictions WHERE user_id = ? GROUP BY sentiment", (user_id,))
        sentiment_data = cursor.fetchall()
        
        sentiment_counts = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
        sentiment_conf = {'Positive': 0.0, 'Neutral': 0.0, 'Negative': 0.0}
        
        for row in sentiment_data:
            sent = row[0]
            if sent in sentiment_counts:
                sentiment_counts[sent] = row[1]
                sentiment_conf[sent] = round(row[2], 2)
                
        # Average overall confidence
        cursor.execute("SELECT AVG(confidence) FROM predictions WHERE user_id = ?", (user_id,))
        avg_confidence = round(cursor.fetchone()[0], 2)
        
        # 2. Line Chart data (Grouped by Date)
        cursor.execute("SELECT date, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY date ORDER BY date DESC LIMIT 10", (user_id,))
        line_data = cursor.fetchall()
        line_labels = [row[0] for row in reversed(line_data)]
        line_counts = [row[1] for row in reversed(line_data)]
        
        # 3. Bar Chart (Confidences)
        bar_data = [sentiment_conf['Positive'], sentiment_conf['Neutral'], sentiment_conf['Negative']]
        
        # 4. Word Cloud data
        cursor.execute("SELECT tweet FROM predictions WHERE user_id = ?", (user_id,))
        tweets = cursor.fetchall()
        
        # Aggregate word count
        word_freq = {}
        local_stops = {'the', 'a', 'to', 'and', 'is', 'in', 'it', 'you', 'of', 'for', 'on', 'my', 'that', 'at', 'with', 'this', 'me', 'i', 'have', 'so', 'just', 'be', 'but', 'was', 'your'}
        if preprocessor:
            local_stops = local_stops.union(preprocessor.stop_words)
            
        for t_row in tweets:
            clean_t = re.sub(r'[^\w\s]', '', t_row[0].lower())
            words = clean_t.split()
            for w in words:
                if len(w) > 2 and w not in local_stops:
                    word_freq[w] = word_freq.get(w, 0) + 1
                    
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:40]
        word_cloud = [{'text': word, 'value': count} for word, count in sorted_words]
        
        # 5. Recent predictions list (Limit 50)
        cursor.execute("SELECT id, tweet, sentiment, confidence, date, time FROM predictions WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user_id,))
        recent_rows = cursor.fetchall()
        recent = []
        for r in recent_rows:
            recent.append({
                'id': r[0],
                'tweet': r[1],
                'sentiment': r[2],
                'confidence': r[3],
                'date': r[4],
                'time': r[5]
            })
            
        conn.close()
        
        return jsonify({
            'total': total_predictions,
            'positive': sentiment_counts['Positive'],
            'neutral': sentiment_counts['Neutral'],
            'negative': sentiment_counts['Negative'],
            'avg_confidence': avg_confidence,
            'line_chart': {
                'labels': line_labels,
                'data': line_counts
            },
            'bar_chart': bar_data,
            'word_cloud': word_cloud,
            'recent': recent
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Dashboard data error: {str(e)}'}), 500

@app.route('/history/delete', methods=['POST'])
def delete_history():
    """Delete a single prediction history entry for the current user session."""
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing record ID.'}), 400
        
    try:
        user_id = get_user_session_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = ? AND user_id = ?", (data['id'], user_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Record deleted successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database delete error: {str(e)}'}), 500

@app.route('/history/clear', methods=['POST'])
def clear_history():
    """Clear prediction history for the current user session."""
    try:
        user_id = get_user_session_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'History cleared successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database clear error: {str(e)}'}), 500

@app.route('/history/export')
def export_history():
    """Export prediction history database to a downloadable CSV for current user session."""
    try:
        user_id = get_user_session_id()
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT id, tweet, sentiment, confidence, date, time FROM predictions WHERE user_id = ? ORDER BY id DESC", conn, params=(user_id,))
        conn.close()
        
        export_filename = f"prediction_history_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        export_path = os.path.join(app.config['UPLOAD_FOLDER'], export_filename)
        df.to_csv(export_path, index=False)
        
        return send_file(export_path, as_attachment=True, download_name=export_filename)
    except Exception as e:
        return render_template('error.html', 
                               error_code='EXPORT_FAILED',
                               error_title='Export Failed',
                               error_message=f'Could not export prediction logs: {str(e)}'), 500



# Global HTTP Error Handlers
@app.errorhandler(400)
def bad_request_error(e):
    return render_template('error.html', 
                           error_code='400_BAD_REQUEST',
                           error_title='Bad Request',
                           error_message='The server could not understand the request due to malformed syntax. Please verify your input and try again.'), 400

@app.errorhandler(403)
def forbidden_error(e):
    return render_template('error.html', 
                           error_code='403_FORBIDDEN',
                           error_title='Access Forbidden',
                           error_message='You do not have permission to access this resource.'), 403

@app.errorhandler(404)
def page_not_found_error(e):
    return render_template('error.html', 
                           error_code='404_NOT_FOUND',
                           error_title='Page Not Found',
                           error_message='The page you are looking for does not exist or has been moved.'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', 
                           error_code='500_INTERNAL_ERROR',
                           error_title='Internal Server Error',
                           error_message='An unexpected error occurred on our server. Please try again later.'), 500

if __name__ == '__main__':
    # Start production/development web server based on PORT environment variables
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(host='0.0.0.0', port=port, debug=debug_mode)


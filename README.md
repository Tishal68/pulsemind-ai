# PulseMind AI 🧠💼
### AI-Powered Sentiment Intelligence Platform

PulseMind AI is a full-stack, enterprise-ready **Sentiment Intelligence Platform** designed to extract, analyze, and visualize emotional context and public opinion from unstructured text data (social media posts, customer reviews, product feedback, support tickets, and short-form documents).

Using Natural Language Processing (NLP) and Machine Learning, PulseMind AI classifies text into **Positive**, **Neutral**, or **Negative** sentiment with a calculated prediction confidence percentage.

The application features a sleek SaaS design inspired by modern tools like Linear, Cursor, and GitHub Dark.



## 📋 Table of Contents
- [🎯 Project Overview & Vision](#-project-overview--vision)
- [🔮 Core Features](#-core-features)
- [🛠️ Technology Stack](#️-technology-stack)
- [📁 Folder Structure](#-folder-structure)
- [🧠 Machine Learning Architecture](#-machine-learning-architecture)
- [🚀 Quickstart & Setup Guide](#-quickstart--setup-guide)
- [⚙️ Local Model Training](#️-local-model-training)
- [📊 Dashboard & CSV Batch Analyzer](#-dashboard--csv-batch-analyzer)
- [🛡️ Production Quality & Error Handling](#️-production-quality--error-handling)
- [🌐 Cloud Deployment Guide](#-cloud-deployment-guide)
- [📜 License & Contributing](#-license--contributing)
- [👤 Author](#-author)

---

## 🎯 Project Overview & Vision
Unstructured customer feedback contains crucial business insights. PulseMind AI bridges the gap between raw text data and actionable decisions by delivering platform-independent sentiment intelligence for:
- **Customer Satisfaction Tracking**: Aggregate public reviews and support feedback in real-time.
- **Brand Reputation Monitoring**: Track sentiment shifts and customer sentiment distribution.
- **Ticket Prioritization**: Identify urgent negative feedback for immediate routing.
- **Competitor Intelligence**: Analyze public feedback to identify market gaps.

---

## 🔮 Core Features

- ⚡ **Real-Time Text Classifier**: Millisecond-fast sentiment classification with progress confidence bars, text report exports, and copy actions. Supports inputs up to **10,000 characters**.
- 📁 **CSV Batch Analyzer**: Drag-and-drop CSV batch evaluation with multi-encoding fallback parsing (`utf-8`, `latin-1`, `cp1252`) and structured CSV export downloads.
- 📊 **Interactive Analytics Dashboard**: Real-time counter metrics, dynamic Chart.js visualizations (Share distributions, confidence levels, timeline volume trends), and an interactive keyword Word Cloud.
- 💾 **Persistent SQLite History**: Local prediction logging (`predictions.db`) featuring single-record deletion, database purging, and history exports.
- 🚫 **Zero-Alert Policy**: Native browser `alert()` and `confirm()` dialogs are replaced with animated glassmorphic modals (`showConfirmModal`).
- 🛡️ **Global Error Handling**: Custom branded HTTP error pages (`templates/error.html`) for 400, 403, 404, and 500 status codes.
- 🖨️ **PDF / Print Export**: Integrated `@media print` CSS layout for printing or saving dashboard reports to PDF.

---

## 🛠️ Technology Stack

| Domain | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3 (Custom Charcoal Glassmorphism), Vanilla JavaScript (ES6+), Chart.js, Bootstrap Icons |
| **Backend** | Python 3.11+, Flask 3.0 (REST API, Jinja2 Routing), Gunicorn WSGI |
| **Machine Learning** | Scikit-Learn (`TfidfVectorizer`, `LogisticRegression`), NLTK (Tokenization, Porter Stemmer, Stopwords), Pandas, NumPy, Joblib |
| **Database** | SQLite3 (Local Persistent Logs) |
| **Deployment** | Render, Railway, Docker, Gunicorn, `Procfile` |

---

## 📁 Folder Structure

```
PulseMind_AI_Production/
│
├── app.py                      # Flask Application Server (REST Routes, DB Controller, API Endpoints)
├── train_model.py              # Local ML Pipeline (Preprocessing, Splitting, Training, Evaluation)
├── utils.py                    # Preprocessing Engine (Regex cleaning, Stopwords, Stemmer)
├── wsgi.py                     # Production WSGI Entry Point
├── Procfile                    # PaaS Hosting Instruction File (Render / Railway / Heroku)
├── runtime.txt                 # Target Python Version Definition
├── requirements.txt            # Python Dependencies Specification
├── .gitignore                  # GitHub Exclusion Rules
├── LICENSE                     # MIT Open-Source License
├── CHANGELOG.md                # Release Version History
├── CONTRIBUTING.md             # Contribution Guidelines & Coding Standards
├── README.md                   # Repository Documentation
│
├── dataset/                    # Dataset Directory (Excluded from Git)
│     └── .gitkeep              # Keeps directory structure tracked
│
├── screenshots/                # Application Screenshots & Mockups
│     ├── home.png
│     ├── prediction.png
│     ├── dashboard.png
│     ├── upload.png
│     └── about.png
│
├── static/
│     ├── css/
│     │     └── style.css       # Design System (Charcoal variables, Keyframes, Print styles)
│     ├── js/
│     │     └── script.js       # App Controller (Chart renderers, Modals, Toasts, Skeletons)
│     └── images/
│           ├── favicon.svg     # Square Vector Brand Icon
│           ├── logo.svg         # General Horizontal Logo
│           ├── logo-light.svg   # Navbar Logo (Dark Mode)
│           └── logo-dark.svg    # Navbar Logo (Light Mode)
│
├── templates/
│     ├── base.html             # Layout Shell (Navbar, Footer, CDN Loads)
│     ├── index.html            # Real-Time Text Analyzer Page
│     ├── upload.html           # Batch CSV Processor Page
│     ├── dashboard.html        # Interactive Analytics Dashboard Page
│     ├── about.html            # Engine Architecture & Pipeline Page
│     └── error.html            # Branded Global Error Page
│
├── uploads/                    # Temporary Storage for CSV Uploads (Excluded from Git)
│     └── .gitkeep
└── reports/                    # Model Training Evaluation Output Reports (Excluded from Git)
      └── .gitkeep
```

---

## 🧠 Machine Learning Architecture

The NLP machine learning engine converts raw text into numerical representations and fits a linear decision boundary:

```
[Input Text / Document]
          ↓
[Regex Cleaning]       ──► Removes URLs, mentions (@user), hashtags (#topic), and non-ASCII/emojis
          ↓
[Case Normalization]   ──► Converts characters to lowercase
          ↓
[NLTK Tokenization]    ──► Splits text into word tokens using word_tokenize
          ↓
[Stopword Removal]     ──► Filters out non-sentimental words (the, is, at, and)
          ↓
[Porter Stemming]      ──► Reduces tokens to core roots (e.g. happiest -> happi)
          ↓
[TF-IDF Vectorization] ──► Generates numerical arrays using Unigrams & Bigrams (15,000 features)
          ↓
[Logistic Regression]  ──► Fits linear mathematical boundary to compute class log-odds
          ↓
[Categorical Output]   ──► Positive, Neutral, or Negative class + Confidence Score (%)
```

---

## 🚀 Quickstart & Setup Guide

Follow these steps to run **PulseMind AI** on your local machine:

### 1. Clone Repository & Prepare Virtual Environment
```bash
git clone https://github.com/YOUR_USERNAME/PulseMind-AI.git
cd PulseMind-AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Dataset Setup
Download a public sentiment dataset (such as the **Twitter US Airline Sentiment Dataset** or **Sentiment140**).
Place the CSV file inside the `dataset/` directory and rename it to `twitter.csv`:

```
dataset/twitter.csv
```

---

### 3. Train Model Locally
Run `train_model.py` to train the Logistic Regression pipeline locally on your computer:

```bash
python train_model.py
```

The script will split the dataset (**80% Train / 20% Test**), output classification metrics, and serialize the trained pipeline files:
- `sentiment_model.pkl`
- `vectorizer.pkl`
- `reports/evaluation.txt`

> [!NOTE]
> Pre-trained model pipeline binaries (`sentiment_model.pkl` and `vectorizer.pkl`) are included in the repository (~1.5 MB total) to enable **instant, zero-configuration deployment on Render.com** without build lag. The raw dataset (`dataset/twitter.csv`) and SQLite runtime logs (`predictions.db`) remain strictly excluded from GitHub via `.gitignore`.


---

### 4. Start the Application
Run `app.py` to launch the Flask server:

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000` to start analyzing text!

---

eMind-AI](https://github.com/)

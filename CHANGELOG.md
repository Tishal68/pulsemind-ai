# Changelog

All notable changes to the **PulseMind AI** platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-28

### 🚀 Added
- **Real-Time Sentiment Classifier**: Interactive single-text analyzer supporting inputs up to 10,000 characters with real-time character counters and confidence scores.
- **CSV Batch Analysis**: Bulk CSV processing pipeline with automatic text column detection (`text`, `tweet`, `review`, `comment`), multi-encoding fallback parsing, and restructured CSV report downloads.
- **Interactive Analytics Dashboard**: Real-time counter metrics, dynamic Chart.js visualizations (Sentiment shares, average confidence, timeline trends), and custom HTML5 canvas keyword Word Cloud.
- **Persistent SQLite Database**: Built-in SQLite logging (`predictions.db`) for tracking analysis history, single-record deletion, full purge options, and CSV history exports.
- **Custom Confirmation Modals**: Built-in glassmorphic UI modal (`showConfirmModal`) replacing native browser `confirm()` popups.
- **Global Error Handling**: Custom branded HTTP error pages (`templates/error.html`) for 400, 403, 404, and 500 status codes.
- **Print & PDF Export**: Integrated `@media print` CSS layout for exporting dashboard metrics directly to PDF.

### 🎨 Design & UI
- **Charcoal Dark & Light Themes**: Refined SaaS visual style inspired by Linear, Cursor, and GitHub with soft border lighting and responsive glassmorphism cards.
- **SVG Branding Assets**: Custom vector graphics (`favicon.svg`, `logo-light.svg`, `logo-dark.svg`, `logo.svg`) with dynamic theme-switching integration in `script.js`.
- **Skeleton Loaders**: Gradient pulse placeholders (`.skeleton-pulse`) preventing cumulative layout shifts during async data fetches.
- **Accessibility**: Visible `:focus-visible` focus loops for inputs, textareas, and interactive buttons.

### ⚙️ Machine Learning & Backend
- **NLTK Preprocessing Pipeline**: Lowercasing, URL/mention/hashtag regex stripping, NLTK word tokenization, English stopword filtering, and Porter stemming.
- **TF-IDF + Logistic Regression**: Unigram/bigram feature extraction fitting a linear decision boundary with ~77.8% accuracy.
- **Production Web Server**: Added `gunicorn` configuration, `Procfile`, `wsgi.py`, and `runtime.txt` for one-click PaaS deployment (Render, Railway).

### 🛠️ Production Cleanup
- Removed legacy academic demo references and platform-specific dependencies.
- Standardized absolute script-relative path resolution (`BASE_DIR`).
- Established clean GitHub repository structure with professional `.gitignore` exclusions.

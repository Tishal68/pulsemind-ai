# Contributing to PulseMind AI

Thank you for considering contributing to **PulseMind AI**! We welcome contributions from developers, researchers, and open-source enthusiasts.

---

## 🛠️ Local Development Environment Setup

### 1. Fork & Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/PulseMind-AI.git
cd PulseMind-AI
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Prepare Dataset & Train Local Model
Place a sentiment CSV dataset at `dataset/twitter.csv` and run:
```bash
python train_model.py
```

### 5. Launch Local Flask Server
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

---

## 📐 Coding Standards & Guidelines

- **PEP 8 Compliance**: Follow standard Python code style guidelines. Use 4 spaces for indentation.
- **Defensive Error Handling**: Ensure database queries and file operations use explicit `try-except` blocks.
- **Zero Browser Alerts**: Avoid native `alert()` or `confirm()` popups. Use `showToast()` or `showConfirmModal()`.
- **Modular Frontend**: Keep CSS variables inside `style.css` design tokens and avoid inline hardcoded hex codes.

---

## 🔀 Submitting Pull Requests

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Commit your changes with clear messages:
   ```bash
   git commit -m "feat: add multi-language text preprocessing support"
   ```
3. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
4. Open a **Pull Request (PR)** on GitHub with a description of your changes.

---

## 🐞 Reporting Bugs & Issues

When opening an issue on GitHub, please include:
- Operating System and Python version.
- Exact error tracebacks or console logs.
- Steps to reproduce the bug.

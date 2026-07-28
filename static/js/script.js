document.addEventListener('DOMContentLoaded', () => {
    // --- Theme Toggle Handler ---
    const themeToggleBtn = document.getElementById('themeToggle');
    const themeIcon = themeToggleBtn ? themeToggleBtn.querySelector('i') : null;
    
    // Check saved theme or system preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Initialize logo on load
    const navbarLogo = document.getElementById('navbarLogo');
    if (navbarLogo) {
        navbarLogo.src = savedTheme === 'dark' ? '/static/images/logo-light.svg' : '/static/images/logo-dark.svg';
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            showToast(`Switched to ${newTheme} mode`, 'info');
            
            // Toggle navbar logo
            if (navbarLogo) {
                navbarLogo.src = newTheme === 'dark' ? '/static/images/logo-light.svg' : '/static/images/logo-dark.svg';
            }
            
            // Reload charts on theme change if on dashboard
            if (window.location.pathname.includes('dashboard')) {
                loadDashboardData();
            }
        });
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.className = 'bi bi-sun-fill';
        } else {
            themeIcon.className = 'bi bi-moon-stars-fill';
        }
    }

    // --- Toast Notification Handler ---
    function showToast(message, type = 'info') {
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.className = 'toast';
        
        let iconClass = 'bi-info-circle-fill info';
        if (type === 'success') iconClass = 'bi-check-circle-fill success';
        if (type === 'error') iconClass = 'bi-exclamation-triangle-fill error';
        
        toast.innerHTML = `
            <i class="bi ${iconClass}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Trigger reflow
        toast.offsetHeight;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 4000);
    }
    window.showToast = showToast; // Expose globally

    // --- Custom Confirmation Modal ---
    function showConfirmModal(title, message, onConfirm) {
        const modalContainer = document.createElement('div');
        modalContainer.className = 'modal-container';
        
        modalContainer.innerHTML = `
            <div class="glass-card modal-card">
                <h3>${title}</h3>
                <p>${message}</p>
                <div class="modal-btns">
                    <button class="btn-secondary modal-cancel-btn">Cancel</button>
                    <button class="glow-btn modal-confirm-btn" style="background: var(--sentiment-neg); border-color: rgba(248, 81, 73, 0.4);">Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modalContainer);
        
        // Trigger transition
        setTimeout(() => modalContainer.classList.add('show'), 10);
        
        const cancelBtn = modalContainer.querySelector('.modal-cancel-btn');
        const confirmBtn = modalContainer.querySelector('.modal-confirm-btn');
        
        function closeModal() {
            modalContainer.classList.remove('show');
            setTimeout(() => modalContainer.remove(), 200);
        }
        
        cancelBtn.addEventListener('click', closeModal);
        confirmBtn.addEventListener('click', () => {
            closeModal();
            onConfirm();
        });
        
        modalContainer.addEventListener('click', (e) => {
            if (e.target === modalContainer) closeModal();
        });
    }
    window.showConfirmModal = showConfirmModal;

    // --- Typing Animation (Hero Section) ---
    const typingSpan = document.querySelector('.typing-container');
    if (typingSpan) {
        const phrases = [
            "Analyze social media posts in real-time.",
            "Evaluate product and customer reviews.",
            "Understand sentiment and emotional context.",
            "Classify CSV datasets instantly."
        ];
        let phraseIdx = 0;
        let charIdx = 0;
        let isDeleting = false;
        let delay = 100;

        function typeEffect() {
            const currentPhrase = phrases[phraseIdx];
            
            if (isDeleting) {
                typingSpan.textContent = currentPhrase.substring(0, charIdx - 1);
                charIdx--;
                delay = 50;
            } else {
                typingSpan.textContent = currentPhrase.substring(0, charIdx + 1);
                charIdx++;
                delay = 100;
            }

            if (!isDeleting && charIdx === currentPhrase.length) {
                isDeleting = true;
                delay = 2000; // Pause at end of sentence
            } else if (isDeleting && charIdx === 0) {
                isDeleting = false;
                phraseIdx = (phraseIdx + 1) % phrases.length;
                delay = 500; // Pause before new sentence
            }

            setTimeout(typeEffect, delay);
        }
        setTimeout(typeEffect, 1000);
    }

    // --- Character Count Handler ---
    const textarea = document.getElementById('tweetInput');
    const counter = document.getElementById('charCount');
    if (textarea && counter) {
        textarea.addEventListener('input', () => {
            const count = textarea.value.length;
            counter.textContent = count;
            if (count > 9500) {
                counter.style.color = '#f43f5e'; // Warning limit color
            } else {
                counter.style.color = 'var(--text-secondary)';
            }
        });
    }

    // --- Example Preset Buttons ---
    const exampleBtns = document.querySelectorAll('.example-btn');
    if (exampleBtns && textarea) {
        exampleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                textarea.value = btn.getAttribute('data-tweet');
                textarea.dispatchEvent(new Event('input')); // Update char count
                showToast("Example text loaded!", "success");
            });
        });
    }

    // --- Single Tweet Prediction ---
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loader = document.getElementById('loader');
    const resultsCard = document.getElementById('resultsCard');
    
    if (analyzeBtn && textarea) {
        analyzeBtn.addEventListener('click', async () => {
            const text = textarea.value.trim();
            if (!text) {
                showToast("Please enter text to analyze.", "error");
                return;
            }

            // Hide old card, show loader
            resultsCard.classList.remove('reveal');
            loader.style.display = 'flex';
            analyzeBtn.disabled = true;

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tweet: text })
                });

                const data = await response.json();
                loader.style.display = 'none';
                analyzeBtn.disabled = false;

                if (data.status === 'success') {
                    displaySingleResult(data);
                    showToast("Prediction complete!", "success");
                } else {
                    showToast(data.message || "An error occurred.", "error");
                }
            } catch (error) {
                loader.style.display = 'none';
                analyzeBtn.disabled = false;
                showToast("Failed to connect to server.", "error");
                console.error(error);
            }
        });
    }

    function displaySingleResult(data) {
        const emojiEl = document.getElementById('resultEmoji');
        const sentimentEl = document.getElementById('resultSentiment');
        const confidenceValueEl = document.getElementById('confidenceValue');
        const progressBar = document.getElementById('resultProgressBar');
        
        let emoji = "😐";
        if (data.prediction === 'Positive') emoji = "😊";
        if (data.prediction === 'Negative') emoji = "😡";

        emojiEl.textContent = emoji;
        sentimentEl.textContent = data.prediction;
        
        // Remove old classes and add current sentiment class
        sentimentEl.className = `result-sentiment ${data.prediction}`;
        
        confidenceValueEl.textContent = `${data.confidence}%`;
        
        progressBar.className = `progress-bar ${data.prediction}`;
        progressBar.style.width = '0%';
        
        // Render card
        resultsCard.style.display = 'block';
        setTimeout(() => {
            resultsCard.classList.add('reveal');
            // Animate progress bar fill after card shows
            setTimeout(() => {
                progressBar.style.width = `${data.confidence}%`;
            }, 100);
        }, 50);

        // Copy button handler
        const copyBtn = document.getElementById('copyBtn');
        if (copyBtn) {
            copyBtn.onclick = () => {
                const copyText = `Text Content: "${data.tweet}"\nSentiment: ${data.prediction} (${data.confidence}%)`;
                navigator.clipboard.writeText(copyText).then(() => {
                    showToast("Result copied to clipboard!", "success");
                }).catch(() => {
                    showToast("Failed to copy text.", "error");
                });
            };
        }

        // Download button handler
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.onclick = () => {
                const fileText = `PulseMind AI Classification Result\n===============================\nDate: ${data.date}\nTime: ${data.time}\n\nAnalyzed Text:\n"${data.tweet}"\n\nClassification:\nSentiment: ${data.prediction}\nConfidence: ${data.confidence}%\n`;
                const blob = new Blob([fileText], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `sentiment_result_${data.id}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                showToast("Result downloaded!", "success");
            };
        }
    }

    // --- CSV File Upload & Table Render ---
    const uploadForm = document.getElementById('uploadForm');
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const uploadLoader = document.getElementById('uploadLoader');
    const uploadResults = document.getElementById('uploadResults');
    const uploadTableBody = document.querySelector('#uploadTable tbody');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');

    if (uploadZone && fileInput) {
        // Drag and drop events
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
            }, false);
        });

        uploadZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        uploadZone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                handleFileSelect(fileInput.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        const uploadZoneText = uploadZone.querySelector('.upload-info h3');
        if (uploadZoneText) {
            uploadZoneText.textContent = `Selected: ${file.name}`;
        }
        showToast(`Selected file: ${file.name}`, 'info');
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (fileInput.files.length === 0) {
                showToast("Please select a CSV file first.", "error");
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            uploadLoader.style.display = 'flex';
            uploadResults.style.display = 'none';

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                uploadLoader.style.display = 'none';

                if (data.status === 'success') {
                    showToast(`Batch completed! Processed ${data.count} records.`, 'success');
                    renderUploadTable(data.results);
                    downloadCsvBtn.onclick = () => {
                        window.location.href = data.download_url;
                    };
                    uploadResults.style.display = 'block';
                } else {
                    showToast(data.message || "An error occurred.", "error");
                }
            } catch (err) {
                uploadLoader.style.display = 'none';
                showToast("Connection to server failed.", "error");
                console.error(err);
            }
        });
    }

    function renderUploadTable(results) {
        if (!uploadTableBody) return;
        uploadTableBody.innerHTML = '';
        
        results.forEach((row, i) => {
            const tr = document.createElement('tr');
            
            // Limit shown tweet text length in table for clean spacing
            const truncatedTweet = row.tweet.length > 120 ? row.tweet.substring(0, 120) + '...' : row.tweet;
            
            tr.innerHTML = `
                <td>${i + 1}</td>
                <td title="${row.tweet}">${truncatedTweet}</td>
                <td><span class="badge ${row.sentiment}">${row.sentiment}</span></td>
                <td><strong>${row.confidence}%</strong></td>
            `;
            uploadTableBody.appendChild(tr);
        });
    }

    // --- Dashboard & Chart.js Config ---
    let sentimentPieChart = null;
    let confidenceBarChart = null;
    let volumeLineChart = null;

    if (window.location.pathname.includes('dashboard')) {
        loadDashboardData();
        
        const clearHistoryBtn = document.getElementById('clearHistoryBtn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => {
                showConfirmModal(
                    "Purge Database Logs",
                    "Are you sure you want to delete ALL prediction history from the database? This action cannot be undone and will reset the analytics dashboard.",
                    async () => {
                        try {
                            const response = await fetch('/history/clear', { method: 'POST' });
                            const data = await response.json();
                            if (data.status === 'success') {
                                showToast("All prediction history cleared!", "success");
                                loadDashboardData();
                            } else {
                                showToast("Failed to clear database.", "error");
                            }
                        } catch (e) {
                            showToast("Connection error.", "error");
                        }
                    }
                );
            });
        }
    }

    async function loadDashboardData() {
        // Set up skeleton loaders immediately
        const statsElements = ['totalCount', 'posCount', 'neutCount', 'negCount', 'avgConfidence'];
        statsElements.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = '<span class="skeleton-pulse" style="width: 70px; height: 32px; display: inline-block; border-radius: 6px;"></span>';
            }
        });
        
        const historyTableBody = document.querySelector('#historyTable tbody');
        if (historyTableBody) {
            historyTableBody.innerHTML = `
                <tr class="skeleton-row">
                    <td colspan="6" style="padding: 30px; text-align: center;">
                        <span class="skeleton-pulse" style="width: 90%; height: 16px; display: block; border-radius: 4px; margin: 0 auto 12px auto;"></span>
                        <span class="skeleton-pulse" style="width: 75%; height: 16px; display: block; border-radius: 4px; margin: 0 auto 12px auto;"></span>
                        <span class="skeleton-pulse" style="width: 60%; height: 16px; display: block; border-radius: 4px; margin: 0 auto;"></span>
                    </td>
                </tr>
            `;
        }

        try {
            const response = await fetch('/dashboard/stats');
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            const data = await response.json();
            if (data.status === 'error') {
                throw new Error(data.message);
            }

            // 1. Counter numbers animations
            animateCounter('totalCount', data.total);
            animateCounter('posCount', data.positive);
            animateCounter('neutCount', data.neutral);
            animateCounter('negCount', data.negative);
            animateCounter('avgConfidence', data.avg_confidence, true);

            if (data.total === 0) {
                showToast("No database logs found. Try performing predictions first!", "info");
                destroyCharts();
                renderEmptyDashboard();
                return;
            }

            // 2. Render Charts
            renderCharts(data);
            
            // 3. Render Word Cloud
            renderWordCloud(data.word_cloud);
            
            // 4. Render History List
            renderHistoryList(data.recent);

        } catch (error) {
            showToast("Failed to fetch dashboard statistics: " + error.message, "error");
            console.error(error);
            animateCounter('totalCount', 0);
            animateCounter('posCount', 0);
            animateCounter('neutCount', 0);
            animateCounter('negCount', 0);
            animateCounter('avgConfidence', 0, true);
            destroyCharts();
            renderEmptyDashboard();
        }
    }

    function animateCounter(id, targetValue, isFloat = false) {
        const el = document.getElementById(id);
        if (!el) return;
        
        const val = Number(targetValue);
        if (isNaN(val) || val === 0) {
            el.textContent = isFloat ? '0.00%' : '0';
            return;
        }
        
        let start = 0;
        const duration = 1000;
        const stepTime = 15;
        const steps = duration / stepTime;
        const increment = val / steps;
        
        const timer = setInterval(() => {
            start += increment;
            if (start >= val) {
                el.textContent = isFloat ? `${val.toFixed(2)}%` : Math.round(val);
                clearInterval(timer);
            } else {
                el.textContent = isFloat ? `${start.toFixed(2)}%` : Math.round(start);
            }
        }, stepTime);
    }


    function destroyCharts() {
        if (sentimentPieChart) sentimentPieChart.destroy();
        if (confidenceBarChart) confidenceBarChart.destroy();
        if (volumeLineChart) volumeLineChart.destroy();
    }

    function renderEmptyDashboard() {
        const cloudContainer = document.getElementById('wordcloudContainer');
        if (cloudContainer) cloudContainer.innerHTML = '<p style="color:var(--text-secondary); text-align:center;">No predictions log yet</p>';
        
        const historyTableBody = document.querySelector('#historyTable tbody');
        if (historyTableBody) historyTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-secondary)">No predictions found in SQLite database.</td></tr>';
    }

    function renderCharts(data) {
        destroyCharts();

        // Get computed styles for CSS variable colors
        const style = getComputedStyle(document.documentElement);
        const posColor = style.getPropertyValue('--sentiment-pos').trim() || '#10b981';
        const neutColor = style.getPropertyValue('--sentiment-neut').trim() || '#6b7280';
        const negColor = style.getPropertyValue('--sentiment-neg').trim() || '#f43f5e';
        const primaryColor = style.getPropertyValue('--primary').trim() || '#6366f1';
        const textPrimary = style.getPropertyValue('--text-primary').trim() || '#ffffff';
        const cardBorder = style.getPropertyValue('--card-border').trim() || 'rgba(255,255,255,0.08)';

        // 1. Pie Chart: Sentiment Distribution
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        sentimentPieChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [data.positive, data.neutral, data.negative],
                    backgroundColor: [posColor, neutColor, negColor],
                    borderWidth: 1,
                    borderColor: cardBorder
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textPrimary, font: { family: 'Inter', size: 12 } }
                    }
                },
                cutout: '65%'
            }
        });

        // 2. Bar Chart: Confidence by Sentiment
        const barCtx = document.getElementById('barChart').getContext('2d');
        confidenceBarChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    label: 'Avg Confidence %',
                    data: data.bar_chart,
                    backgroundColor: [posColor, neutColor, negColor],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: cardBorder },
                        ticks: { color: textPrimary }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: textPrimary }
                    }
                }
            }
        });

        // 3. Line Chart: Prediction Volume History
        const lineCtx = document.getElementById('lineChart').getContext('2d');
        volumeLineChart = new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: data.line_chart.labels.length > 0 ? data.line_chart.labels : ['No Logs'],
                datasets: [{
                    label: 'Texts Processed',
                    data: data.line_chart.data.length > 0 ? data.line_chart.data : [0],
                    borderColor: primaryColor,
                    backgroundColor: 'rgba(99, 102, 241, 0.15)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 2,
                    pointBackgroundColor: primaryColor
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: cardBorder },
                        ticks: { color: textPrimary, stepSize: 1 }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: textPrimary }
                    }
                }
            }
        });
    }

    function renderWordCloud(words) {
        const cloudContainer = document.getElementById('wordcloudContainer');
        if (!cloudContainer) return;
        cloudContainer.innerHTML = '';
        
        if (!words || words.length === 0) {
            cloudContainer.innerHTML = '<p style="color:var(--text-secondary)">No text processed yet</p>';
            return;
        }

        // Get max value to compute scale
        const maxVal = Math.max(...words.map(w => w.value));
        const style = getComputedStyle(document.documentElement);
        const primaryColor = style.getPropertyValue('--primary').trim() || '#6366f1';
        const textPrimary = style.getPropertyValue('--text-primary').trim() || '#ffffff';
        const textSecondary = style.getPropertyValue('--text-secondary').trim() || '#9ca3af';
        
        const colors = [primaryColor, '#10b981', '#3b82f6', '#ec4899', '#f59e0b', textPrimary, textSecondary];

        words.forEach(word => {
            const span = document.createElement('span');
            span.className = 'cloud-word';
            span.textContent = word.text;
            
            // Calculate size scale (range 12px to 42px)
            const fontSize = 12 + ((word.value / maxVal) * 30);
            span.style.fontSize = `${fontSize}px`;
            
            // Assign random theme color
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            span.style.color = randomColor;
            
            // Varied opacities
            const opacity = 0.5 + ((word.value / maxVal) * 0.5);
            span.style.opacity = opacity;
            
            span.setAttribute('title', `Count: ${word.value}`);
            
            cloudContainer.appendChild(span);
        });
    }

    function renderHistoryList(history) {
        const historyTableBody = document.querySelector('#historyTable tbody');
        if (!historyTableBody) return;
        historyTableBody.innerHTML = '';

        if (history.length === 0) {
            historyTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-secondary)">No predictions in database.</td></tr>';
            return;
        }

        history.forEach(row => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-id', row.id);
            
            const truncatedTweet = row.tweet.length > 80 ? row.tweet.substring(0, 80) + '...' : row.tweet;

            tr.innerHTML = `
                <td>${row.id}</td>
                <td title="${row.tweet}">${truncatedTweet}</td>
                <td><span class="badge ${row.sentiment}">${row.sentiment}</span></td>
                <td><strong>${row.confidence}%</strong></td>
                <td>${row.date} <span style="color:var(--text-secondary); font-size:0.8rem">${row.time}</span></td>
                <td>
                    <button class="delete-btn" onclick="deleteHistoryItem(${row.id})">
                        <i class="bi bi-trash3-fill"></i>
                    </button>
                </td>
            `;
            historyTableBody.appendChild(tr);
        });
    }

    // Function to delete single history item
    async function deleteHistoryItem(id) {
        showConfirmModal(
            `Delete Prediction #${id}`,
            "Are you sure you want to delete this prediction entry from the database? This action cannot be undone.",
            async () => {
                try {
                    const response = await fetch('/history/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: id })
                    });
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        showToast(`Record #${id} deleted`, 'success');
                        const row = document.querySelector(`tr[data-id="${id}"]`);
                        if (row) row.remove();
                        loadDashboardData();
                    } else {
                        showToast("Failed to delete record.", "error");
                    }
                } catch (e) {
                    showToast("Error connecting to server.", "error");
                }
            }
        );
    }

    // Expose to window so onclick handlers in dynamic html can call it
    window.deleteHistoryItem = deleteHistoryItem;
});

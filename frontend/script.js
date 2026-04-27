const API_BASE = 'http://127.0.0.1:8000'; // Full URL needed for Live Server compatibility

// Global Chart Instances
let lineChartInstance = null;
let donutChartInstance = null;

// Initialize Dashboard Charts
function initCharts() {
    if (!document.getElementById('lineChart')) return;

    // Default empty charts
    const ctxLine = document.getElementById('lineChart').getContext('2d');
    lineChartInstance = new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            datasets: [
                {
                    label: 'Total Traffic',
                    data: [0, 0, 0, 0, 0, 0],
                    borderColor: '#00ffff',
                    backgroundColor: 'rgba(0, 255, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Fraud',
                    data: [0, 0, 0, 0, 0, 0],
                    borderColor: '#ff3366',
                    backgroundColor: 'rgba(255, 51, 102, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#a0a0b0' } }
            },
            scales: {
                x: { ticks: { color: '#a0a0b0' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#a0a0b0' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });

    const ctxDonut = document.getElementById('donutChart').getContext('2d');
    donutChartInstance = new Chart(ctxDonut, {
        type: 'doughnut',
        data: {
            labels: ['Normal', 'Fraud'],
            datasets: [{
                data: [1, 0], // Default
                backgroundColor: ['#00ff9d', '#ff3366'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { position: 'bottom', labels: { color: '#a0a0b0', padding: 20 } }
            }
        }
    });
}

// Fetch and update dashboard stats
async function fetchStats() {
    if (!document.getElementById('statTotal')) return;

    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();

        // Animate counter
        animateValue('statTotal', 0, data.total_processed, 1000);
        animateValue('statFraud', 0, data.fraud_detected, 1000);
        animateValue('statNormal', 0, data.normal_count, 1000);
        
        document.getElementById('statAvgRisk').textContent = `${data.avg_risk_score}%`;

        // Update Donut Chart
        if (donutChartInstance && data.total_processed > 0) {
            donutChartInstance.data.datasets[0].data = [data.normal_count, data.fraud_detected];
            donutChartInstance.update();
        }

    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Fetch recent transactions
async function fetchTransactions() {
    const tableBody = document.getElementById('transactionsTableBody');
    if (!tableBody) return;

    try {
        const res = await fetch(`${API_BASE}/transactions`);
        const data = await res.json();
        
        tableBody.innerHTML = '';
        
        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No transactions found</td></tr>';
            return;
        }

        // Mock data for line chart (since we don't group by hour in backend, we'll just distribute recent data randomly for visual effect)
        let hourlyTotal = [0, 0, 0, 0, 0, 0];
        let hourlyFraud = [0, 0, 0, 0, 0, 0];

        data.forEach((tx, idx) => {
            const tr = document.createElement('tr');
            
            let riskBadgeClass = 'badge-low';
            if (tx.risk_score > 70) riskBadgeClass = 'badge-high';
            else if (tx.risk_score > 30) riskBadgeClass = 'badge-medium';

            const formattedTime = new Date(tx.timestamp).toLocaleTimeString();
            
            tr.innerHTML = `
                <td>#${tx.id}</td>
                <td style="font-family: 'Space Grotesk', sans-serif;">$${tx.amount.toFixed(2)}</td>
                <td>${tx.location}</td>
                <td>${tx.device}</td>
                <td>${formattedTime}</td>
                <td><span class="${tx.prediction === 'Fraud' ? 'stat-red' : 'stat-green'}">${tx.prediction}</span></td>
                <td><span class="badge ${riskBadgeClass}">${tx.risk_score}%</span></td>
            `;
            tableBody.appendChild(tr);

            // Populate mock line chart data
            const bucket = idx % 6;
            hourlyTotal[bucket]++;
            if (tx.prediction === 'Fraud') hourlyFraud[bucket]++;
        });

        // Update Line Chart
        if (lineChartInstance) {
            // Just scale it up for visual effect
            lineChartInstance.data.datasets[0].data = hourlyTotal.map(v => v * 15 + Math.random() * 50);
            lineChartInstance.data.datasets[1].data = hourlyFraud.map(v => v * 15 + Math.random() * 10);
            lineChartInstance.update();
        }

    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

// Animate numbers
function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Single Transaction Form Submit
const predictionForm = document.getElementById('predictionForm');
if (predictionForm) {
    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const loader = document.getElementById('loader');
        loader.classList.add('active');
        
        const payload = {
            amount: parseFloat(document.getElementById('amount').value),
            location: document.getElementById('location').value,
            device: document.getElementById('device').value,
            time: parseInt(document.getElementById('time').value)
        };

        try {
            const res = await fetch(`${API_BASE}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await res.json();
            
            // Store result in local storage to pass to result.html
            localStorage.setItem('fraudResult', JSON.stringify(data));
            
            window.location.href = 'result.html';
        } catch (error) {
            console.error('Error predicting:', error);
            alert('Prediction failed. Is the backend running?');
            loader.classList.remove('active');
        }
    });
}

// File Upload Logic
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const fileInfo = document.getElementById('fileInfo');
const analyzeBtn = document.getElementById('analyzeBtn');

if (fileInput && dropZone) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    // Handle selected files
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type === "text/csv" || file.name.endsWith('.csv')) {
                fileInfo.style.display = 'block';
                fileInfo.innerHTML = `<i class="fa-solid fa-file-csv"></i> ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                analyzeBtn.style.display = 'block';
                // Attach file to input for upload
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
            } else {
                alert('Please upload a valid CSV file.');
            }
        }
    }

    // Analyze Batch
    analyzeBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        const loader = document.getElementById('loader');
        loader.classList.add('active');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch(`${API_BASE}/analyze-dataset`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                let errorMsg = 'Batch analysis failed on the server.';
                try {
                    const errorData = await res.json();
                    errorMsg = errorData.detail || errorMsg;
                } catch (e) {
                    errorMsg = `Server error (${res.status}): ${res.statusText}`;
                }
                throw new Error(errorMsg);
            }

            const data = await res.json();

            // Populate Batch Results
            document.getElementById('batchResults').style.display = 'block';
            
            animateValue('batchTotal', 0, data.total_records, 1000);
            animateValue('batchFraud', 0, data.fraud_count, 1000);
            document.getElementById('batchFraudPct').textContent = `${data.fraud_percentage}%`;
            document.getElementById('batchAvgRisk').textContent = `${data.avg_risk_score}%`;

            // Populate High Risk Table
            const tbody = document.getElementById('highRiskTableBody');
            tbody.innerHTML = '';
            
            data.high_risk_transactions.forEach(tx => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-family: 'Space Grotesk', sans-serif;">$${tx.amount.toFixed(2)}</td>
                    <td>${tx.location}</td>
                    <td>${tx.device}</td>
                    <td>${tx.time}:00</td>
                    <td><span class="badge badge-high">${tx.risk_score}%</span></td>
                `;
                tbody.appendChild(tr);
            });

            // Smooth scroll to results
            document.getElementById('batchResults').scrollIntoView({ behavior: 'smooth' });

            // Refresh global stats & transactions
            fetchStats();
            fetchTransactions();

        } catch (error) {
            console.error('Error analyzing dataset:', error);
            alert(`Batch Analysis Failed: ${error.message}`);
        } finally {
            loader.classList.remove('active');
        }
    });
}

// Auto-refresh Dashboard
if (window.location.pathname.includes('dashboard.html')) {
    document.addEventListener('DOMContentLoaded', () => {
        initCharts();
        fetchStats();
        fetchTransactions();
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            fetchStats();
            fetchTransactions();
        }, 5000);
    });
}

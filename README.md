# FraudShield AI – Real-Time & Dataset Fraud Detection System

FraudShield AI is a state-of-the-art, production-ready fintech application that detects fraudulent transactions in real-time and processes large batch datasets. It features a high-end glassmorphism dashboard powered by a Scikit-Learn Random Forest model and a FastAPI backend.

## 🚀 Features
- **Real-Time Single Transaction Detection:** Input transaction details to instantly receive an AI-powered risk score and verdict.
- **Batch Dataset Analysis:** Drag-and-drop CSV datasets to analyze thousands of transactions at once.
- **Futuristic UI/UX:** Stunning neon, glassmorphism UI with smooth animations.
- **Live Dashboard:** Real-time metrics counters and interactive Chart.js graphs that automatically refresh.
- **Machine Learning Integration:** Uses `RandomForestClassifier` trained on transaction data.

## 🧠 Tech Stack
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Chart.js
- **Backend:** Python, FastAPI, Uvicorn, SQLite
- **Machine Learning:** Scikit-Learn, Pandas, NumPy

## 🛠️ Project Structure
```
fraudshield-ai/
├── backend/
│   ├── main.py        # FastAPI server endpoints
│   ├── database.py    # SQLite DB initialization & functions
│   └── model.pkl      # Trained Random Forest model (generated)
├── frontend/
│   ├── index.html     # Landing page
│   ├── input.html     # Single transaction check
│   ├── result.html    # Prediction result view
│   ├── dashboard.html # Main analytics dashboard
│   ├── style.css      # Glassmorphism/Neon styles
│   └── script.js      # Fetch APIs and Chart.js logic
├── model/
│   ├── train.py       # ML Model training script
│   └── generate_dataset.py # Synthetic data generation
├── data/
│   └── dataset.csv    # Generated synthetic dataset
├── requirements.txt   # Python dependencies
└── README.md
```

## ⚙️ Setup Instructions

### 1. Install Dependencies
Ensure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset & Train Model
Run the following scripts to generate a dataset and train the Machine Learning model:
```bash
# Generate synthetic data (saved to data/dataset.csv)
python model/generate_dataset.py

# Train the Random Forest model (saves model to backend/model.pkl)
python model/train.py
```

### 3. Run the Backend Server
Start the FastAPI server:
```bash
python -m uvicorn backend.main:app --reload
```
The backend API will be available at `http://127.0.0.1:8000`.

### 4. Open the Frontend
Since it uses Vanilla JS, simply double-click `frontend/index.html` to open it in your browser. Alternatively, use a live server extension if you are in VS Code.

## 🌟 Demo Walkthrough
1. **Landing Page:** Enjoy the neon animation.
2. **Dashboard:** See real-time empty graphs.
3. **Single Check:** Go to the "Single Check" page, input some data (e.g., $1500 amount at 3 AM), and click "Run AI Analysis". See the animated verdict.
4. **Batch Analysis:** Go to the Dashboard, drop `data/dataset.csv` into the upload zone, and click "Analyze Dataset". Wait for the loading animation and watch the analytics and charts update dynamically!

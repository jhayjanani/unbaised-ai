import sqlite3
import os

DB_PATH = 'backend/transactions.db'

def init_db():
    os.makedirs('backend', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        location TEXT,
        device TEXT,
        time INTEGER,
        prediction TEXT,
        risk_score REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def insert_transaction(amount, location, device, time, prediction, risk_score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO transactions (amount, location, device, time, prediction, risk_score)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (amount, location, device, time, prediction, risk_score))
    
    conn.commit()
    conn.close()

def insert_transactions_batch(transactions):
    """Inserts multiple transactions in a single transaction for efficiency."""
    if not transactions:
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executemany('''
    INSERT INTO transactions (amount, location, device, time, prediction, risk_score)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', transactions)
    
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM transactions')
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE prediction = 'Fraud'")
    fraud_count = cursor.fetchone()[0]
    
    normal_count = total - fraud_count
    
    cursor.execute('SELECT AVG(risk_score) FROM transactions')
    avg_risk = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        'total_processed': total,
        'fraud_detected': fraud_count,
        'normal_count': normal_count,
        'avg_risk_score': round(avg_risk, 2)
    }

def get_recent_transactions(limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM transactions 
    ORDER BY timestamp DESC 
    LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

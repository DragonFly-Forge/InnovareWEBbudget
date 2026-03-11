import csv
from io import StringIO
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import get_db_connection 
from smart_logic import get_daily_spending_limit
from flask import render_template # Add this to your imports
import random

# Place this function BEFORE your routes
def get_simulated_price(current_price):
    """
    Simulates a market change for your youth budgeting project.
    Generates a random fluctuation between -5% and +10%.
    """
    # Using random.uniform for a decimal range
    change_percent = random.uniform(-0.05, 0.10) 
    new_price = float(current_price) * (1 + change_percent)
    return round(new_price, 2) 
app = Flask(__name__)
CORS(app) 

# --- QOL: EXPORT DATA TO CSV ---
@app.route('/api/export/<int:user_id>', methods=['GET'])
def export_csv(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.date, t.description, c.name, t.amount, t.type 
            FROM transactions t 
            JOIN categories c ON t.category_id = c.id 
            WHERE t.user_id = %s ORDER BY t.date DESC
        """, (user_id,))
        rows = cur.fetchall()
        
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Date', 'Description', 'Category', 'Amount', 'Type'])
        cw.writerows(rows)
        
        return Response(
            si.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=SSY_Report_User_{user_id}.csv"}
        )
    finally:
        cur.close()
        conn.close()

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    budget = data.get('budget', 5000)
    
    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id", 
                    (username, f"{username}@ssy.com", hashed_pw))
        new_id = cur.fetchone()[0]
        # Automatically setting budget for March 2026
        cur.execute("INSERT INTO budgets (user_id, category_id, monthly_limit, month_year) VALUES (%s, 1, %s, '2026-03-01')", (new_id, budget))
        conn.commit()
        return jsonify({"message": "Account Created", "user_id": new_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and check_password_hash(user[1], password):
        return jsonify({"user_id": user[0]}), 200
    return jsonify({"error": "Invalid Credentials"}), 401

@app.route('/api/clear-data/<int:user_id>', methods=['DELETE'])
def clear_user_data(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM transactions WHERE user_id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "Data Cleared"}), 200
    finally:
        cur.close()
        conn.close()

@app.route('/api/smart-summary/<int:user_id>', methods=['GET'])
def smart_summary(user_id):
    data = get_daily_spending_limit(user_id)
    return jsonify(data), 200 if isinstance(data, dict) else 500

@app.route('/api/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT t.amount, t.description, t.type, t.date, c.name, c.icon FROM transactions t JOIN categories c ON t.category_id = c.id WHERE t.user_id = %s ORDER BY t.date DESC", (user_id,))
    rows = cur.fetchall()
    res = [{"amount": float(r[0]), "description": r[1], "type": r[2], "date": r[3].strftime("%Y-%m-%d"), "category": r[4], "icon": r[5]} for r in rows]
    cur.close()
    conn.close()
    return jsonify(res), 200

@app.route('/api/add-transaction', methods=['POST'])
def add_transaction():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (user_id, category_id, amount, type, description, date) VALUES (%s, %s, %s, 'expense', %s, CURRENT_DATE)", 
                (data['user_id'], data['category_id'], data['amount'], data['description']))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Success"}), 201

@app.route('/api/add-income', methods=['POST'])
def add_income():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (user_id, category_id, amount, type, description, date) VALUES (%s, %s, %s, 'income', %s, CURRENT_DATE)", 
                (data['user_id'], data['category_id'], data['amount'], data['description']))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Success"}), 201



@app.route('/')
def index():
    # This serves your HTML file instead of JSON
    return render_template('index.html')
if __name__ == "__main__":
    app.run(debug=True, port=5000)
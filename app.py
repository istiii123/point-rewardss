from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'rahasia_osha'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
    conn.close()
    if user:
        session['user_id'] = user['id']
        session['name'] = user['name']
        return redirect('/dashboard')
    return 'Login gagal'

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('dashboard.html', user=user)

@app.route('/redeem', methods=['POST'])
def redeem():
    if 'user_id' not in session:
        return redirect('/')
    item = request.form['item']
    cost = int(request.form['cost'])

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if user['points'] >= cost:
        new_points = user['points'] - cost
        conn.execute('UPDATE users SET points = ? WHERE id = ?', (new_points, session['user_id']))
        conn.execute('INSERT INTO transactions (user_id, description, points) VALUES (?, ?, ?)',
                     (session['user_id'], f"Redeemed {item}", -cost))
        conn.commit()
    conn.close()
    return redirect('/dashboard')

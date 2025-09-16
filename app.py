from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Create users table if not exists
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
# Insert default users if not exist
default_users = [
    ('admin', generate_password_hash('admin123')),
    ('user1', generate_password_hash('pass1')),
    ('user2', generate_password_hash('pass2'))
]
for username, hashed_pw in default_users:
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
    except sqlite3.IntegrityError:
        pass  # User already exists
conn.commit()
conn.close()

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user[0] == username and check_password_hash(user[1], password):
            return f"Welcome, {username}!"
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if get_user(username):
            error = "Username already exists"
        else:
            hashed_password = generate_password_hash(password)
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

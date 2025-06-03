from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from werkzeug.utils import secure_filename
from datetime import date

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="profile"
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM register WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        name = request.form['name']
        birthdate = request.form['birthdate']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        image = request.files['image']

        filename = ''
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO register (name, birthdate, address, username, password, image_filename)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, birthdate, address, username, password, filename))
            conn.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            print(e)
            message = 'Username already exists or database error.'
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html', message=message)

@app.route('/profile')
def profile():
    username = request.args.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM register WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return "User not found"

    birthdate = user.get('birthdate')
    if birthdate:
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    else:
        age = None

    return render_template('profile.html', user=user, age=age)

if __name__ == '__main__':
    app.run(debug=True)

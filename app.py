from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from dotenv import load_dotenv
import os



load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')



@app.route('/')
def home():
    return render_template("home.html")




def get_row_count(table_name):
    conn = sqlite3.connect('user.db')  # Replace with your database file path
    cursor = conn.cursor()

    query = f"SELECT COUNT(*) FROM {table_name};"
    cursor.execute(query)
    row_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return row_count


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Password and Confirm Password don't match", 'danger')
            return redirect(url_for('register'))




        hashed_password = generate_password_hash(password, method='sha256')




         # Connect to the database
        conn = sqlite3.connect('User.db')
        cursor = conn.cursor()


        cursor.execute('SELECT EXISTS ( SELECT 1 FROM User WHERE username = ?)', (username,))

        exists = cursor.fetchone()[0]

        if(exists):
            flash('Username already exists. Choose another username.', 'failure')
            return redirect(url_for('register'))


        index = get_row_count("User") + 1
        data = (index, username, hashed_password)

        cursor.execute('INSERT INTO User VALUES (?, ?, ?)', data)

        # Save the changes and close the connection
        conn.commit()
        conn.close()



        # flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('User.db')
        cursor = conn.cursor()


        cursor.execute('SELECT * FROM User WHERE username = ?', (username, ))

        rows = cursor.fetchall()

        print("\n\n\nRows:", rows)

        conn.close()

        if len(rows) == 0:
            flash("User does not exist.", "danger")
            return redirect(url_for('login'))


        if check_password_hash(rows[0][2], password):
            # flash('Login successful.', 'success')
            return redirect(url_for('dashboard', name=username))
        else:
            print("Invalid")
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard/<name>')
def dashboard(name):
    return render_template('dashboard.html', user=name)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run()

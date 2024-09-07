from flask import Flask, render_template, request, redirect, url_for # type: ignore
from flask_mysqldb import MySQL # type: ignore
import MySQLdb.cursors # type: ignore
import re
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kanishka@15'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'simple_expense_tracker'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        hashed_password = generate_password_hash(password)  # Default hash method
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM app_users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO app_users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    return render_template('signup.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM app_users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account and check_password_hash(account['password'], password):
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/home', methods=['GET'])
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user_expenses')
    expenses = cursor.fetchall()
    return render_template('home.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO user_expenses (user_id, description, amount) VALUES (%s, %s, %s)', (1, description, amount))  # user_id is hardcoded for simplicity
        mysql.connection.commit()
        return redirect(url_for('home'))
    return render_template('add_expense.html')

@app.route('/stats', methods=['GET'])
def stats():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Total amount per day
    cursor.execute("""
        SELECT DATE(date_added) AS date, SUM(amount) AS total_amount
        FROM user_expenses
        GROUP BY DATE(date_added)
        ORDER BY DATE(date_added) DESC
    """)
    daily_totals = cursor.fetchall()
    
    # Total amount per month
    cursor.execute("""
        SELECT YEAR(date_added) AS year, MONTH(date_added) AS month, SUM(amount) AS total_amount
        FROM user_expenses
        GROUP BY YEAR(date_added), MONTH(date_added)
        ORDER BY YEAR(date_added) DESC, MONTH(date_added) DESC
    """)
    monthly_totals = cursor.fetchall()
    
    # Total amount per year
    cursor.execute("""
        SELECT YEAR(date_added) AS year, SUM(amount) AS total_amount
        FROM user_expenses
        GROUP BY YEAR(date_added)
        ORDER BY YEAR(date_added) DESC
    """)
    yearly_totals = cursor.fetchall()
    
    return render_template('stats.html', daily_totals=daily_totals, monthly_totals=monthly_totals, yearly_totals=yearly_totals)



if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime
import time

app = Flask(__name__)
app.secret_key = 'benefit'

#database connection details
app.config['MYSQL_DB'] = 'The Curious Case Of Cosmetics'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pick me girls'

# Intialize MySQL
mysql = MySQL(app)

#http://localhost:5000/
@app.route('/', methods=['GET', 'POST'])
def login():
    #output message if something goes wrong
    msg = ''
    # Check if "member_id" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        pw = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM `Member User` WHERE username = %s AND password = %s', (username, pw,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['Username']
            return redirect('dashboard.html')
    
        else:
            msg = 'Incorrect username/password! Try again!'
    return render_template('login.html', msg=msg)




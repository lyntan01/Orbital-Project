from flask import Flask, render_template, request, redirect, url_for, session, flash, Markup
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
app.config['MYSQL_PASSWORD'] = 'T0107553a'

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
            session['username'] = account['username']
            return redirect(url_for('routine'))
    
        else:
            msg = 'Incorrect username/password! Try again!'
    return render_template('login.html', msg=msg)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'firstname' in request.form and "email" in request.form and "gender" in request.form and 'lastname' in request.form and 'password' in request.form:
        username = request.form['username']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        gender = request.form['gender']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM `Member User` WHERE email = %s', (email,))
        emailcheck = cursor.fetchone()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM `Member User` WHERE username = %s', (username,))
        usercheck = cursor.fetchone()
        # If account exists show error and validation checks
        if emailcheck:
            msg = 'Account already exists!'
        elif usercheck:
            msg = 'Username already exists!'
        elif len(gender) != 1:
            msg = 'Gender must be F or M!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into member user table
            cursor.execute(
                'INSERT INTO `Member User` VALUES (%s, %s, %s, %s, %s, %s )', (username, firstname, lastname, gender, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    # Show registration form with message (if any)
    return render_template('signup.html', msg=msg)

@app.route('/shelve', methods=['GET', 'POST'])
def shelve():
    if 'loggedin' in session:
        products = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT DISTINCT brand, skincare_or_makeup, T1.product_name, shelved_date
                            FROM `Shelves` AS T1
                            JOIN `Product` AS T2 
                            ON T1.product_name = T2.product_name
                            WHERE T1.username = %s''', (session['username'],))
        results = cursor.fetchall()
        for row in results:
            products.append(row)
        return render_template('shelve.html', products=products)

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if 'loggedin' in session:
        products = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT DISTINCT brand, skincare_or_makeup, T1.product_name, wished_date
                            FROM `Wishes` AS T1
                            JOIN `Product` AS T2 
                            ON T1.product_name = T2.product_name
                            WHERE T1.username = %s''', (session['username'],))
        results = cursor.fetchall()
        for row in results:
            products.append(row)
        return render_template('wishlist.html', products=products)

@app.route('/using', methods=['GET', 'POST'])
def using():
    if 'loggedin' in session:
        products = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT DISTINCT brand, skincare_or_makeup, T1.product_name, routine_category, expiry_date, frequency_type, frequency, specific_days
                            FROM `Uses` AS T1
                            JOIN `Product` AS T2 
                            ON T1.product_name = T2.product_name
                            WHERE T1.username = %s''', (session['username'],))
        results = cursor.fetchall()
        for row in results:
            products.append(row)
        return render_template('using.html', products=products)

@app.route('/routine', methods=['GET', 'POST'])
def routine():
    if 'loggedin' in session:
        products = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT DISTINCT brand, skincare_or_makeup, T1.product_name, routine_category, expiry_date, frequency_type, frequency, specific_days
                            FROM `Uses` AS T1
                            JOIN `Product` AS T2 
                            ON T1.product_name = T2.product_name
                            WHERE T1.username = %s ''', (session['username'],))
        results = cursor.fetchall()
        for row in results:
            products.append(row)
        return render_template('routine.html', products=products)


@app.route('/deleteShelve/<string:product_name>', methods=['GET', 'POST'] )
def delete(product_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'DELETE FROM `Shelves` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
    mysql.connection.commit()
    flash("Item Deleted!")
    return redirect(url_for('shelve'))

@app.route('/deleteWishlist/<string:product_name>', methods=['GET', 'POST'] )
def deleteWishlist(product_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'DELETE FROM `Wishes` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
    mysql.connection.commit()
    flash("Item Deleted!")
    return redirect(url_for('wishlist'))

@app.route('/deleteUsing/<string:product_name>', methods=['GET', 'POST'] )
def deleteUsing(product_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'DELETE FROM `Uses` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
    mysql.connection.commit()
    flash("Item Deleted!")
    return redirect(url_for('using'))

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('member_id', None)
    session.pop('name', None)
    # Redirect to login page
    return redirect(url_for('login'))

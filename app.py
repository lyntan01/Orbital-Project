from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = 'benefit'

#database connection details
app.config['MYSQL_DB'] = 'The Curious Case Of Cosmetics'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jenojinv1630'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/<username>/profile', methods=['GET', 'POST'])
def profile(username):
    # output message if something goes wrong
    msg = 'There was a problem loading your profile page. Please try again.'

    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute(
                'SELECT * FROM `Member User` WHERE username = %s', (username,))
        # Store user's information into a dictionary
        userInfo = cursor.fetchone()

        # If account does not exist show error and validation checks
        if not userInfo:
            msg = 'Account does not exist!'
        else: 
            # Account exists, now find all reviews made by user
            cursor = mysql.connection.cursor()
            cursor.execute(
                '''SELECT r.product_name, p.brand, p.skincare_or_makeup, r.rating 
                FROM Review r, Product p 
                WHERE r.username = %s AND r.product_name = p.product_name 
                ORDER BY p.brand, p.skincare_or_makeup, r.rating DESC''', (username,))
            # Store user's reviews into a dictionary
            reviews = cursor.fetchall()

            msg = 'Your profile will now be displayed'

    # Show user's profile with user's reviews (if any)
    return render_template('profile.html', username=username, userInfo=userInfo, reviews=reviews)

@app.route('/search', methods=['GET', 'POST'])
def search():
    products = []
    # Check if 'search_term' POST request exists (user submitted form)
    if request.method == 'POST' and 'search_term' in request.form:
        # Create variables for easy access
        search_term = request.form['search_term']
        # Check if product exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''SELECT product_name, brand, skincare_or_makeup, average_rating 
            FROM Product 
            WHERE LOCATE(%s, product_name) > 0 OR LOCATE(%s, brand) > 0
            ORDER BY brand, product_name''', (search_term, search_term,))
        # Store search results into a dictionary
        products = cursor.fetchall()
        return render_template('search.html', products=products, post=True)
    else:
        return render_template('search.html', products=products, post=False)

# This method adds a product to one of the user's shelves, 
# then redirects the user to the page of the selected shelf
@app.route('/add', methods=['GET', 'POST'])
def add():
    # CHANGE AFTER INTEGRATING
    username = 'lyntanrambutan'

    if request.method == 'POST': 
        # Form submitted is from Search page
        if 'product_name' in request.form and 'shelf' in request.form:
            product_name = request.form['product_name']
            shelf = request.form['shelf']
            date = datetime.today().strftime('%Y-%m-%d')

            existingShelves = checkExistingShelf(username, product_name)
            cursor = mysql.connection.cursor()
            if shelf=="Shelved":
                # If product already exists in user's Shelved products, show error and validation checks
                if "Shelved" in existingShelves:
                    msg = 'This product has already been Shelved!'
                elif existingShelves:
                    msg = 'This product is already in your ' + existingShelves[0] + "!"
                # Product is not in any of the user's shelves
                else:
                    cursor = mysql.connection.cursor()
                    cursor.execute('INSERT INTO `Shelves` VALUES(%s, %s, %s)', (username, product_name, date,))
                    mysql.connection.commit()
                    msg = 'Successfully added product to Shelved!'
                    return redirect(url_for('shelve'))
            
            elif shelf=="Wish List":
                # If product already exists in user's Wish List, show error and validation checks
                if "Wish List" in existingShelves:
                    msg = 'This product is already in your Wish List!'
                elif existingShelves:
                    msg = 'This product is already in your ' + existingShelves[0] + "!"
                # Product is not in any of the user's shelves
                else:
                    cursor = mysql.connection.cursor()
                    cursor.execute('INSERT INTO `Wishes` VALUES(%s, %s, %s)', (username, product_name, date,))
                    mysql.connection.commit()
                    msg = 'Successfully added product to Wish List!'
                    return redirect(url_for('wishlist'))

            else: # shelf == "Currently Using"
                # If product already exists in user's Currently Using products, show error and validation checks
                if "Currently Using" in existingShelves:
                    msg = 'This product is already in your Currently Using shelf!'
                elif existingShelves:
                    msg = 'This product is already in your ' + existingShelves[0] + "!"
                # Product is not in any of the user's shelves
                else:
                    return render_template('add.html', product_name=product_name, today_date=date) 

        # Form submitted is from Add page, to add product to Currently Using
        elif 'frequency_type' in request.form and 'routine_category' in request.form: 
            product_name = request.form['product_name']
            frequency_type = request.form['frequency_type']
            frequency = request.form['frequency']
            specific_days = request.form['specific_days']
            expiry_date = request.form['expiry_date']
            routine_category = request.form['routine_category']
            date = datetime.today().strftime('%Y-%m-%d')
            
            cursor = mysql.connection.cursor()
            cursor.execute(
                'INSERT INTO Uses VALUES(%s, %s, %s, %s, %s, %s, %s, %s)', 
                (username, product_name, frequency_type, frequency, specific_days, expiry_date, routine_category, date,))
            mysql.connection.commit()
            msg = 'Successfully added product to Currently Using!'

            return redirect(url_for('using'))
    
    return redirect(request.referrer)

# Helper method to check if product is already in one of user's shelves
def checkExistingShelf(username, product_name):
    existingShelves = []

    # Check if product is already in Shelved products
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Shelves WHERE username = %s AND product_name = %s', (username, product_name,))
    result = cursor.fetchone()
    if result:
        existingShelves.append("Shelved")

    # Check if product is already in Currently Using products
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Uses WHERE username = %s AND product_name = %s', (username, product_name,))
    result = cursor.fetchone()
    if result:
        existingShelves.append("Currently Using")

    # Check if product is already in Wish List
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Wishes WHERE username = %s AND product_name = %s', (username, product_name,))
    result = cursor.fetchone()
    if result:
        existingShelves.append("Wish List")
    
    return existingShelves

@app.route('/create', methods=['GET', 'POST'])
def create():
    return "Page for Create Product not created yet."

@app.route('/shelve', methods=['GET', 'POST'])
def shelve():
    return "kexin"

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    return "kexin"

@app.route('/using', methods=['GET', 'POST'])
def using():
    return "kexin"

if __name__ == "__main__":
    app.run(debug=True)

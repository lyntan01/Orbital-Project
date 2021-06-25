from flask import Flask, render_template, request, redirect, url_for, session, flash, Markup
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime, date, timedelta
import time
import math

app = Flask(__name__)
app.secret_key = 'benefit'

# database connection details (local)
# app.config['MYSQL_DB'] = 'The Curious Case Of Cosmetics'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'Jenojinv1630'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# database connection details (heroku)
app.config['MYSQL_DB'] = 'heroku_6a15b81e32c4217'
app.config['MYSQL_HOST'] = 'us-cdbr-east-04.cleardb.com'
app.config['MYSQL_USER'] = 'b8ee7e3fb778a2'
app.config['MYSQL_PASSWORD'] = '82cbd045'

# Intialize MySQL
mysql = MySQL(app)

#http://localhost:5000/
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/video', methods=['GET', 'POST'])
def video():
    return render_template('video.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('dashboard'))
    
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
            return render_template('login.html', msg=msg)

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
    else:
        return "Error: You are not logged in. Please log in to view this page."

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
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/using', methods=['GET', 'POST'])
def using():
    if 'loggedin' in session:
        products = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT DISTINCT brand, skincare_or_makeup, T1.product_name, used_date
                            FROM `Uses` AS T1
                            JOIN `Product` AS T2 
                            ON T1.product_name = T2.product_name
                            WHERE T1.username = %s''', (session['username'],))
        results = cursor.fetchall()
        for row in results:
            products.append(row)
        return render_template('using.html', products=products)
    else:
        return "Error: You are not logged in. Please log in to view this page."

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
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/deleteShelve/<string:product_name>', methods=['GET', 'POST'] )
def delete(product_name):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'DELETE FROM `Shelves` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
        mysql.connection.commit()
        flash("Item Deleted!")
        return redirect(url_for('shelve'))
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/deleteWishlist/<string:product_name>', methods=['GET', 'POST'] )
def deleteWishlist(product_name):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'DELETE FROM `Wishes` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
        mysql.connection.commit()
        flash("Item Deleted!")
        return redirect(url_for('wishlist'))
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/deleteUsing/<string:product_name>', methods=['GET', 'POST'] )
def deleteUsing(product_name):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'DELETE FROM `Uses` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
        mysql.connection.commit()
        flash("Item Deleted!")
        return redirect(url_for('using'))
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/edit/<string:prev_page>/<string:product_name>', methods=['GET', 'POST'] )
def edit(product_name, prev_page):
    if 'loggedin' in session:
        msg = ''
        date = datetime.today().strftime('%Y-%m-%d')
        if request.method == 'POST' and 'my_products_cat' in request.form :
            redirect_page = ''
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if prev_page == "Shelves":
                redirect_page = 'shelve'
                cursor.execute(
                    'DELETE FROM `Shelves` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
            elif prev_page == "Wishes":
                redirect_page = 'wishlist'
                cursor.execute(
                    'DELETE FROM `Wishes` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
            else:
                redirect_page = 'using'
                cursor.execute(
                    'DELETE FROM `Uses` WHERE username = %s AND product_name = %s', (session['username'], product_name,))
            mysql.connection.commit()

            product_category = request.form['my_products_cat'] 
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


            if product_category == "Shelve":
                cursor.execute(
                    'INSERT INTO `Shelves` VALUES (%s, %s, %s)', (session['username'], product_name, date, ))
            
            
            elif product_category == "Wish":
                cursor.execute(
                    'INSERT INTO `Wishes` VALUES (%s, %s, %s)', (session['username'], product_name, date, )) 
            
            elif product_category == "Using" and not 'frequency_type' in request.form:
                msg = 'Please fill in the Frequency of Usage field!'
                return render_template('edit.html', product_name=product_name, prev_page=prev_page, msg=msg, date=date)
                       
            elif product_category == "Using" and not 'routine_category' in request.form:
                msg = 'Please fill in the Routine Category field!'
                return render_template('edit.html', product_name=product_name, prev_page=prev_page, msg=msg,date=date)
            
            else:       
                expiry = request.form['expiry_date']
                frequency = request.form['frequency']
                specific_days = request.form['specific_days']
                frequency_type = request.form['frequency_type'] 
                routine_category = request.form['routine_category']

                if specific_days == "0": # default value
                    specific_days = generateSpecificDays(frequency_type, int(frequency))

                cursor.execute(
                    'INSERT INTO `Uses` VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (session['username'], product_name, frequency_type, frequency, specific_days, expiry, routine_category, date, ))

            mysql.connection.commit()
            flash("Update Successful!")
            return redirect(url_for(redirect_page))
        
        else: 
            if request.method == 'POST' and not 'my_products_cat' in request.form:
                msg = "Please fill in the Product Category field!"
            
            return render_template('edit.html', product_name=product_name, prev_page=prev_page, msg=msg, date=date)
    else:
            return "Error: You are not logged in. Please log in to view this page."

@app.route('/profile', methods=['GET', 'POST'])
@app.route('/<username>/profile', methods=['GET', 'POST'])
def profile(username=None):
    if 'loggedin' in session:
        # Display the user's own profile if no username specified
        if username == None:
            username = session['username']

        if request.method == 'GET':
            cursor = mysql.connection.cursor()
            cursor.execute(
                    'SELECT * FROM `Member User` WHERE username = %s', (username,))
            # Store user's information into a dictionary
            userInfo = cursor.fetchone()

            # Check that account exists, now find all reviews made by user
            if userInfo:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    '''SELECT r.product_name, p.brand, p.skincare_or_makeup, r.rating 
                    FROM Review r, Product p 
                    WHERE r.username = %s AND r.product_name = p.product_name 
                    ORDER BY p.brand, p.skincare_or_makeup, r.rating DESC''', (username,))
                # Store user's reviews into a dictionary
                reviews = cursor.fetchall()

        # Show user's profile with user's reviews (if any)
        return render_template('profile.html', username=username, userInfo=userInfo, reviews=reviews)
    else:
            return "Error: You are not logged in. Please log in to view this page."

@app.route('/search/<search_term>/<error_msg>', methods=['GET', 'POST'])
@app.route('/search/<search_term>', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def search(search_term=None, error_msg=None):
    if 'loggedin' in session:
        products = []
        # Check if 'search_term' POST request exists (user submitted form)
        if (request.method == 'POST' and 'search_term' in request.form) or search_term:
            if not search_term:
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
            return render_template('search.html', products=products, post=True, error_msg=error_msg, search_term=search_term)
        else:
            return render_template('search.html', products=products, post=False, error_msg=error_msg, search_term=search_term)
    else:
        return "Error: You are not logged in. Please log in to view this page."

# This method adds a product to one of the user's shelves, 
# then redirects the user to the page of the selected shelf
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'loggedin' in session:
        error_msg = None

        if request.method == 'POST': 
            # Form submitted is from Search page
            if 'product_name' in request.form and 'shelf' in request.form:
                product_name = request.form['product_name']
                shelf = request.form['shelf']
                date = datetime.today().strftime('%Y-%m-%d')

                existingShelves = checkExistingShelf(session['username'], product_name)
                cursor = mysql.connection.cursor()
                if shelf=="Shelved":
                    # If product already exists in user's Shelved products, show error and validation checks
                    if "Shelved" in existingShelves:
                        error_msg = 'This product has already been Shelved!'
                    elif existingShelves:
                        error_msg = 'This product is already in your ' + existingShelves[0] + "!"
                    # Product is not in any of the user's shelves
                    else:
                        cursor = mysql.connection.cursor()
                        cursor.execute('INSERT INTO `Shelves` VALUES(%s, %s, %s)', (session['username'], product_name, date,))
                        mysql.connection.commit()
                        flash('Successfully added product to Shelved!')
                        return redirect(url_for('shelve'))
                
                elif shelf=="Wish List":
                    # If product already exists in user's Wish List, show error and validation checks
                    if "Wish List" in existingShelves:
                        error_msg = 'This product is already in your Wish List!'
                    elif existingShelves:
                        error_msg = 'This product is already in your ' + existingShelves[0] + "!"
                    # Product is not in any of the user's shelves
                    else:
                        cursor = mysql.connection.cursor()
                        cursor.execute('INSERT INTO `Wishes` VALUES(%s, %s, %s)', (session['username'], product_name, date,))
                        mysql.connection.commit()
                        flash('Successfully added product to Wish List!')
                        return redirect(url_for('wishlist'))

                else: # shelf == "Currently Using"
                    # If product already exists in user's Currently Using products, show error and validation checks
                    if "Currently Using" in existingShelves:
                        error_msg = 'This product is already in your Currently Using!'
                    elif existingShelves:
                        error_msg = 'This product is already in your ' + existingShelves[0] + "!"
                    # Product is not in any of the user's shelves
                    else:
                        return render_template('add.html', product_name=product_name, today_date=date, error_msg=None) 
            
                search_term = request.form['search_term']
                return redirect(url_for('search', search_term=search_term, error_msg=error_msg))

            # Form submitted is from Add page, to add product to Currently Using
            else:
                if 'frequency_type' not in request.form:
                    error_msg = 'Please fill in the Frequency of Usage field!'
                    return render_template('add.html', product_name=request.form['product_name'], today_date=datetime.today().strftime('%Y-%m-%d'), error_msg=error_msg) 
                
                elif 'routine_category' not in request.form:
                    error_msg = 'Please fill in the Routine Category field!'
                    return render_template('add.html', product_name=request.form['product_name'], today_date=datetime.today().strftime('%Y-%m-%d'), error_msg=error_msg) 

                else:
                    product_name = request.form['product_name']
                    frequency_type = request.form['frequency_type']
                    frequency = request.form['frequency']
                    specific_days = request.form['specific_days']
                    expiry_date = request.form['expiry_date']
                    routine_category = request.form['routine_category']
                    date = datetime.today().strftime('%Y-%m-%d')

                    if specific_days == "0": # default value
                        specific_days = generateSpecificDays(frequency_type, int(frequency))
                    
                    cursor = mysql.connection.cursor()
                    cursor.execute(
                        'INSERT INTO Uses VALUES(%s, %s, %s, %s, %s, %s, %s, %s)', 
                        (session['username'], product_name, frequency_type, frequency, specific_days, expiry_date, routine_category, date,))
                    mysql.connection.commit()

                    flash('Successfully added product to Currently Using!')
                    return redirect(url_for('using'))         
    else:
            return "Error: You are not logged in. Please log in to view this page."

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

# Helper method to determine default specific days
def generateSpecificDays(frequency_type, num_of_times):
    max = 7 # if frequency_type == "Weekly"
    if frequency_type == "Monthly":
        max = 30
    interval = math.ceil(max/num_of_times)
    days = []
    for i in range(1, max+1, interval):
        days.append(i)
    
    if len(days) < num_of_times:
        interval = math.floor(max/num_of_times)
        days = []
        for i in range(1, max+1, interval):
            days.append(i)
    
    specific_days = ""
    for i in range(num_of_times):
        specific_days += str(days[i]) + ","
    specific_days = specific_days[:-1] # remove last comma
    
    return specific_days

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'loggedin' in session:
        error_msg = None

        if request.method == 'POST' and 'product_name' in request.form and 'brand' in request.form and 'skincare_or_makeup' in request.form:
            # Create variables for easy access
            product_name = request.form['product_name'].title().strip()
            brand = request.form['brand'].strip()
            skincare_or_makeup = request.form['skincare_or_makeup']
            average_rating = 0.00
            # photo = request.form['photo']

            # Check that product does not already exist in database
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM Product WHERE product_name = %s', (product_name,))
            result = cursor.fetchone()
            if result:
                error_msg = 'This product already exists in the database!'
            else:
                # Insert product into database
                cursor = mysql.connection.cursor()

                # Photo file uploaded by user
                # if len(photo) > 0: 
                #     cursor.execute('INSERT INTO Product VALUES(%s, %s, %s, %s, %s)', (product_name, brand, skincare_or_makeup, average_rating, photo, ))
                # No photo file uploaded
                # else:
                
                cursor.execute('INSERT INTO Product VALUES(%s, %s, %s, %s, null)', (product_name, brand, skincare_or_makeup, average_rating,))
                mysql.connection.commit()
                flash('Product successfully added to database!')
            
                return redirect(url_for('search',search_term=product_name))
            
        elif request.method == 'POST' and 'product_name' in request.form and 'brand' in request.form and 'skincare_or_makeup' not in request.form:
            error_msg = "Please fill in Type of product!"

        return render_template('create.html', error_msg=error_msg)
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/review/<string:product_name>', methods=['GET', 'POST'])
def review(product_name):

    if 'loggedin' in session:
        error_msg = None

        if request.method == 'POST' and 'rating' in request.form:
            # Create variables for easy access
            rating = request.form['rating']

            # Check if user's review of that product already exists
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM Review WHERE username = %s AND product_name = %s', (session['username'], product_name,))
            result = cursor.fetchone()
            if result:
                error_msg = 'You have already left a review for this product!'
            else:
                # Insert new review into database
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO Review VALUES(%s, %s, %s)', (rating, session['username'], product_name,))
                mysql.connection.commit()
                # Update average rating of product in database
                cursor = mysql.connection.cursor()
                cursor.execute(
                    '''UPDATE Product 
                    SET average_rating = (SELECT ROUND(AVG(rating),2) FROM Review WHERE product_name = %s) 
                    WHERE product_name = %s''', (product_name, product_name,))
                mysql.connection.commit()

                flash('Review successfully added!')
            
                return redirect(url_for('search', search_term=product_name))
        return render_template('review.html', product_name=product_name, error_msg=error_msg)
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:

        # Find Currently Using products which are expiring in the next 30 days
        new_date = date.today() + timedelta(days=30) 
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT p.brand, u.product_name, u.expiry_date 
                        FROM Product p, Uses u
	                    WHERE p.product_name = u.product_name 
                            AND username = %s 
                            AND expiry_date >= %s AND expiry_date <= %s
                        ORDER BY expiry_date''', (session['username'], date.today(), new_date,))
        expiring_products = cursor.fetchall()

        # For each product, add number of days from today to the expiry date
        for product in expiring_products:
            num_days_left = product["expiry_date"] - date.today()
            product["num_days_left"] = num_days_left.days
        
        # Find Day Routine products of user
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT p.brand, u.product_name, u.frequency_type, u.specific_days 
                        FROM Product p, Uses u
                        WHERE p.product_name = u.product_name 
                            AND username = %s
                            AND (routine_category = 'Day' OR routine_category = 'Both')
                        ORDER BY FIELD(frequency_type, 'Daily', 'Weekly', 'Monthly')''', (session['username'],))
        day_routine_tuple = cursor.fetchall()
        day_routine = []

        # Filter Day Routine products for that particular day
        for product in day_routine_tuple:

            if product["frequency_type"] == "Daily":
                day_routine.append(product)
            else:
                specific_days = product["specific_days"].split(",")

                # Check if product should be used on this day of the week
                day_of_week = str(date.today().isoweekday())
                if product["frequency_type"] == "Weekly" and day_of_week in specific_days: 
                    day_routine.append(product)

                # Check if product should be used on this day of the month
                day_of_month = str(date.today().day)
                if product["frequency_type"] == "Monthly" and day_of_month in specific_days: 
                    day_routine.append(product)

        # Find Day Routine products of user
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT p.brand, u.product_name, u.frequency_type, u.specific_days 
                        FROM Product p, Uses u
                        WHERE p.product_name = u.product_name 
                            AND username = %s
                            AND (routine_category = 'Night' OR routine_category = 'Both')
                        ORDER BY FIELD(frequency_type, 'Daily', 'Weekly', 'Monthly')''', (session['username'],))
        night_routine_tuple = cursor.fetchall()
        night_routine = []

        # Filter Day Routine products for that particular day
        for product in night_routine_tuple:

            if product["frequency_type"] == "Daily":
                night_routine.append(product)
            else:
                specific_days = product["specific_days"].split(",")

                # Check if product should be used on this day of the week
                day_of_week = str(date.today().isoweekday())
                if product["frequency_type"] == "Weekly" and day_of_week in specific_days: 
                    night_routine.append(product)

                # Check if product should be used on this day of the month
                day_of_month = str(date.today().day)
                if product["frequency_type"] == "Monthly" and day_of_month in specific_days: 
                    night_routine.append(product)

        return render_template('dashboard.html', username=session['username'], expiring_products=expiring_products, 
            day_routine=day_routine, night_routine=night_routine, date=date.today())
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    if 'loggedin' in session:
        products = []
        # Check if 'skincare_or_makeup' POST request exists (user submitted form)
        if request.method == 'POST' and 'skincare_or_makeup' in request.form:
            type = request.form['skincare_or_makeup']
            # Get top 10 products by average rating using MySQL
            cursor = mysql.connection.cursor()
            cursor.execute(
                '''SELECT product_name, brand, average_rating 
                FROM Product 
                WHERE skincare_or_makeup = %s
                ORDER BY average_rating DESC LIMIT 10''', (type,))
            # Store search results into a dictionary
            products = cursor.fetchall()
            return render_template('leaderboard.html', products=products, type=type)
        else:
            return render_template('leaderboard.html', products=products, type=None)
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT Count(*) AS Count FROM `Forum Thread`''')
        countThreads = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT Count(DISTINCT username) AS Count FROM `Forum Thread`''')
        countUsers = cursor.fetchone()

        username = session['username']

        posts = []
        numReplies = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'search_term' in request.form:
            search = request.form['search_term']
            filterThread = request.form['filter']
            if filterThread == 'Titles':
                cursor.execute('SELECT * FROM `Forum Thread` WHERE title LIKE %s ORDER BY post_date DESC', (f'%{search}%',))
            if filterThread == 'Descriptions':
                cursor.execute('SELECT * FROM `Forum Thread` WHERE description LIKE %s ORDER BY post_date DESC', (f'%{search}%',))
        else:
            cursor.execute('''SELECT * FROM `Forum Thread` ORDER BY post_date DESC''')

        results = cursor.fetchall()
        for row in results:
            posts.append(row)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT COUNT(reply_ID) AS count FROM `Forum Reply` WHERE thread_ID = %s', (row['thread_ID'],))
            adder = cursor.fetchone()
            numReplies.append(adder)

        return render_template('forum.html', posts=posts, username=username, countThreads=countThreads, countUsers=countUsers, numReplies=numReplies)

    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/reply/<string:thread_ID>', methods = ['GET', 'POST'])
def reply(thread_ID):
    if 'loggedin' in session:
        if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT max(reply_ID) AS Maximum from `Forum Reply` WHERE thread_ID = %s', (thread_ID,))
            biggest_ID = cursor.fetchone()
            if biggest_ID['Maximum']!= None:
                biggest_ID = biggest_ID['Maximum'] + 1
            else:
                biggest_ID = 1

            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            comment = request.form['comment']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''INSERT INTO `Forum Reply` VALUE(%s, %s, %s, %s, %s)''', (biggest_ID, thread_ID, session['username'], comment, date,))
            mysql.connection.commit()
            flash('Reply added!')

        username = session['username']
        posts = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT * FROM `Forum Thread` WHERE thread_ID = %s''', (thread_ID,))
        thread = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT * FROM `Forum Reply` WHERE thread_ID = %s ORDER BY post_date DESC''', (thread_ID,))
        results = cursor.fetchall()
        for row in results:
            posts.append(row)
        return render_template('reply.html', posts=posts, thread=thread, username=username, thread_ID = thread_ID)

    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/deleteReply/<string:thread_ID>/<string:reply_ID>', methods=['GET', 'POST'] )
def deleteReply(thread_ID, reply_ID):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'DELETE FROM `Forum Reply` WHERE thread_ID= %s AND reply_ID = %s', (thread_ID, reply_ID,))
        mysql.connection.commit()
        flash("Reply Deleted!")

        username = session['username']
        posts = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT * FROM `Forum Thread` WHERE thread_ID = %s''', (thread_ID,))
        thread = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT * FROM `Forum Reply` WHERE thread_ID = %s ORDER BY post_date DESC''', (thread_ID,))
        results = cursor.fetchall()
        for row in results:
            posts.append(row)
    
        return redirect(url_for('reply', posts=posts, thread=thread, username=username, thread_ID=thread_ID))
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/deleteThread/<string:thread_ID>', methods=['GET', 'POST'] )
def deleteThread(thread_ID):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'DELETE FROM `Forum Thread` WHERE username = %s AND thread_ID = %s', (session['username'], thread_ID,))
        mysql.connection.commit()
        flash("Thread Deleted!")
        return redirect(url_for('forum'))
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/addThread', methods=['GET', 'POST'] )
def addThread():
    if 'loggedin' in session:
        if request.method == 'POST' and 'title' in request.form and 'description' in request.form:
            title = request.form['title']
            description = request.form['description']
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT max(thread_ID) AS Maximum from `Forum Thread`')
            biggest_ID = cursor.fetchone()
            if biggest_ID['Maximum']!= None:
                biggest_ID = biggest_ID['Maximum'] + 1
            else:
                biggest_ID = 1


            cursor.execute('INSERT INTO `Forum Thread` VALUES (%s, %s, %s, %s, %s)', (biggest_ID, session['username'], title, description, date,))
            mysql.connection.commit()

            flash("Thread Added!")
            return redirect(url_for('forum'))
        else:
            msg = ''
            if request.method == 'POST' and not ('title' in request.form or 'description' in request.form):
                msg = 'Fill in the Title/Description field!'
            return render_template('addThread.html', msg = msg)
    else:
        return "Error: You are not logged in. Please log in to view this page."

@app.route('/logout')
def logout():
    if 'loggedin' in session:
        # Remove session data, this will log the user out
        session.pop('loggedin', None)
        session.pop('member_id', None)
        session.pop('name', None)
        # Redirect to login page
        return redirect(url_for('index'))
    else:
        return "Error: You are not logged in. Please log in to view this page."

if __name__ == "__main__":
    app.run(debug=True)




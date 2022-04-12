from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'random'

db = pymysql.connect(host ='localhost',
					user = 'admin',							
					password = 'admin',
					db = 'mybookshop')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/product/')
def product():
    return render_template('product.html')

@app.route('/register/' ,methods=['GET', 'POST'])
def register():
	# Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
       	# Check if account exists using MySQL
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
        	return 'Username already have'
        else:
        	# Account doesnt exists and the form data is valid, now insert new account into accounts table
        	cursor = db.cursor(pymysql.cursors.DictCursor)
        	cursor.execute('INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `phoneNo`) VALUES (Null, %s, %s, '', '')', (username, password,))
        	db.commit()
        	return 'Created account'
        	
    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    #Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using pyMySQL
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account['username']
            session['password'] = account['password']
            # Redirect to profile page
            return redirect(url_for('profile'))
        else:
        	return 'Incorrect username or password'
    return render_template('login.html')

@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
    	cursor = db.cursor(pymysql.cursors.DictCursor)
    	cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['username'],))
    	account = cursor.fetchone()
    	return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/update', methods=['POST'])
def update():
	if request.method == 'POST' and 'email' in request.form and 'phoneNo' in request.form:
		email = request.form['email']
		phoneNo = request.form['phoneNo']
		# Check if user is loggedin
		if 'loggedin' in session:
			cursor = db.cursor(pymysql.cursors.DictCursor)
			cursor.execute('UPDATE `accounts` SET email = %s, phoneNo = %s WHERE `accounts`.`username` = %s', (email, phoneNo, session['username'],))
			account = cursor.fetchone()
			db.commit()
			return 'Update success'

@app.route('/delete/', methods = ['POST','GET'])
def delete():
    cursor = db.cursor(pymysql.cursors.DictCursor)
  	
    cursor.execute('DELETE FROM accounts WHERE username = %s', (session['username'],))
    db.commit()
    return 'Account Removed Successfully'
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
	# Remove session data, this will log the user out
	session.pop('loggedin', None)
	session.pop('username', None)
	session.pop('password', None)
	# Redirect to login page
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.debug = True;
	app.run(port='8000')
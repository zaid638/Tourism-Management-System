from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from temp_db import read_db, save_db, package

app = Flask(__name__)

app.secret_key = '22154'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'Zaid'
app.config['MYSQL_PASSWORD'] = '22155'
app.config['MYSQL_DB'] = 'tourism'


mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/packages")
def packages():

    cursor1 = mysql.connection.cursor()
    cursor1.execute("SELECT * FROM packages")
    result1 = cursor1.fetchall()

    pkges = []

    for i in result1:
        sub = []
        sub.append(i[0])
        sub.append(i[1])
        cursor2 = mysql.connection.cursor()
        cursor2.execute(f"SELECT location_name FROM locations where package_id={i[0]}")
        result2 = cursor2.fetchall()
        loc = []
        for j in result2:
            loc.append(j[0])
        sub.append(loc)
        sub.append(i[2])
        sub.append(i[3])
        pkges.append(sub)        
    return render_template("packages.html", pkge=pkges)



@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE user_name = % s AND password = % s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['first_name'].upper()
            session['id'] = account['user_id']
            msg = 'Logged in successfully !'
            return redirect(url_for('userpackages'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)




@app.route('/userpackages')
def userpackages():

    cursor1 = mysql.connection.cursor()
    cursor1.execute("SELECT * FROM packages")
    result1 = cursor1.fetchall()

    pkges = []

    for i in result1:
        sub = []
        sub.append(i[0])
        sub.append(i[1])
        cursor2 = mysql.connection.cursor()
        cursor2.execute(f"SELECT location_name FROM locations where package_id={i[0]}")
        result2 = cursor2.fetchall()
        loc = []
        for j in result2:
            loc.append(j[0])
        sub.append(loc)
        sub.append(i[2])
        sub.append(i[3])
        pkges.append(sub)        
    return render_template("packages2.html", pkge=pkges)


@app.route('/')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return render_template('index.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'firstname' in request.form and 'password' in request.form and 'email' in request.form and 'lastname' in\
    request.form and 'phoneno' in request.form and 'username' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phoneno = request.form['phoneno']
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_name = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s, % s, % s, % s)',
                           (firstname, lastname, email, phoneno, username, password, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('login.html', msg=msg)
        
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)
    


@app.route("/history")
def history():

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT booking_id, package_id, booking_date, number_of_tickets, status FROM bookings  WHERE user_id = % s', (session['id'], ))
    result = cursor.fetchall()
       
    return render_template("booking_history.html", data=result)





if __name__ == '__main__':
    app.run(debug=True)
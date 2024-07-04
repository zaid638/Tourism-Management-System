from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime

app = Flask(__name__)

app.secret_key = '22154'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Amna2003@'
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
        cursor2.execute(f"SELECT location_name FROM view_packages where package_id={i[0]}")
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
        cursor2.execute(f"SELECT location_name FROM view_packages where package_id={i[0]}")
        result2 = cursor2.fetchall()
        loc = []
        for j in result2:
            loc.append(j[0])
        sub.append(loc)
        sub.append(i[2])
        sub.append(i[3])
        pkges.append(sub)        
    return render_template("userpackages.html", pkge=pkges)


@app.route('/')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('id', None)
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
    


@app.route("/history", methods=['GET', 'POST'])
def history():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT booking_id, package_id, booking_date, number_of_tickets, status FROM bookings  WHERE user_id = % s ORDER BY booking_id DESC', (session['id'], ))
    result = cursor.fetchall()       
    return render_template("booking_history.html", data=result)


@app.route('/booking', methods=['GET', 'POST'])
def booking():

    if request.method == 'POST' and 'PackageID' in request.form and 'Tickets' in request.form:
        PackageID = request.form['PackageID']
        Ticket = request.form['Tickets']
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if not re.match(r'[0-9]+', Ticket):
            msg = 'name must contain only numbers !'
        else:
            cursor2.execute('INSERT INTO bookings VALUES (NULL, % s, % s, % s, % s, % s)',
                           (PackageID, session['id'], datetime.datetime.now().strftime("%Y-%m-%d"), Ticket, "pending", ))
            mysql.connection.commit()
            msg = 'You have successfully booked we will confirm your bookng in 24 hrs!'
            return redirect(url_for('history'))
        
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    pkgID = request.form['pkgID']
    pkgName = request.form['pkgName']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT location_name, discription FROM locations, package_details WHERE locations.location_id = package_details.location_id AND package_details.package_id = % s', (pkgID, ))
    result = cursor.fetchall()

    return render_template('booking_form.html', data = result, data2 = pkgName, data3 = pkgID)



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    cursor1 = mysql.connection.cursor()
    cursor2 = mysql.connection.cursor() 
    cursor3 = mysql.connection.cursor()  
    cursor4 = mysql.connection.cursor()
    cursor1.execute('SELECT count(*) FROM users')
    cursor2.execute('SELECT count(*) FROM packages')
    cursor3.execute('SELECT count(*) FROM bookings')
    cursor4.execute('SELECT count(*) FROM bookings where status="pending"')
    USERS = cursor1.fetchone()    
    PACKAGES = cursor2.fetchone()        
    BOOKINGS = cursor3.fetchone()        
    PENDING = cursor4.fetchone()        
    return render_template('admin_home.html', users=USERS, packages=PACKAGES, bookings=BOOKINGS, pending=PENDING)



@app.route("/manage_users", methods=['GET', 'POST'])
def manage_users():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()       
    return render_template("manage_users.html", data=result)


@app.route("/manage_bookings", methods=['GET', 'POST'])
def manage_bookings():

    if request.method == 'POST' and 'bkID' in request.form:
        bookingID = request.form['bkID']
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute(f'UPDATE bookings SET status = "confirmed" WHERE booking_id = {bookingID}')
        mysql.connection.commit()
        return redirect(url_for('manage_bookings'))
        

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM bookings ORDER BY booking_id DESC')
    result = cursor.fetchall()
       
    return render_template("manage_bookings.html", data=result)



@app.route("/manage_packages_add", methods=['GET', 'POST'])
def manage_packages_add():

    if request.method == 'POST' and 'PackageName' in request.form and 'Location1' in request.form and 'Location2' in request.form\
        and 'Location3' in request.form and 'Days' in request.form and 'Amount' in request.form and 'pkID' in request.form:
        PackageID = request.form['pkID']
        PackageName = request.form['PackageName']
        Location1 = request.form['Location1']
        Location2 = request.form['Location2']
        Location3 = request.form['Location3']
        Days = request.form['Days']
        Amount = request.form['Amount']

        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('INSERT INTO package_details VALUES (% s, % s, % s, % s, % s)',(int(PackageID)+1, PackageName, Location1, Days, Amount))
        cursor2.execute('INSERT INTO package_details VALUES (% s, % s, % s, % s, % s)',(int(PackageID)+1, PackageName, Location2, Days, Amount))
        cursor2.execute('INSERT INTO package_details VALUES (% s, % s, % s, % s, % s)',(int(PackageID)+1, PackageName, Location3, Days, Amount))
        cursor2.execute('INSERT INTO packages VALUES (Null, % s, % s, % s)',(PackageName, Days, Amount)) 
        mysql.connection.commit()
        return redirect(url_for('manage_packages_add'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM view_packages')
    result = cursor.fetchall()

    cursor.execute('SELECT location_id FROM locations')
    result2 = cursor.fetchall()
       
    return render_template("manage_packages_add.html", data=result, len=len(result), data2=result2)



@app.route("/manage_packages_delete", methods=['GET', 'POST'])
def manage_packages_delete():

    if request.method == 'POST' and 'PackageID' in request.form:
        PackageID = request.form['PackageID']


        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute(f'DELETE FROM package_details WHERE package_id = {PackageID}')
        cursor2.execute(f'DELETE FROM packages WHERE package_id = {PackageID}') 
        mysql.connection.commit()
        return redirect(url_for('manage_packages_delete'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM view_packages')
    result = cursor.fetchall()

    cursor.execute('SELECT package_id FROM packages')
    result2 = cursor.fetchall()
       
    return render_template("manage_packages_delete.html", data=result, len=len(result), data2=result2)



@app.route("/manage_locations_add", methods=['GET', 'POST'])
def manage_locations_add():

    if request.method == 'POST' and 'Location' in request.form and 'Country' in request.form and 'Description' in request.form:
        Location = request.form['Location']
        Country = request.form['Country']
        Description = request.form['Description']

        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('INSERT INTO locations VALUES (NULL, % s, % s, % s)',
                        (Location, Country, Description))
        mysql.connection.commit()
        return redirect(url_for('manage_locations_add'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT location_id, location_name, country, discription FROM locations')
    result = cursor.fetchall()
       
    return render_template("manage_locations_add.html", data=result, len=len(result))


@app.route("/manage_locations_update", methods=['GET', 'POST'])
def manage_locations_update():

    if request.method == 'POST' and 'LocationID' in request.form and 'Location' in request.form and 'Country' in request.form and 'Description' in request.form:
        LocationID = request.form['LocationID']
        Location = request.form['Location']
        Country = request.form['Country']
        Description = request.form['Description']

        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute(f'UPDATE locations SET location_name = "{Location}", country = "{Country}", discription = "{Description}" WHERE location_id = {LocationID}')
        mysql.connection.commit()
        return redirect(url_for('manage_locations_update'))    

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT location_id, location_name, country, discription FROM locations')
    result = cursor.fetchall()
       
    return render_template("manage_locations_update.html", data=result, len=len(result))


@app.route("/manage_locations_delete", methods=['GET', 'POST'])
def manage_locations_delete():

    if request.method == 'POST' and 'LocationID' in request.form:
        LocationID = request.form['LocationID']

        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute(f'DELETE FROM locations WHERE location_id = {LocationID}')
        mysql.connection.commit()
        return redirect(url_for('manage_locations_delete'))       

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT location_id, location_name, country, discription FROM locations')
    result = cursor.fetchall()
       
    return render_template("manage_locations_delete.html", data=result, len=len(result))



if __name__ == '__main__':
    app.run(debug=True)

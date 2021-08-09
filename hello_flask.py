from flask import Flask, render_template, request, session, url_for, redirect,flash
import pymysql

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                               user='root',
                               password='',
                               database='airport')
@app.route('/')
def initsearch():

    return render_template('index.html')

@app.route('/searchflight', methods=['GET','POST'])
def searchflight():
    departure_city = request.form['From']
    arrive_city = request.form['To']
    session['departure_city'] = departure_city
    session['arrive_city'] = arrive_city

    # cursor = conn.cursor()
    #
    # query = 'SELECT flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city,\
    #         arrive_airport,arrival_time,price\
    #         FROM flight, airport A1, airport A2\
    #         WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming" \
    #         AND A1.city=\'{}\' and A2.city = \'{}\' \
    #         ORDER BY departure_time'
    #
    # cursor.execute(query.format(departure_city, arrive_city))
    # data = cursor.fetchone()
    # cursor.close()
    # error = None

    # if (data):
        # see if there's eligible flight
    return redirect(url_for('showflight'))

    # else:
        # returns an error message to the html page
        # flash('No eligible flight')
        # return redirect('/')

@app.route('/showflight')
def showflight():
    departure_city = session['departure_city']
    arrive_city = session['arrive_city']
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city,\
            arrive_airport,arrival_time,price\
            FROM flight, airport A1, airport A2\
            WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming" \
            AND A1.city=\'{}\' and A2.city = \'{}\' \
            ORDER BY departure_time'
    cursor.execute(query.format(departure_city,arrive_city))
    data = cursor.fetchall()
    cursor.close()
    return render_template('index.html', flights=data)


@app.route('/backtosearch')
def backtosearch():
    session.pop('departure_city')
    session.pop('arrive_city')
    return redirect('/')

@app.route('/login')
def login():
    return render_template('yz_login.html')



@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    usertype = request.form['usertype']
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    if usertype == 'customer':
        query = "SELECT * FROM customer WHERE email = \'{}\' and pass_word = \'{}\'"
    elif usertype == 'agent':
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' and pass_word = \'{}\'"
    elif usertype == 'staff':
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' and pass_word = \'{}\'"

    cursor.execute(query.format(username, password))
    userdata = cursor.fetchall()

    cursor.close()

    if userdata:
        session['username'] = username
        session['usertype'] = usertype
        if usertype == 'staff':
            return redirect(url_for('staff_home'))
        elif usertype == 'agent':
            return redirect(url_for('agent_home'))
        elif usertype == 'customer':
            return redirect(url_for('customer_home'))

    else:
        flash('Invalid login or username.')
        return redirect('/')

@app.route('/customer_home')
def customer_home():
    return render_template('customer_home.html')

@app.route('/staff_home')
def staff_home():
    return render_template('staff_home.html')

@app.route('/agent_home')
def agent_home():
    return render_template('agent_home.html')

@app.route('/register_customer')
def register_customer():
    return render_template('register_customer.html')

@app.route('/registerAuth_C')
def registerAuth_C():
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    phone = request.form['phone']
    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    building = request.form['building']
    dob = request.form['dob']
    passport_country = request.form['passport_country']
    passport_number = request.form['passport_number']
    expiration_date = request.form['expiration_date']

    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM customer WHERE email = \'{}\'"
    cursor.execute(query.format(email))
    cdata = cursor.fetchall()
    if cdata>0: #check if this email has been registered
        error = "This email has already been registered, please login"
        return render_template('register_customer.html',error=error)

    else: #Insert customer info into DB
        cursor = conn.cursor()
        query_insert = "INSERT INTO customer VALUES(\'{}\', \'{}\', md5(\'{}\'),\
         \'{}\', \'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\', \'{}\', \'{}\')"
        cursor.excute(query_insert.format(email, name, password, building, street, city, state, phone,
                                          passport_number, expiration_date, passport_country, dob))
        conn.commit()
        cursor.close()
        flash("Registration Done.")
        return redirect(url_for('/login'))



@app.route('/register_agent')
def register_agent():
    return render_template('register_agent.html')

@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():
    email = request.form['email']
    password = request.form['password']
    id = request.form['agent ID']

    cursor = conn.cursor()
    query = "SELECT * FROM booking_agent WHERE email = %s"
    cursor.execute(query, (email))
    data = cursor.fetchone()

    if(data):
        error = "This user already exists"
        return render_template('register_agent.html', error = error)
    else:
        ins = "INSERT INTO booking_agent VALUES(%s, md5(%s), %s)"
        cursor.execute(ins, (email, password, id))
        conn.commit()
        cursor.close()
        flash("Registration Done.")
        return redirect(url_for('init'))

@app.route('/register_staff')
def register_staff():
    return render_template('register_staff.html')

@app.route('/registerAuth_staff', methods=['GET', 'POST'])
def registerAuth_staff():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    dob = request.form['dob']
    airline = request.form['airline']

    cursor = conn.cursor()
    query = "SELECT * FROM airline_staff WHERE username = %s"
    cursor.execute(query, (username))
    data = cursor.fetchone()

    if(data):
        error = "This user already exists"
        return render_template('register_staff.html', error = error)
    else:
        ins = "INSERT INTO airline_staff VALUES(%s, md5(%s), %s, %s, %s, %s)"
        cursor.execute(ins, (username, password, first_name, last_name, dob, airline))
        conn.commit()
        cursor.close()
        flash("Registration Done.")
        return redirect(url_for('init'))


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
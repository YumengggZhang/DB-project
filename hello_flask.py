from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                               user='root',
                               password='',
                               database='Airport.co')


@app.route('/')
def initsearch():
    session.clear()
    return render_template('index.html')


@app.route('/searchflight', methods=['GET', 'POST'])
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
    cursor.execute(query.format(departure_city, arrive_city))
    data = cursor.fetchall()
    cursor.close()
    return render_template('index.html', flights=data)


@app.route('/backtosearch')
def backtosearch():
    session.pop('departure_city')
    session.pop('arrive_city')
    return redirect('/')


# ---------------------------------------LOGIN------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login_customer')
def login_customer():
    return render_template('login.html',login='customer')


@app.route('/login_agent')
def login_agent():
    return render_template('login.html',login='agent')


@app.route('/login_staff')
def login_staff():
    return render_template('login.html',login='staff')


@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # if request.method =='GET':
    #     return render_template('register.html')
    # if request.method == 'POST':
        # usertype = request.form['usertype']
    username = request.form.get("username")
    password = request.form.get('password')
    agent_id = request.form.get('agent_id')
    # print(username,password,agent_id)

    airline = request.form.get('airline')


    cursor = conn.cursor()
    if (not agent_id) and (not airline):
        query = "SELECT * FROM customer WHERE email = \'{}\' and pass_word = \'{}\'"
    elif agent_id:
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' and pass_word = \'{}\'"
    elif airline:
        query = "SELECT * FROM airline_staff WHERE username = \'{}\' and pass_word = \'{}\'"

    cursor.execute(query.format(username, password))
    userdata = cursor.fetchall()

    cursor.close()

    if userdata:
        session['username'] = username
        # session['usertype'] = usertype

        # session['nickname'] = userdata[0][1]  # refers to the 'name' attribute, used for home page

        if (not agent_id) and (not airline):
            session['nickname'] = userdata[0][1]
            return redirect(url_for('customer_home'))
        elif agent_id:
            session['nickname'] = userdata[0][1]
            session['agent_id'] = agent_id
            return redirect(url_for('agent_home'))
        elif airline:
            session['airline'] = airline
            session['nickname'] = username
            return redirect(url_for('staff_home'))

    else:
        flash('Invalid login or username.')
        return redirect('/')


#------------------------------------ HOME PAGE----------------------------------------------
@app.route('/customer_home')
def customer_home():
    return render_template('customer_home.html', username=session['nickname'])


@app.route('/staff_home')
def staff_home():
    return render_template('staff_home.html', username=session['nickname'])


@app.route('/agent_home')
def agent_home():
    return render_template('agent_home.html', username=session['nickname'])


#----------------------------------------REGISTER----------------------------------------------
@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_customer')
def register_customer():
    return render_template('register.html', register='customer')


@app.route('/register_agent')
def register_agent():
    return render_template('register.html', register='agent')


@app.route('/register_staff')
def register_staff():
    return render_template('register.html', register='staff')


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
        return render_template('register.html',error=error)

    else: #Insert customer info into DB
        cursor = conn.cursor()
        query_insert = "INSERT INTO customer VALUES(\'{}\', \'{}\', md5(\'{}\'),\
         \'{}\', \'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\', \'{}\', \'{}\')"
        cursor.excute(query_insert.format(email, name, password, building, street, city, state, phone,
                                          passport_number, expiration_date, passport_country, dob))
        conn.commit()
        cursor.close()
        # flash("Registration Done.")
        return redirect(url_for('/login'))


@app.route('/registerAuth_A', methods=['GET', 'POST'])
def registerAuth_agent():
    email = request.form['email']
    password = request.form['password']
    id = request.form['agent ID']

    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM booking_agent WHERE email = \'{}\'"
    cursor.execute(query.format(email))
    adata = cursor.fetchone()

    if adata>0: #check if this email has been registered
        error = "This email has already been registered, please login"
        return render_template('register.html', error=error,register='agent')
    else:
        insert_query = "INSERT INTO booking_agent VALUES(\'{}\', md5(\'{}\'), \'{}\')"
        cursor.execute(insert_query.format(email, password, id))
        conn.commit()
        cursor.close()
        # flash("Registration Done.")
        return redirect(url_for('/login'))


@app.route('/registerAuth_S', methods=['GET', 'POST'])
def registerAuth_staff():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    dob = request.form['dob']
    airline = request.form['airline']


    cursor = conn.cursor()
    query = "SELECT COUNt(*) FROM airline_staff WHERE username = \'{}\'"
    cursor.execute(query.format(username))
    sdata = cursor.fetchone()

    if sdata>0: #check if this email has been registered
        error = "This username has already been registered, please login"
        return render_template('register.html',error=error,register='staff')
    else:
        insert_query = "INSERT INTO airline_staff VALUES(\'{}\', md5(\'{}\'), \'{}\', \'{}\', \'{}\', \'{}\')"
        cursor.execute(insert_query, (username, password, first_name, last_name, dob, airline))
        conn.commit()
        cursor.close()
        # flash("Registration Done.")
        return redirect(url_for('/login'))


@app.route('/cviewAll')
def cview_all():
    # return redirect(url_for(customer_home), cview='all')
    return render_template('customer_home.html', username=session['nickname'], cview='all')


@app.route('/customer/searchAll', methods=['GET', 'POST'])
def customer_search_all():
    # if request.method == 'GET':
    departure_city = request.form['From']
    arrive_city = request.form['To']
    session['departure_city'] = departure_city
    session['arrive_city'] = arrive_city

    departure_city = session['departure_city']
    arrive_city = session['arrive_city']
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city,\
            arrive_airport,arrival_time,price\
            FROM flight, airport A1, airport A2\
            WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming" \
            AND A1.city=\'{}\' and A2.city = \'{}\' \
            ORDER BY departure_time'
    cursor.execute(query.format(departure_city, arrive_city))
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_home.html', username=session['nickname'], cview='all', flights=data)


# check if the airplane is full
@app.route('/customer/verifyFlight')
def customer_verify_flight():
    # get data from query strings
    airline = request.args.get('airline')
    flight_num = request.args.get('flight_num')

    # query evaluation
    query = ''  # TODO
    seats_avail = 0

    # query execution
    cursor = conn.cursor()
    query = """
    select ( (select airplane.seats_amt
  from airplane, flight
  where airplane.airplane_id = flight.airplane_id
  and flight.airline_name = \'{0}\'  -- [0] can ba changed in Python
  and flight.flight_num = \'{1}\')  -- [1] can be changed in Python
  -
  (select count(ticket_id)
  from ticket
  where flight_airline_name = \'{0}\'  -- [2] can be changed in Python, and has to match [0]
  and flight_num = \'{1}\')  -- [3] can be changed in Python, and has to match [1]
) as num_seats_avail;  -- if the airplane is full, num_seats_avail will be 0; otherwise it will be a positive number
    """
    cursor.execute(query.format(airline, flight_num))
    seats_avail = cursor.fetchone()
    cursor.close()
    if seats_avail > 0:
        return redirect(url_for('customer/purchase'))
    error = 'We are sorry that there is no available seat on this flight. Please check later or purchase another one.'
    return redirect(url_for('cviewAll'), error=error)


@app.route('/customer/purchase', methods=['GET', 'POST'])
def customer_purchase():
    return render_template('purchase.html')
    # departure_city = request.form['From']
    # arrive_city = request.form['To']
    # session['departure_city'] = departure_city
    # session['arrive_city'] = arrive_city
    #
    # departure_city = session['departure_city']
    # arrive_city = session['arrive_city']
    # cursor = conn.cursor()
    # query = 'SELECT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city,\
    #         arrive_airport,arrival_time,price\
    #         FROM flight, airport A1, airport A2\
    #         WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming" \
    #         AND A1.city=\'{}\' and A2.city = \'{}\' \
    #         ORDER BY departure_time'
    # cursor.execute(query.format(departure_city, arrive_city))
    # data = cursor.fetchall()
    # cursor.close()
    # return render_template('customer_home.html', username=session['nickname'], cview='all', flights=data)


@app.route('/cviewMy', methods=['GET', 'POST'])
def cview_my():

    username= session['username']
    cursor = conn.cursor()
    query = 'SELECT DISTINCT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city,\
            arrive_airport,arrival_time,price\
            FROM flight NATURAL JOIN Ticket NATURAL JOIN purchases, airport A1, airport A2\
            WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming"\
            AND customer_email=\'{}\' \
            ORDER BY departure_time'
    cursor.execute(query.format(username))
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_home.html', username=session['nickname'], cview='my', flights=data)


@app.route('/cviewStats')
def cview_stats():
    return render_template('customer_home.html', username=session['nickname'], cview='stats')


# ------------------------------------Agent-----------------------------------------
@app.route('/aviewAll')
def aview_all():
    # return redirect(url_for(customer_home), cview='all')
    return render_template('agent_home.html', username=session['nickname'], aview='all')


@app.route('/agent/searchAll', methods=['GET', 'POST'])
def agent_search_all():
    departure_city = request.form['From']
    arrive_city = request.form['To']
    session['departure_city'] = departure_city
    session['arrive_city'] = arrive_city

    departure_city = session['departure_city']
    arrive_city = session['arrive_city']
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city,\
            arrive_airport,arrival_time,price\
            FROM flight, airport A1, airport A2\
            WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming" \
            AND A1.city=\'{}\' and A2.city = \'{}\' \
            ORDER BY departure_time'
    cursor.execute(query.format(departure_city, arrive_city))
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_home.html', username=session['nickname'], aview='all', flights=data)


@app.route('/aviewMy')
def aview_my():
    return render_template('agent_home.html', username=session['nickname'], aview='my')


@app.route('/aviewStats')
def aview_stats():
    return render_template('agent_home.html', username=session['nickname'], aview='stats')

#——----------------------------------------------------Airline Staff--------------------------------------------------------
@app.route('/sadd')
def s_add():
    # return redirect(url_for(customer_home), cview='all')
    return render_template('staff_home.html', username=session['nickname'], s='add')


@app.route('/sviewMy', methods=['GET', 'POST'])
def staff_view_my():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM flight\
            WHERE airline_name IN (SELECT airline_name FROM airline_staff WHERE username=\'{}\')'
    cursor.execute(query.format(username))
    print(username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_home.html', username=session['nickname'], s='viewMy', flights=data)


@app.route('/sstats')
def staff_stats():
    return render_template('staff_home.html', username=session['nickname'], s='stats')


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

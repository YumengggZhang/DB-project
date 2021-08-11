from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql
import datetime

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
    if departure_city:
        ctd1 = 'A1.city=\'{}\''.format(departure_city)
    else:
        ctd1 = True

    if arrive_city:
        ctd2 = 'A2.city=\'{}\''.format(arrive_city)
    else:
        ctd2 = True

    query = """
    SELECT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city, 
    arrive_airport,arrival_time,price 
    FROM flight, airport A1, airport A2
    WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming"
    AND {0} AND {1}
    ORDER BY departure_time""".format(ctd1, ctd2)

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


@app.route('/registerAuth_C', methods=['GET', 'POST'])
def registerAuth_customer():
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    phone = request.form['phone']
    state = request.form['state']
    city = request.form['city']
    street = request.form.get('street')
    building = request.form.get('building')
    dob = request.form.get('dob')
    passport_country = request.form.get('passport_country')
    passport_number = request.form.get('passport_number')
    expiration_date = request.form.get('expiration_date')

    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM customer WHERE email = \'{}\'"
    cursor.execute(query.format(email))
    cdata = cursor.fetchall()
    if cdata>0: #check if this email has been registered
        error = "This email has already been registered, please login"
        return render_template('register.html', error=error)

    else: #Insert customer info into DB
        cursor = conn.cursor()
        query_insert = "INSERT INTO customer VALUES(\'{}\', \'{}\',\'{}\',\
         \'{}\', \'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\', \'{}\', \'{}\')"
        cursor.excute(query_insert.format(email, name, password, building, street, city, state, phone,
                                          passport_number, expiration_date, passport_country, dob))
        conn.commit()
        cursor.close()
        # flash("Registration Done.")
        return redirect(url_for('login'))


@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():

    email = request.form.get('email')
    password = request.form.get('password')
    id = request.form.get('agent_id')

    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM booking_agent WHERE email = \'{}\'"
    cursor.execute(query.format(email))
    adata = cursor.fetchone()
    print(adata)


    if adata[0]>0: #check if this email has been registered
        error = "This email has already been registered, please login"
        return render_template('register.html', error=error, register='agent')
    else:
        insert_query = "INSERT INTO booking_agent VALUES(\'{}\',\'{}\',\'{}\')"
        cursor.execute(insert_query.format(email, password,id))
        conn.commit()
        cursor.close()
        # flash("Registration Done.")
        return redirect(url_for('login'))


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

    if sdata[0]>0: #check if this email has been registered
        error = "This username has already been registered, please login"
        return render_template('register.html',error=error,register='staff')
    else:
        insert_query = "INSERT INTO airline_staff VALUES(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"
        cursor.execute(insert_query.format(username, password,first_name, last_name, dob, airline))
        conn.commit()
        cursor.close()
        # flash("Registration Done.")
        return redirect(url_for('/login'))


# ---------------------------------customer homepage------------------------------------
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

    # query execution
    cursor = conn.cursor()
    query = """
    SELECT seats_amt - count(Ticket_id) as capacity
FROM flight NATURAL JOIN airplane NATURAL JOIN Ticket
WHERE airline_name=\'{0}\' AND flight_num=\'{1}\' 
    """.format(airline, flight_num)
    cursor.execute(query)
    raw = cursor.fetchone()
    print(raw)
    seats_avail = raw[0]
    cursor.close()
    if seats_avail > 0:
        url = """/customer/purchase?airline=\'{0}\'&flight_num=\'{1}\'""".format(airline, flight_num)
        return redirect(url)
    error = 'We are sorry that there is no available seat on this flight. Please check later or purchase another one.'
    return redirect(url_for('cviewAll'))


@app.route('/customer/purchase', methods=['GET', 'POST'])
def customer_purchase():
    # get data from query strings
    airline = request.args.get('airline')
    flight_num = request.args.get('flight_num')
    session['airline'] = airline
    session['flight_num'] = flight_num
    # query execution
    cursor = conn.cursor()
    query1 = """
    SELECT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city, arrive_airport, arrival_time, price
    FROM flight, airport A1, airport A2
    WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name
    AND airline_name = {0} AND flight_num = {1}""".format(airline, flight_num)
    cursor.execute(query1)
    flight_info = cursor.fetchone()
    cursor.close()

    # get data from session
    email = session['username']
    # query execution
    cursor = conn.cursor()
    query2 = """
        SELECT email, name, phone_number, passport_number, passport_expiration, passport_country, date_of_birth
        FROM customer 
        WHERE email = \'{}\'
        """.format(email)
    cursor.execute(query2)
    customer_info = cursor.fetchone()
    cursor.close()

    return render_template('purchase.html', flight_info=flight_info, customer_info=customer_info, ba_info=None)


@app.route('/customer/confirmPurchase', methods=['GET', 'POST'])
def customer_confirm_purchase():
    # generate ticket ID
    cursor = conn.cursor()
    query0 = """
        SELECT max(ticket_id)
        FROM ticket
        """
    cursor.execute(query0)
    max_ticket_id = cursor.fetchone()[0]
    raw = int(max_ticket_id) + 1
    ticket_id = str(raw).zfill(4)
    cursor.close()

    # insert ticket
    airline = session['airline']
    flight_num = session['flight_num']
    cursor = conn.cursor()
    query1 = """
        INSERT INTO ticket VALUES(\'{0}\', {1}, {2})
        """.format(ticket_id, airline, flight_num)
    print(query1)
    cursor.execute(query1)
    conn.commit()
    cursor.close()

    # insert purchase
    email = session['username']
    cursor = conn.cursor()
    query2 = """
            INSERT INTO purchases VALUES(\'{0}\', \'{1}\', NULL)
            """.format(ticket_id, email)
    print(query2)
    cursor.execute(query2)
    conn.commit()
    cursor.close()

    # render success page

    # get ticket info
    cursor = conn.cursor()
    query3 = """
        SELECT *
        FROM ticket
        WHERE ticket_id = {0}""".format(ticket_id)
    print(query3)
    cursor.execute(query3)
    ticket_info = cursor.fetchone()
    cursor.close()

    # get flight info
    cursor = conn.cursor()
    query4 = """
    SELECT airline_name, flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city, arrive_airport, arrival_time, price
    FROM flight, airport A1, airport A2
    WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name
    AND airline_name = {0} AND flight_num = {1}""".format(airline, flight_num)
    cursor.execute(query4)
    flight_info = cursor.fetchone()
    cursor.close()

    return render_template('ticket.html', ticket_info=ticket_info, flight_info=flight_info)


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


# ------------------------------------Agent homepage-----------------------------------------
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

    username = session['username']
    cursor = conn.cursor()

    flight_query = 'SELECT *  FROM flight\
             WHERE flight_status = "upcoming"\
             AND (airline_name, flight_num) IN\
             (SELECT airline_name, flight_num  FROM ticket\
             WHERE ticket_id IN (SELECT ticket_id\
              FROM purchases WHERE booking_agent_email = \'{}\'))'
    cursor.execute(flight_query.format(username))
    flight_data = cursor.fetchall()

    cursor.close()

    return render_template('agent_home.html', username=session['nickname'], aview='my',
                           flights=flight_data)
                           # commision = commission_data,
                           # top_customer_list1 = top_customer_data1)


@app.route('/aviewStats')
def aview_stats():
    today = datetime.date.today()
    ly_today = today - datetime.timedelta(25*7)
    lm_today = today - datetime.timedelta(30)
    ly_today = ly_today.strftime('%y%m%d')
    str_today = today.strftime('%y%m%d')
    username = session['username']
    cursor = conn.cursor()

    commission_query = 'SELECT booking_agent_email,sum(price*0.1) as tot_commision,\
                       sum(price*0.1)/(COUNT(Ticket_id)) as avg_commsion, count(ticket_id) as ticket_sold\
                       FROM purchases NATURAL JOIN Ticket NATURAL JOIN flight\
                       WHERE transaction_date BETWEEN \'{}\' AND \'{}\'\
                       AND booking_agent_email = \'{}\' '

    cursor.execute(commission_query.format(lm_today, today, username))
    commission_data = cursor.fetchall()

    customer_query = 'SELECT customer_email,tickets_amt as t1 FROM (SELECT Customer_email,COUNT(Ticket_id) as tickets_amt\
       											FROM purchases\
                                                 	WHERE booking_agent_email = \'{}\'\
                                                   AND transaction_date BETWEEN \'{}\' AND \'{}\'\
                                                 	GROUP BY Customer_email) C1\
                         WHERE  5 > (SELECT count(customer_email) FROM (SELECT Customer_email,COUNT(Ticket_id) as tickets_amt\
       											FROM purchases\
                                                  WHERE booking_agent_email = \'{}\'\
                                                  AND transaction_date BETWEEN \'{}\' AND \'{}\'\
                                                  GROUP BY Customer_email) C2\
                         WHERE C2.tickets_amt> C1.tickets_amt)'
    cursor.execute(customer_query.format(username, ly_today, today, username, ly_today, today))
    top_5_customer_email = cursor.fetchall()
    top_5_customer_email_list = [line[0] for line in top_5_customer_email]
    top_customer_list1 = []
    customer_query2 = 'SELECT email,name,city,state,phone_number,date_of_birth \
                           FROM Customer\
                           WHERE email= \'{}\' '
    for customer in top_5_customer_email_list:
        cursor.execute(customer_query2.format(customer))
        customer_info = cursor.fetchone()
        top_customer_list1.append(customer_info)

    cursor.close()
    return render_template('agent_home.html', username=session['nickname'], aview='stats', commision_data = commission_data,
                           top_customer_list1 = top_customer_list1)


#——-------------------------------------------------Staff Homepage--------------------------------------------------------
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
    # print(username)
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

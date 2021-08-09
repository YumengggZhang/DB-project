from flask import Flask, render_template, request, session, url_for, redirect, flash
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
        query = "SELECT * FROM customer WHERE email = %s and password = %s"
    elif usertype == 'agent':
        query = "SELECT * FROM booking_agent WHERE email = %s and password = %s"
    elif usertype == 'staff':
        query = "SELECT * FROM airline_staff WHERE username = %s and password = %s"

    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()

    if (data):
        session['username'] = username
        session['user_type'] = usertype
        if usertype == 'staff':
            return redirect(url_for('staff_home'))
        elif usertype == 'agent':
            return redirect(url_for('agent_home'))
        elif usertype == 'customer':
            return redirect(url_for('customer_home'))

    else:
        flash('Invalid login or username.')
        return redirect('/')

@app.route('/register/customer')
def register_customer():
    return render_template('register_customer.html')

@app.route('/register/agent')
def register_agent():
    return render_template('register_agent.html')

@app.route('/register/staff')
def register_staff():
    return render_template('register_staff.html')

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
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

    return render_template('search.html')

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

    if (data):
        # see if there's eligible flight
        return redirect(url_for('showflight'))

    else:
        # returns an error message to the html page
        flash('No eligible flight')
        return redirect('/')

@app.route('/showflight')
def showflight():
    departure_city = session['departure_city']
    arrive_city = session['arrive_city']
    cursor = conn.cursor()
    query = 'SELECT flight_num, A1.city as depart_city, depart_airport, departure_time, A2.city as arrival_city,\
            arrive_airport,arrival_time,price\
            FROM flight, airport A1, airport A2\
            WHERE flight.depart_airport=A1.name AND flight.arrive_airport=A2.name AND flight_status="upcoming" \
            AND A1.city=\'{}\' and A2.city = \'{}\' \
            ORDER BY departure_time'
    cursor.execute(query.format(departure_city,arrive_city))
    data = cursor.fetchall()
    cursor.close()
    return render_template('flights_info.html', flights=data)


@app.route('/backtosearch')
def backtosearch():
    session.pop('departure_city')
    session.pop('arrive_city')
    return redirect('/')

app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
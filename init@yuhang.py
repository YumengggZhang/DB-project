# ------------------------------------------------------------------------------------

from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       database='airport')

# ------------------------------------------------------------------------------------


@app.route('/cviewAll')
def cview_all():
    return render_template('customer_home.html', cview='all')


@app.route('/cviewMy')
def cview_my():
    return render_template('customer_home.html', cview='my')


@app.route('/cviewStats')
def cview_stats():
    return render_template('customer_home.html', cview='stats')

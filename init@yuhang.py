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

@app.route('/')
def


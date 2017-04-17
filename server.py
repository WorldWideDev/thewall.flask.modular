from flask import Flask, render_template, redirect, flash, request as req, session
#from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
from apps.logreg import logReg
from apps.wall import wall

app = Flask(__name__)
app.register_blueprint(logReg)
app.register_blueprint(wall)
app.secret_key = 'secrettts'
#mysql = MySQLConnector(app, 'wall')


app.run(debug=True)

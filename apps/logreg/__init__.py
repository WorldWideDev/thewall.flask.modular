from flask import Flask, render_template, redirect, flash, request as req, session, Blueprint
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re

app = Flask(__name__)
mysql = MySQLConnector(app, 'the_wall')

logReg = Blueprint('logReg', __name__, template_folder='../templates', static_folder='static')

bcrypt = Bcrypt(app)

#REGEX VARS
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

@logReg.route('/')
def index():
    return render_template('index.html')

@logReg.route('/signup', methods=['POST'])
def handleSignup():
    valid = validateSignup()
    print valid
    if valid:
        print 'success'
        createUser(req.form)
        flash('Welcome, '+session['name']+'. Thanks for registering')
        return redirect('/wall')
    else:
        return redirect('/')

def createUser(newUser):
    hashed_pw = bcrypt.generate_password_hash(newUser['password'])
    print hashed_pw
    print newUser['first_name'], 'in create user'
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) \
            VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    data = {
        'first_name': newUser['first_name'],
        'last_name': newUser['last_name'],
        'email': newUser['email'],
        'password': hashed_pw
    }
    createdUserId = mysql.query_db(query, data)
    createdUser = mysql.query_db("SELECT id, first_name FROM users WHERE id = :createdUserId",
                { 'createdUserId':createdUserId})
    print createdUser, 'is created user'
    loginUser(createdUser)



@logReg.route('/login', methods=['POST'])
def handleLogin():
    validUser = validateLogin()
    if validUser['isValid']:
        loginUser(validUser['user'])
        flash("Welcome back, " + session['name'])
        return redirect('/wall')
    else:
        return redirect('/')

def loginUser(user):
    print user, 'is login user method'
    session['id'] = user[0]['id']
    session['name'] = user[0]['first_name']

@logReg.route('/logout')
def logout():
    session.clear()
    flash("You have succesfully logged out")
    return redirect('/')

def validateLogin():
    isValid = True
    print 'hi im in validate login'
    # check for sumbitted email in db
    query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    data = {'email': req.form['email']}
    logUser = mysql.query_db(query, data)
    # if query returns empty array, email doesn't exist
    print logUser
    if logUser == []:
        isValid = False
        flash("Email not in system")
    else:
        # check pw
        if not bcrypt.check_password_hash(logUser[0]['password'], req.form['password']):
            isValid = False
            flash("Incorrect Password")
    return {"isValid": isValid, "user": logUser}

def validateSignup():
    isValid = True;
    print req.form
    # first_name: letters only, at least 2 characters and that it was submitted
    # last_name: letters only, at least 2 characters and that it was submitted
    if len(req.form['first_name']) < 2 or len(req.form['last_name']) < 2:
        #flash("Names must be at least 2 characters")
        flash("Names must be at least 2 characters")
        isValid = False
    if not re.match(NAME_REGEX, req.form['first_name']):
        isValid = False
        flash("Names must be letters only")
    # email: valid email format
    if not re.match(EMAIL_REGEX, req.form['email']):
        isValid = False
        flash("Invalid Email")
    # password: at least 8 chars and that it was submitted
    if len(req.form['password']) < 8:
        isValid = False
        flash("Password must be at least 8 characters")
    # password confirm: matches password
    if req.form['password'] != req.form['pw_confirm']:
        isValid = False
        flash("Passwords don't match")

    return isValid

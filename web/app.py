
import pymongo
import bcrypt
import os
from functools import wraps
from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_mail import Mail,Message
from werkzeug.utils import secure_filename
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
mail = Mail(app)

s = URLSafeTimedSerializer('GOMOGOMONO...')

salt = b'$2b$11$Za4hFNuzn3Rvw7gLnUVZCu'

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['CNN']

#Unrouted functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):

        if 'USERNAME' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


@app.route("/login", methods=('GET', 'POST'))
def login():
    '''verifies entered credentials with that in the database'''
    error_message = ""

    if request.method == 'POST':
        global username
        print("hie")
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), salt)
        user = db.Credentials.find_one({'username': username})

        if user != None :
            dbUsername = user['username']
            dbPassword = bytes(user['password'])

            if username != dbUsername or bcrypt.hashpw(request.form['password'].encode('utf-8'), password) != dbPassword:
                error_message = 'Invalid Credentials. Please try again.'
            else:
                session['USERNAME'] = username
                db.Credentials.update_one({"username":username}, {"$set":{"active":"True"}})
                return redirect(url_for('login'))
        else:
            error_message = 'Invalid Credentials. Please try again.'

    return render_template('login.html', Error_Message=error_message, System_Name="")

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    '''verifies entered credentials with that in the database'''
    error_message = ""

    if request.method == 'POST':
        global username
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), salt)
        db.Credentials.insert_one({'username': username,'password':password})


    return render_template('signup.html', Error_Message=error_message, System_Name="")

if __name__ == "__main__":
	app.run(debug=True)
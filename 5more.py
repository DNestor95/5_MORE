# basic flask app to show pages for login, register, authroized, signup,  and account creation wiht oauth for the login page and signup page
# this is the main app file for the flask app

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_oauthlib.client import OAuth
import google_auth_oauthlib
from google_auth_oauthlib import flow
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_sqlalchemy import SQLAlchemy
import os
# configuration
DEBUG = True




# app setup

app = Flask(__name__)
app.config.from_object(__name__)


#create the database for the app
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'fdaa:1:da8e:0:1::2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()

#the oauth is working and calling the api but I cannot fully test it since fly will not allow us to deploy

# oauth setup
@app.route('/login/google')
def login_google():
    # Create a flow instance using the client ID and secret
    # obtained from the Google Cloud Console
    flow = flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {'client_id': os.getenv('GOOGLE_CLIENT_ID'), 'client_secret': os.getenv('GOOGLE_CLIENT_SECRET')},
        scopes=['openid', 'email', 'profile'])

    # Generate a URL for the user to authorize the application
    authorization_url, state = flow.authorization_url(
        access_type='offline', prompt='consent')

    # Store the state in the session so the callback can verify the response
    session['oauth_state'] = state

    return redirect(authorization_url)

@app.route('/login/google/callback')
def login_google_callback():
    # Verify the state to prevent cross-site request forgery attacks
    state = session.pop('oauth_state', None)
    if state is None or state != request.args.get('state'):
        return 'Invalid state parameter', 400

    # Exchange the authorization code for an access token and ID token
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {'client_id': os.getenv('GOOGLE_CLIENT_ID'), 'client_secret': os.getenv('GOOGLE_CLIENT_SECRET')},
        scopes=['openid', 'email', 'profile'])
    flow.fetch_token(authorization_response=request.url)

    # Verify the ID token and get the user's information
    id_info = id_token.verify_oauth2_token(
        flow.credentials.id_token, requests.Request(), CLIENT_ID)

    # Get the user's email and name
    email = id_info['email']
    name = id_info.get('name', '')

    # Do something with the user's information (e.g. create a new user account)
    # ...

    return redirect(url_for('index'))
# routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
   #get the login info from the form and check it against the database
    if request.method == "POST":    
        username = request.form["username"]
        password = request.form["password"]
        #check if the username and password are in the database
        user = User.query.filter_by(username=username, password=password).first()
        if user is None:
            flash("Username or password is incorrect")
            return redirect(url_for("login"))
        else:
            session["user_id"] = user.id
            return redirect(url_for("account"))
    else:
        return render_template("login.html")
    


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/authorized")
def authorized():
    return render_template("authorized.html")


@app.route("/account")
def account():
    return render_template("account.html")


@app.route("/logout")
def logout():
    return render_template("logout.html")









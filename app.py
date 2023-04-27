from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_oauthlib.client import OAuth
import google_auth_oauthlib
from google_auth_oauthlib import flow
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_sqlalchemy import SQLAlchemy
import os


# app setup

app = Flask(__name__)
app.config.from_object(__name__)


# database setup

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# database models

#the database should have a user table and each user should have a workout object inside it 
class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(255), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    workouts = db.relationship('Workout', backref='user', lazy=True)


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    
def __init__(self, username, password):
    self.username = username
    self.email = email
    self.password = password

def __repr__(self):
    return "<User %r>" % self.username


# the oauth is working and calling the api but I cannot fully test it since fly will not allow us to deploy


# oauth setup
@app.route("/login/google")
def login_google():
    # Create a flow instance using the client ID and secret
    # obtained from the Google Cloud Console
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        },
        scopes=["openid", "email", "profile"],
    )

    # Generate a URL for the user to authorize the application
    authorization_url, state = flow.authorization_url(
        access_type="offline", prompt="consent"
    )

    # Store the state in the session so the callback can verify the response
    session["oauth_state"] = state

    return redirect(authorization_url)


@app.route("/login/google/callback")
def login_google_callback():
    # Verify the state to prevent cross-site request forgery attacks
    state = session.pop("oauth_state", None)
    if state is None or state != request.args.get("state"):
        return "Invalid state parameter", 400

    # Exchange the authorization code for an access token and ID token
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        },
        scopes=["openid", "email", "profile"],
    )
    flow.fetch_token(authorization_response=request.url)

    # Verify the ID token and get the user's information
    id_info = id_token.verify_oauth2_token(
        flow.credentials.id_token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID")
    )

    # Get the user's email and name
    email = id_info["email"]
    name = id_info.get("name", "")

    # Do something with the user's information (e.g. create a new user account)
    # ...

    return redirect(url_for("index"))


# routes
@app.route("/")
def index():
    return render_template("index.html")


# route for login that displays the login page and authenticates the users
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get form info
        username = request.form["username"]
        password = request.form["password"]

        # check if user exists
        user = User.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                session["username"] = username
                flash("Login successful!", "info")
                return redirect(url_for("account"))
            else:
                flash("Incorrect password!", "warning")
                return redirect(url_for("login"))
        else:
            flash("User does not exist!", "warning")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        # put the info into the database
        user = User(username, password, email)
        db.session.add(user)
        db.session.commit()

        return "Thank you for signing up, " + username + "!"
    else:
        return render_template("signup.html")


@app.route("/authorized")
def authorized():
    return render_template("authorized.html")


@app.route("/workout", methods=["GET", "POST"])
def account():
    workout =  session.username.get("workout")
    reps = session.username.get("reps")
    sets = session.username.get("sets")
    weight = session.username.get("weight")
    #if one button called passed is pressed then the weight is increaed by 5 pounds, if the fail button is pressed then the weight is decreased by 5 pounds then update the page    
    if request.method == "POST":
        if request.form["passed"]:
            weight += 5
        elif request.form["fail"]:
            sets += 1
            reps = reps * 1.2
            weight -= 5
        else:
            return render_template("workout.html", workout=workout, reps=reps, sets=sets, weight=weight)
    #pass the new values to the database for the current session user
    user = User.query.filter_by(username=session["username"]).first()
    user.workout = workout
    user.reps = reps
    user.sets = sets
    user.weight = weight
    db.session.commit()
    
    
    return render_template("workout.html", workout=workout, reps=reps, sets=sets, weight=weight)


@app.route("/logout")
def logout():
    return render_template("logout.html")


# if __name__ == "__main__":
# app.run()

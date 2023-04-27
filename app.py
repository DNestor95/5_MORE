from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_oauthlib.client import OAuth
import google_auth_oauthlib
from google_auth_oauthlib import flow
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
import os
import bcrypt

# app setup

app = Flask(__name__)
app.config.from_object(__name__)


# database setup

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"



db = SQLAlchemy(app)

# database models


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(50), nullable=False)
    workouts = relationship("Workout", backref="user", lazy=True)

class Workout(db.Model):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    workout_name = Column(String(50), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))



with app.app_context():
    db.create_all()


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

    # Store the user's information in the session
    session["email"] = email
    session["name"] = name

    # create a user in the database
    user = User(email, name)
    db.session.add(user)
    db.session.commit()

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
        #check the password if it matches the users password 
        
        
        # check if user exists in database
        user = User.query.filter_by(username=username).first()
        #get hashed password from database
        hashed_password = User.query.filter_by(hashed_password=hashed_password).first()
        

        if user:

                
            if bcrypt.checkpw(password, hashed_password):
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
        #encrypt the password with bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        
        # put the info into the database
        user = User(username, hashed_password, email)
        db.session.add(user)
        db.session.commit()

        return "Thank you for signing up, " + username + "!"
    else:
        return render_template("signup.html")


@app.route("/authorized")
def authorized():
    return render_template("authorized.html")


@app.route("/workout", methods=["GET", "POST"])
def workout():
    # get hte current user and display their workouts
    workouts = Workout.query.filter_by(user_id=session["username"]).all()



    
    if request.method == "POST":
        workout_name = request.form["workout_name"]
        sets = request.form["sets"]
        reps = request.form["reps"]
        weight = request.form["weight"]
        workout = Workout(workout_name, sets, reps, weight, session["username"])
        db.session.add(workout)
        db.session.commit()

    
    if request.method == "POST":
        if request.form["submit_button"] == "Failed Workout":
            workout_name = request.form["workout_name"]
            sets = request.form["sets"]
            reps = request.form["reps"]
            weight = request.form["weight"]
            workout = Workout(workout_name, sets, reps, weight, session["username"])
            db.session.add(workout)
            db.session.commit()
            weight = weight - 5
            reps = reps + 2
            sets = sets + 1
            workout = Workout(workout_name, sets, reps, weight, session["username"])
            db.session.add(workout)
            db.session.commit()
            return redirect(url_for("workout"))
        

        return redirect(url_for("workout"))
    
    
    return render_template("workout.html", workouts=workouts)


@app.route("/logout")
def logout():
    # log current user out
    session.pop("username", None)
    flash("You have been logged out!", "info")


if __name__ == "__main__":
    app.run(debug=True)
    
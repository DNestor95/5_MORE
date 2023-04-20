# basic flask app to show pages for login, register, authroized, signup,  and account creation wiht oauth for the login page and signup page
# this is the main app file for the flask app

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_oauthlib.client import OAuth

# configuration
DEBUG = True


# app setup

app = Flask(__name__)
app.config.from_object(__name__)


# oauth setup
oauth = OAuth()
facebook = oauth.remote_app(
    "facebook",
    base_url="https://graph.facebook.com/",
    request_token_url=None,
    access_token_url="/oauth/access_token",
    authorize_url="https://www.facebook.com/dialog/oauth",
    consumer_key="APP_ID",
    consumer_secret="APP_SECRET",
    request_token_params={"scope": "email"},
)


# routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
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





@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get("oauth_token")


if __name__ == "__main__":
    app.run()

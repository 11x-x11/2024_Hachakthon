"""
app.py contains all of the server application
this is where you'll find all of the GET/POST request handlers
the socket event handlers are inside of socket_routes.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_socketio import SocketIO, emit
import secrets
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# Don't remove this!!
import socket_routes  # Import socket event handlers

# Index page
@app.route("/")
def index():
    return render_template("index.jinja")

# Login page
@app.route("/login")
def login():
    return render_template("login.jinja")

# Handles a POST request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    # Placeholder for handling login logic
    pass

# Signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# Handles a POST request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    # Placeholder for handling signup logic
    pass

# Home page
@app.route("/home")
def home():
    # Placeholder for home page logic
    pass

# Handler for 404 errors
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404


@app.route('/profile/<username>')
def profile(username):
    user = users.get(username)
    if user is None:
        return "User not found", 404
    return render_template('profile.html', user=user)


if __name__ == '__main__':
    socketio.run(app)

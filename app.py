from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from flask_socketio import SocketIO, emit
import secrets
from db import db, User, init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)
init_db(app)

import socket_routes

@app.route("/")
def index():
    print("DEBUG: Accessing index page")
    return redirect(url_for('login'))

@app.route("/login")
def login():
    print("DEBUG: Accessing login page")
    return render_template("login.jinja")

@app.route("/login/user", methods=["POST"])
def login_user():
    print("DEBUG: Processing login request")
    username = request.form.get('username')
    password = request.form.get('password')
    print(f"DEBUG: Login attempt - Username: {username}")
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = username
        print("DEBUG: Login successful")
        flash('Login successful!', 'success')
        return redirect(url_for('home'))
    else:
        print("DEBUG: Login failed")
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))

@app.route("/signup")
def signup():
    print("DEBUG: Accessing signup page")
    return render_template("signup.jinja")

@app.route("/signup/user", methods=["POST"])
def signup_user():
    print("DEBUG: Processing signup request")
    username = request.form.get('username')
    password = request.form.get('password')
    print(f"DEBUG: Signup attempt - Username: {username}")
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print("DEBUG: Signup failed - Username already exists")
        flash('Username already exists', 'error')
        return redirect(url_for('signup'))
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        print("DEBUG: Signup successful")
        flash('Signup successful!', 'success')
        return redirect(url_for('home'))

@app.route("/home")
def home():
    if 'username' not in session:
        print("DEBUG: Unauthorized access to home page - redirecting to login")
        return redirect(url_for('login'))
    return render_template("home.jinja", username=session['username'])

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(_):
    print("DEBUG: 404 error occurred")
    return render_template('404.jinja'), 404

if __name__ == '__main__':
    ssl_contexts = ('certificate/mydomain.crt', 'certificate/mydomain.key')
    socketio.run(app, ssl_context=ssl_contexts)
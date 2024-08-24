from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from flask_socketio import SocketIO, emit
import secrets
import db

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

import socket_routes

@app.after_request
def apply_csp(response):
    response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login")
def login():
    return render_template("login.jinja")

@app.route("/login/user", methods=["POST"])
def login_user():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = db.get_user(username)
    if user is None:
        flash("Error: User does not exist!")
        return redirect(url_for('login'))

    if db.verify_password(user.password, password) is False:
        flash("Error: Password does not match!")
        return redirect(url_for('login'))
    
    session['username'] = username

    return redirect(url_for('home'))
    

@app.route("/signup")
def signup():
    return render_template("signup.jinja")

@app.route("/signup/user", methods=["POST"])
def signup_user():   
    username = request.form.get('username')
    password = request.form.get('password')

    if type(username) != str:
        flash("Error: Fail to create an account!")
    
    if db.get_user(username) is None:
        db.insert_user(username, password)
        session['username'] = username
        flash('Signup successful!', 'success')
        return redirect(url_for('home'))
    else:
        flash("Error: User already exists!")
        return redirect(url_for('signup'))

@app.route("/home")
def home():
    user = db.get_user(session['username'])
    
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("home.jinja", username=session['username'], user=user)

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = db.get_user(session['username'])
    return render_template("profile.jinja", user=user)

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    username = session['username']
    email = request.form.get('email')
    dob = request.form.get('dob')
    location = request.form.get('location')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    bio = request.form.get("bio")
    profile_image = request.files.get('profile_image')

    print(profile_image == None)
    
    db.update_user_profile(
        username=username,
        email=email,
        dob=dob,
        location=location,
        latitude=float(latitude) if latitude else None,
        longitude=float(longitude) if longitude else None,
        bio=bio,
        profile_image=profile_image,
    )
    
    print("haha")
    
    return redirect(url_for('profile'))


if __name__ == '__main__':
    ssl_contexts = ('certificate/mydomain.crt', 'certificate/mydomain.key')
    socketio.run(app, ssl_context=ssl_contexts)
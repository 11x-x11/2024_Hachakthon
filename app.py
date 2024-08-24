from flask import Flask, jsonify, render_template, request, redirect, url_for, session, abort, flash
from flask_socketio import SocketIO, emit
import secrets
import db
import requests
import geonamescache
import pycountry

app = Flask(__name__)

GEONAMES_USERNAME = 'your_geonames_username'

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
        flash("Error: User does not exist!", "error")
        return redirect(url_for('login'))

    if db.verify_password(user.password, password) is False:
        flash("Error: Password does not match!", "error")
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
        flash("Error: Fail to create an account!", "error")
    
    if db.get_user(username) is None:
        db.insert_user(username, password)
        session['username'] = username
        flash('Signup successful!', 'success')
        return redirect(url_for('home'))
    else:
        flash("Error: User already exists!", "error")
        return redirect(url_for('signup'))

@app.route("/home")
def home():
    user = db.get_user(session['username'])
    
    if 'username' not in session:
        return redirect(url_for('login'))
    
    categories = db.get_all_categories()
    return render_template("home.jinja", username=session['username'], user=user, categories=categories)

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

@app.route('/get_skills_by_category')
def get_skills_by_category():
    category_id = request.args.get('category_id', type=int)
    
    if not category_id:
        return jsonify({'error': 'Category ID is required'}), 400
    
    try:
        skills = db.get_skills_by_category(category_id)
        if not skills:
            return jsonify({'skills': []})  # Return an empty list if no skills are found

        return jsonify({'skills': [{'id': skill.id, 'name': skill.name} for skill in skills]})
    except Exception as e:
        app.logger.error(f"Error retrieving skills for category {category_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching skills'}), 500


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = db.get_user(session['username'])
    countries = [(country.alpha_2, country.name) for country in pycountry.countries]
    categories = db.get_all_categories()
    return render_template("profile.jinja", user=user, categories=categories, countries=countries)

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    username = session['username']
    email = request.form.get('email')
    dob = request.form.get('dob')
    country = request.form.get('country')
    city = request.form.get('city')
    bio = request.form.get("bio")
    profile_image = request.files.get('profile_image')
    
    selected_skill_ids = request.form.getlist('skills[]')
    
    db.update_user_profile(
        username=username,
        email=email,
        dob=dob,
        country=country,
        city=city,
        bio=bio,
        profile_image=profile_image,
        selected_skill_ids=selected_skill_ids
    )
    
    return redirect(url_for('profile'))

@app.route('/get_cities')
def get_cities():
    country_code = request.args.get('country')
    gc = geonamescache.GeonamesCache()
    all_cities = gc.get_cities()

    # Filter cities by country code
    filtered_cities = [
        city['name'] for city in all_cities.values()
        if city['countrycode'] == country_code
    ]

    return jsonify({'cities': filtered_cities})

@app.route('/get_skills')
def get_skills():
    category_id = request.args.get('category_id')
    print(category_id)
    if category_id:
        print("123")
        return db.get_skills_by_category(int(category_id))
    else:
        return jsonify({'error': 'Category ID not provided'}), 400

@app.route('/find_matching_user_and_redirect')
def find_matching_user_and_redirect():
    skill_id = request.args.get('skill_id', type=int)

    if not skill_id:
        return jsonify({'error': 'Skill ID is required'}), 400

    try:
        # Get the current user
        user = db.get_user(session['username'])

        # Find a matching user who wants to learn this skill
        matching_user = db.find_matching_user(skill_id, user)

        if matching_user:
            # Create or find a chatroom for these users
            chatroom_url = db.create_chatroom_for_users(user, matching_user)

            return jsonify({'chatroom_url': chatroom_url})
        else:
            return jsonify({'error': 'No matching users found'}), 404
    except Exception as e:
        app.logger.error(f"Error finding matching user for skill {skill_id}: {e}")
        return jsonify({'error': 'An error occurred while finding a matching user'}), 500

@app.route('/chatroom/<int:chatroom_id>')
def chatroom(chatroom_id):
    chatroom = db.get_chatroom(chatroom_id)
    if not chatroom:
        abort(404)
    
    return render_template('chatroom.jinja', chatroom=chatroom)


if __name__ == '__main__':
    ssl_contexts = ('certificate/mydomain.crt', 'certificate/mydomain.key')
    socketio.run(app, ssl_context=ssl_contexts)
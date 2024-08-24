from flask import Flask, jsonify, render_template, request, redirect, url_for, session, abort, flash
from flask_socketio import SocketIO, emit
import secrets
import db
import requests
import geonamescache
import pycountry
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

socketio = SocketIO(app, cors_allowed_origins="*")

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
    username = session.get('username')
    user = db.get_user(username)
    if 'username' not in session:
        return redirect(url_for('login'))

    categories = db.get_all_categories()
    article_list = db.get_all_articles_with_details(username)

    return render_template("home.jinja", username=session['username'], user=user, categories=categories, articles=article_list)

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
    
    skill_ids = request.form.getlist('skills[]')
    interested_skill_ids = request.form.getlist('interested_skills[]')
    
    
    db.update_user_profile(
        username=username,
        email=email,
        dob=dob,
        country=country,
        city=city,
        bio=bio,
        profile_image=profile_image,
        selected_skill_ids=skill_ids,
        interested_skill_ids=interested_skill_ids
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

@socketio.on('find_matching_user')
def handle_find_matching_user(data):
    skill_id = data.get('skill_id')
    username = session.get('username')
    user = db.get_user(username)

    try:
        # Find a matching user
        matching_user = db.find_matching_user(skill_id, user)

        if matching_user:
            # Create or find a chatroom for these users
            chatroom = db.create_chatroom_for_users(user, matching_user)

            emit('matching_user_result', {'chatroom_url': url_for('chatroom', chatroom_id=chatroom.id)})
        else:
            emit('matching_user_result', {'error': 'No matching users found'})
    except Exception as e:
        print(f"Error finding matching user for skill {skill_id}: {e}")
        emit('matching_user_result', {'error': 'An error occurred while finding a matching user'})


@app.route('/chatroom/<int:chatroom_id>')
def chatroom(chatroom_id):
    chatroom = db.get_chatroom(chatroom_id)
    if not chatroom:
        abort(404)
    
    user = db.get_user(session['username'])
    is_initiator = db.get_user_role_in_chatroom(user, chatroom)
    
    socketio.emit('initiate_status', {'is_initiator': is_initiator}, room=chatroom_id)

    return redirect(url_for('home'))


@app.route('/create_article', methods=['POST'])
def create_article():
    title = request.form['title']
    content = request.form['content']
    username = request.form['username']
    
    if db.create_article(title, content, username):
        flash('Article created successfully!', 'success')
    else:
        flash('Failed to create article!', 'error')

    return redirect(url_for('home'))

@app.route('/modify_article/<string:article_id>', methods=['POST'])
def modify_article(article_id):
    title = request.form['title']
    content = request.form['content']
    
    if db.modify_article(int(article_id), title, content):
        flash('Article modified successfully!', 'success')
    else:
        flash('Failed to modify article!', 'error')
    return redirect(url_for('home'))

# Route to delete an article
@app.route('/delete_article/<string:article_id>', methods=['POST'])
def delete_article(article_id):
    if db.elete_article(int(article_id)):
        flash('Article deleted successfully!', 'success')
    else:
        flash('Failed to delete article!', 'error')
    
    return redirect(url_for('home'))

# Route to add a comment to an article
@app.route('/add_comment/<string:article_id>', methods=['POST'])
def add_comment(article_id):
    content = request.form['content']
    username = session.get('username')
    
    if db.add_comment(article_id, content, username):
        flash('Comment added successfully!', 'success')
    else:
        flash('Failed to add comment!', 'error')
        
    return redirect(url_for('home'))

# Route to delete a comment
@app.route('/delete_comment/<string:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if db.delete_comment(comment_id):
        flash('Comment deleted successfully!', 'success')
    else:
        flash('Failed to delete comment!', 'error')
        
    return redirect(url_for('home'))

@socketio.on('my_event')
def handle_my_event(json):
    print('Received event: ' + str(json))
    emit('response', {'data': 'Server received your message!'})

@socketio.on('start_video_chat')
def handle_start_video_chat(data):
    username = data['username']
    print(f"{username} wants to start a video chat")
    # Notify the other user(s) to start the video chat
    emit('video_chat_start', data, broadcast=True)

@socketio.on('video_offer')
def handle_video_offer(data):
    # Forward the offer to the other peer
    emit('video_offer', data, broadcast=True)

@socketio.on('video_answer')
def handle_video_answer(data):
    # Forward the answer to the other peer
    emit('video_answer', data, broadcast=True)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    # Forward the ICE candidate to the other peer
    emit('ice_candidate', data, broadcast=True)


if __name__ == '__main__':
    ssl_contexts = ('certificate/mydomain.crt', 'certificate/mydomain.key')
    socketio.run(app, ssl_context=ssl_contexts)
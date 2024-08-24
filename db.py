import random
from flask import jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from models import *
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.sql import func
import base64

Path("database") \
    .mkdir(exist_ok=True)

engine = create_engine("sqlite:///database/main.db", echo=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()

# initializes the database
Base.metadata.create_all(engine)


def insert_user(username: str, password):
    with Session(engine) as session:
        
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

def get_user(username: str):
    with Session(engine) as session:
        return session.query(User).options(
        joinedload(User.skills),
        joinedload(User.interested_skills)
    ).filter_by(username=username).first()


def verify_password(stored_password, provided_password):
    return provided_password == stored_password

def update_user_profile(
    username: str,
    email: str = None,
    dob: str = None,
    country: str = None,
    city: str = None,
    bio: str = None,
    profile_image: bytes = None,
    selected_skill_ids: list = None,
    interested_skill_ids: list = None
):
    with db_session() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            if email:
                user.email = email
            if dob:
                user.dob = datetime.strptime(dob, "%Y-%m-%d")
            if country:
                user.country = country
            if city:
                user.city = city
            if bio:
                user.bio = bio
            if profile_image:
                user.profile_image = base64.b64encode(profile_image.read())

            if selected_skill_ids is not None:
                # Clear existing skills
                user.skills = []
                # Add selected skills
                for skill_id in selected_skill_ids:
                    skill = session.query(Skill).get(skill_id)
                    if skill:
                        user.skills.append(skill)
            
            if interested_skill_ids is not None:
                # Clear existing interested skills
                user.interested_skills = []
                # Add interested skills
                for skill_id in interested_skill_ids:
                    skill = session.query(Skill).get(skill_id)
                    if skill:
                        user.interested_skills.append(skill)
                
            session.commit()
            return True
        return False


def is_profile_complete(user: User):
    return user.email is not None and user.dob is not None

def populate_initial_skills():
    with Session(engine) as session:
        if session.query(Skill).count() == 0:
            print("haha123")
            categories_skills = {
                    "Technology": ["Programming", "Web Development", "Mobile App Development", "Data Analysis", "Cloud Computing"],
                    "Creative Arts": ["Drawing & Painting", "Graphic Design", "Photography", "Video Editing", "Writing"],
                    "Personal Development": ["Time Management", "Public Speaking", "Mindfulness", "Productivity Tools"],
                    "Business & Marketing": ["Entrepreneurship", "Digital Marketing", "Sales", "Finance"],
                    "Languages": ["English", "Spanish", "French", "Mandarin", "Other Languages"],
                    "Lifestyle & Hobbies": ["Cooking", "Gardening", "DIY & Crafts", "Fitness & Exercise"],
                    "Social & Communication Skills": ["Networking", "Conflict Resolution", "Interpersonal Communication"],
                }
            
            for category_name, skills in categories_skills.items():
                category = SkillCategory(name=category_name)
                session.add(category)
                session.flush()  # Ensure the category ID is available
                
                for skill_name in skills:
                    skill = Skill(name=skill_name, category_id=category.id)
                    session.add(skill)
            
            session.commit()
            
def get_skills_by_category(category_id: int):
    try:
        with Session(engine) as session:
            skills = session.query(Skill).filter_by(category_id=category_id).all()

            # Check if skills is None or an unexpected type
            if not isinstance(skills, list):
                raise ValueError(f"Expected list, got {type(skills)}")

            return skills
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching skills'}), 500
            
def get_all_categories():
    with Session(engine) as session:
        categories = session.query(SkillCategory).options(joinedload(SkillCategory.skills)).all()
        return categories
    
def find_users_by_skill_and_want(skill_id, current_user):
    with Session(engine) as session:
        # Find users who want to learn the skill with skill_id
        interested_users = session.query(User).join(user_skills).filter(user_skills.c.skill_id == skill_id).all()

        # Filter users who have the skills that the current user wants
        matching_users = []
        for user in interested_users:
            if user.username != current_user.username:
                for skill in current_user.skills:
                    if skill in user.skills:
                        matching_users.append((user, skill))
                        break

        return matching_users


def create_chatroom_for_users(user1, user2):
    with Session(engine) as session:
        # Check if a chatroom already exists for these users
        chatroom = session.query(Chatroom).filter(
            Chatroom.users.contains(user1) &
            Chatroom.users.contains(user2)
        ).first()

        if not chatroom:
            # Create a new chatroom
            chatroom = Chatroom(users=[user1, user2])
            session.add(chatroom)
            session.commit()

        # Return the URL to the chatroom
        return url_for('chatroom', chatroom_id=chatroom.id)

def create_article(title: str, content: str, username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            new_article = Article(title=title, content=content, author=user.username)
            session.add(new_article)
            session.commit()
            return True
        return False

def modify_article(article_id: int, title: str, content: str):
    with Session(engine) as session:
        article = session.query(Article).filter_by(id=article_id).first()
        if article:
            article.title = title
            article.content = content
            session.commit()
            return True
        return False

def delete_article(article_id: int):
    with Session(engine) as session:
        article = session.query(Article).filter_by(id=article_id).first()
        if article:
            session.delete(article)
            session.commit()
            return True
        return False

def add_comment(article_id: str, content: str, username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        article = session.query(Article).filter_by(id=article_id).first()
        if user and article:
            new_comment = Comment(content=content, article_id=article_id, author=user.username)
            session.add(new_comment)
            session.commit()
            return True
        return False

def delete_comment(comment_id: str):
    with Session(engine) as session:
        comment = session.query(Comment).filter_by(id=comment_id).first()
        if comment:
            session.delete(comment)
            session.commit()
            return True
        return False

def get_comments_by_article_id(article_id):
    session = db_session()
    try:
        comments = session.query(Comment).filter(Comment.article_id == article_id).all()
        return [{
            'id': comment.id,
            'content': comment.content,
            'article_id': comment.article_id,
            'author': comment.author
        } for comment in comments]
    except Exception as e:
        session.rollback()
        print(f"Error getting comments for article {article_id}: {e}")
        return []
    finally:
        session.close()
        
def get_all_articles_with_details(current_username):
    session = db_session()
    try:
        articles = session.query(Article).options(
            joinedload(Article.comments)
        ).all()

        article_list = []
        for article in articles:
            u = session.query(User).filter_by(username=article.author).first()
            ar = article.to_dict()
            comment_list = []
            
            for comment in get_comments_by_article_id(article.id):
                c = comment
                comment_list.append(c)
            ar.update({'comments': comment_list})
            article_list.append(ar)
        return article_list
    except Exception as e:
        session.rollback()
        print(f"Error getting all articles with details: {e}")
        return []
    finally:
        session.close()
        
def get_all_articles():
    with Session(engine) as session:
        articles = session.query(Article).options(joinedload(Article.comments)).all()
        return [article.to_dict() for article in articles]
        
def find_matching_user(interested_skill_id, current_user):
    with Session(engine) as session:
        # Step 1: Load the interested skill by ID to ensure we're working with the same instance
        interested_skill = session.query(Skill).get(interested_skill_id)
        
        # Step 2: Find users who possess the interested skill
        potential_matches = session.query(User).join(user_skills).filter(
            user_skills.c.skill_id == interested_skill.id,
            User.username != current_user.username
        ).all()
        
        if potential_matches != None:
            return potential_matches[0]
        
        return None

        # # Step 3: Check if any of the potential matches are interested in a skill the current user has
        # for user in potential_matches:
        #     for skill in current_user.skills:
        #         # Ensure the skill is loaded within the current session



def create_chatroom_for_users(user1, user2):
    with Session(engine) as session:
        # Check if a chatroom already exists for these users
        chatroom = session.query(Chatroom).filter(
            Chatroom.users.contains(user1) &
            Chatroom.users.contains(user2)
        ).first()

        if not chatroom:
            # Create a new chatroom
            chatroom = Chatroom(users=[user1, user2])
            session.add(chatroom)
            session.commit()

        # Return the chatroom instance
        return chatroom

def get_chatroom(chatroom_id):
    with Session(engine) as session:
        return session.query(Chatroom).filter_by(id=chatroom_id).first()

def get_user_role_in_chatroom(user, chatroom):
    with Session(engine) as session:
        cu = session.query(ChatroomUser).filter_by(user_id=user.username, chatroom_id=chatroom.id).first()
        return cu.is_initiator if cu else False


def add_friend(user_username, friend_username):
    session = db_session()
    try:
        user = session.query(User).filter_by(username=user_username).first()
        friend = session.query(User).filter_by(username=friend_username).first()

        if user and friend:
            if friend not in user.friends:
                user.friends.append(friend)
                friend.friends.append(user)  
                session.commit()
                return 0
            return 1  # They are already friends
        return -1  # One of the users does not exist
    except Exception as e:
        session.rollback()
        print(f"Error adding friend: {e}")
        return False
    finally:
        session.close()


def get_friend_list(username):
    with db_session() as session:
        friends = session.query(User).join(friend_association, User.username == friend_association.c.friend_id)\
                                     .filter(friend_association.c.user_id == username).all()
        return friends


def create_friend_request(sender_username, receiver_username):
    session = db_session()
    try:
        sender_obj = get_user_by_username(sender_username)
        receiver_obj = get_user_by_username(receiver_username)
        
        if not sender_obj or not receiver_obj:
            return [-1]
        
        existing_request = session.query(FriendRequest).filter_by(
            sender_username=sender_username,
            receiver_username=receiver_username,
            accepted=None
        ).first()

        if existing_request:
            return [1]
        
        if receiver_obj.status == 'offline':
            return [0, None, False]

        new_request = FriendRequest(
            sender_username=sender_username,
            receiver_username=receiver_username
        )
        session.add(new_request)
        session.commit()
        return [0, new_request.request_id, True]
    except Exception as e:
        session.rollback()
        print(f"Error creating friend request: {e}")
        return [-2]  # Error during the

def accept_friend_request_with_details(request_id):
    session = db_session()  # Using scoped session
    try:
        # Use joinedload to fetch related user entities in the same query
        request = session.query(FriendRequest).options(
            joinedload(FriendRequest.sender),
            joinedload(FriendRequest.receiver)
        ).get(request_id)

        if request and request.accepted is None:
            # Mark the friend request as accepted
            request.resolve(True)
            
            # Retrieve usernames from the friend request
            sender_username = request.sender.username
            receiver_username = request.receiver.username

            # Use the existing add_friend function to add each other as friends
            result = add_friend(sender_username, receiver_username)

            if result == 0:
                session.commit()
                return {
                    "success": True,
                    "sender_name": sender_username,
                    "receiver_name": receiver_username,
                    "sender_status": get_user_status(sender_username),
                    "receiver_status": get_user_status(receiver_username),
                    "sender_role": get_user_role(sender_username),
                    "receiver_role": get_user_role(receiver_username)
                }
            else:
                # Handle cases where add_friend does not succeed as expected
                session.rollback()
                return {"success": False, "message": "Failed to add friend"}

        return {"success": False, "message": "Request not pending or does not exist"}
    except Exception as e:
        session.rollback()
        print(f"Error accepting friend request: {e}")
        return {"success": False, "message": "Error during processing"}
    finally:
        session.close()


def decline_friend_request(request_id):
    session = db_session()
    try:
        request = session.query(FriendRequest).get(request_id)
        if request and request.accepted is None:
            request.resolve(False)
            session.commit()
            return True
        return False
    finally:
        session.close()
        
def get_friend_requests(receiver_username):
    session = db_session()
    try:
        friend_requests = session.query(FriendRequest).filter(
            FriendRequest.receiver_username == receiver_username,
            FriendRequest.accepted == None
        ).all()
        return friend_requests
    except Exception as e:
        print(f"Error retrieving friend requests: {e}")
        return []
    finally:
        session.close()

def get_user_by_username(username):
    with db_session() as session:
        return session.query(User).filter_by(username=username).first()


populate_initial_skills()

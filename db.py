from flask import jsonify
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
        return session.query(User).filter_by(username=username).first()
    
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
    selected_skill_ids: list = None
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

def find_matching_user(skill_id, current_user):
    with Session(engine) as session:
        # Find users who want to learn the skill with skill_id
        interested_users = session.query(User).join(user_skills).filter(
            user_skills.c.skill_id == skill_id,
            User.username != current_user.username
        ).all()

        # Filter users who have the skills that the current user wants
        matching_users = []
        for user in interested_users:
            for skill in current_user.skills:
                if skill in user.skills:
                    matching_users.append(user)
                    break

        if matching_users:
            # Randomly select a user from the list of matching users
            return random.choice(matching_users)

        return None

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


populate_initial_skills()

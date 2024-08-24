from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from models import *
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.sql import func
<<<<<<< HEAD

=======
import base64
>>>>>>> 1c1ca7f5a52dcbf5ec7192d8134d7dd628c2cf2f

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

# Update user profile
def update_user_profile(username: str, email: str, dob: str, location: str, latitude: float, longitude: float, bio: str, profile_image: bytes = None):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        print(user)
        if user:
            user.email = email
            user.dob = datetime.strptime(dob, "%Y-%m-%d")
            user.location = location
            user.latitude = latitude
            user.longitude = longitude
            user.bio = bio
            
            if profile_image:
                 user.profile_image = base64.b64encode(profile_image.read())
                 
            session.commit()

def is_profile_complete(user: User):
    return user.email is not None and user.dob is not None
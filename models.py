from sqlalchemy import Boolean, DateTime, LargeBinary, Text, String, Column, Integer, ForeignKey, Table, create_engine, func, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, scoped_session, sessionmaker
from typing import Dict
from datetime import datetime, timezone
import uuid

# data models
class Base(DeclarativeBase):
    def to_dict(self):
        self_dict = dict()
        dropped_keys = ['_sa_instance_state', 'password']
        for key in self.__dict__:
            if key not in dropped_keys:
                self_dict.update({key: self.__dict__[key]})
        return self_dict
    pass

friend_association = Table('friend_association', Base.metadata,
    Column('user_id', String, ForeignKey('user.username'), primary_key=True),
    Column('friend_id', String, ForeignKey('user.username'), primary_key=True)
)

# Updated association table for user skills without the `is_offering` column
user_skills = Table('user_skills', Base.metadata,
    Column('user_id', String, ForeignKey('user.username'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skill.id'), primary_key=True),
)

chatroom_users = Table('chatroom_users', Base.metadata,
    Column('chatroom_id', Integer, ForeignKey('chatroom.id'), primary_key=True),
    Column('user_id', String, ForeignKey('user.username'), primary_key=True)
)

# New association table for user interested skills
user_interested_skills = Table('user_interested_skills', Base.metadata,
    Column('user_id', String, ForeignKey('user.username'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skill.id'), primary_key=True),
)


class User(Base):
    __tablename__ = "user"
    
    username = Column(String, unique=True, nullable=False, primary_key=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)  # Make nullable initially
    dob = Column(DateTime, nullable=True)  # Make nullable initially
    country = Column(String, nullable=True)  # Country field for user location
    city = Column(String, nullable=True)  # City field for user location
    profile_image = Column(LargeBinary, nullable=True)
    bio = Column(Text, nullable=True)

    # Relationships
    friends = relationship(
        'User', 
        secondary=friend_association,
        primaryjoin=username == friend_association.c.user_id,
        secondaryjoin=username == friend_association.c.friend_id,
        backref="friend_of"
    )
    
    skills = relationship(
        'Skill', 
        secondary=user_skills, 
        back_populates='users'
    )
    
    interested_skills = relationship(
        'Skill', 
        secondary=user_interested_skills, 
        back_populates='interested_users'
    )
    
    # Add this relationship to fix the issue
    chatrooms = relationship(
        'Chatroom', 
        secondary=chatroom_users, 
        back_populates='users'
    )


class SkillCategory(Base):
    __tablename__ = "skill_category"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    
    skills = relationship('Skill', back_populates='category')

class Skill(Base):
    __tablename__ = "skill"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False) 
    
    category_id = Column(Integer, ForeignKey('skill_category.id'), nullable=False)
    category = relationship('SkillCategory', back_populates='skills')
    
    users = relationship(
        'User', 
        secondary=user_skills, 
        back_populates='skills'
    )
    
    interested_users = relationship(
        'User', 
        secondary=user_interested_skills, 
        back_populates='interested_skills'
    )


class Chatroom(Base):
    __tablename__ = 'chatroom'

    id = Column(Integer, primary_key=True, autoincrement=True)
    users = relationship('User', secondary='chatroom_users', back_populates='chatrooms')


class Article(Base):
    __tablename__ = 'article'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  # Generate a unique UUID
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, ForeignKey('user.username'), nullable=False)
    comments = relationship(
        'Comment',
        back_populates='article'
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'comments': [comment.to_dict() for comment in self.comments]
        }

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=True)
    article_id = Column(String, ForeignKey('article.id'), nullable=False)
    author = Column(String, ForeignKey('user.username'), nullable=False)
    article = relationship('Article', back_populates='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author,
            'article_id': self.article_id
        }
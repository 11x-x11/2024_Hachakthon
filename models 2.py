from sqlalchemy import Boolean, DateTime, LargeBinary, Text, String, Column, Integer, ForeignKey, Table, create_engine, func, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, scoped_session, sessionmaker
from typing import Dict
from datetime import datetime, timezone

# data models
class Base(DeclarativeBase):
    pass

friend_association = Table('friend_association', Base.metadata,
    Column('user_id', String, ForeignKey('user.username'), primary_key=True),
    Column('friend_id', String, ForeignKey('user.username'), primary_key=True)
)

# Association table for user skills
user_skills = Table('user_skills', Base.metadata,
    Column('user_id', String, ForeignKey('user.username'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skill.id'), primary_key=True),
    Column('is_offering', Boolean, nullable=False)  # True if offering, False if seeking
)

class User(Base):
    __tablename__ = "user"
    
    username = Column(String, unique=True, nullable=False, primary_key=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)  # Make nullable initially
    dob = Column(DateTime, nullable=True)  # Make nullable initially
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    profile_image = Column(LargeBinary, nullable=True)

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

# Skill model
class Skill(Base):
    __tablename__ = "skill"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)  # Skill name (e.g., "Python", "Dancing")
    
    users = relationship(
        'User', 
        secondary=user_skills, 
        back_populates='skills'
    )
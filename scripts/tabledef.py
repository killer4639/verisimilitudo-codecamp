# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Local
SQLALCHEMY_DATABASE_URI = 'postgresql://veefofqdibhpal:8914bc4ed2b67d7c94d979ae0a8557d37dd2d38d4612764711b7d160155257fa@ec2-3-91-127-228.compute-1.amazonaws.com:5432/ddeoponurqhr9a'

# Heroku
# SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(SQLALCHEMY_DATABASE_URI)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    password = Column(String(512))
    email = Column(String(50))

    def __repr__(self):
        return '<User %r>' % self.username


engine = db_connect()  # Connect to database
Base.metadata.create_all(engine)  # Create models

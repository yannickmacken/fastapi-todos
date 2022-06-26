import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# An Engine, which the Session will use for connection resources, specifying location and type of database
SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')
if SQLALCHEMY_DATABASE_URL.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# One central factory method to create a session. When SessionLocal() is called,
# this method creates a session, so it is not necessary to pass engine every time
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base database model through a factory method.
# Classes that inherit from the returned class object will be automatically mapped using declarative mapping.
Base = declarative_base()

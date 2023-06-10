from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

Base = declarative_base()
engine = create_engine('sqlite:///workshop.db')

session_factory = sessionmaker(bind=engine)
session_DB = session_factory()


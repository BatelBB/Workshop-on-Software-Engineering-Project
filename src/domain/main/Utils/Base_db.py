from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///workshop.db')

Session_DB = sessionmaker(bind=engine)
session_DB = Session_DB()


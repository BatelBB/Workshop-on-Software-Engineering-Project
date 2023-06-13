from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

Base = declarative_base()
engine = create_engine('sqlite:///workshop.db', echo=False, pool_size=1000, max_overflow=500)

session_factory = sessionmaker(bind=engine)
session_DB = scoped_session(sessionmaker(autoflush=True, autocommit=False,bind=engine))

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

Base = declarative_base()
engine = create_engine('sqlite:///workshop.db', echo=False, pool_size=1000, max_overflow=500)

session_factory = sessionmaker(bind=engine, expire_on_commit=False)
session_DB = scoped_session(session_factory)


def init_db_from_configuration(db_address):
    global engine, session_factory, session_DB
    engine = create_engine(db_address)
    session_factory = sessionmaker(bind=engine)
    session_DB = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=engine))

import threading

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

Base = declarative_base()

'''
    Provide an API to access the underlying DB
    A singleton, since concurrent access should be synchronized
'''


class DAL:
    lock = threading.RLock()
    pool_size = 200
    max_overflow = 50
    url = 'sqlite:///workshop.db'
    engine = create_engine(url, pool_size=pool_size, max_overflow=max_overflow)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=engine))

    @staticmethod
    def init(url):
        with DAL.lock:
            DAL.session.close()
            DAL.engine = create_engine(url)
            DAL.session_factory = sessionmaker(bind=DAL.engine)
            DAL.session = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=DAL.engine))

    @staticmethod
    def load_or_create_tables(tables):
        Base.metadata.reflect(DAL.engine)
        tables_to_create = []

        for cls in tables:
            if not DAL.is_table_exsits(cls.__tablename__):
                tables_to_create.append(cls.__table__)
        Base.metadata.create_all(DAL.engine, checkfirst=True, tables=tables_to_create)

    @staticmethod
    def is_table_exsits(table_name):
        inspector = inspect(DAL.engine)
        return inspector.has_table(table_name)

    @staticmethod
    def close():
        with DAL.lock:
            DAL.session.close()
            
    @staticmethod
    def add(object):
        with DAL.lock:
            DAL.session.merge(object)
            DAL.session.commit()

    @staticmethod
    def update(object):
        with DAL.lock:
            DAL.session.merge(object)
            DAL.session.commit()

    @staticmethod
    def delete(table, predicate):
        with DAL.lock:
            q = list(filter(predicate, DAL.session.query(table).all()))
            for r in q:
                DAL.session.delete(r)
            DAL.session.commit()

    @staticmethod
    def clear(table):
        with DAL.lock:
            DAL.session.query(table).delete()
            DAL.session.commit()

    @staticmethod
    def size(table):
        with DAL.lock:
            DAL.session.flush()
            return DAL.session.query(table).count()

    @staticmethod
    def is_exists(table, predicate):
        with DAL.lock:
            q = list(filter(predicate, DAL.session.query(table).all()))
            return len(q) > 0

    @staticmethod
    def load(table, predicate, creator):
        with DAL.lock:
            q = list(filter(predicate, DAL.session.query(table).all()))
            return None if len(q) == 0 else creator(q[0])

    @staticmethod
    def load_all(table, creator):
        with DAL.lock:
            rs = DAL.session.query(table).all()
            return list(map(lambda r: creator(r), rs))

    @staticmethod
    def load_all_by(table, predicate, creator):
        with DAL.lock:
            rs = DAL.session.query(table).all()
            return list(map(lambda r: creator(r), filter(predicate, rs)))

    '''
        Return queries instead of business layer objects
    '''
    @staticmethod
    def retrieve_all(table, predicate):
        with DAL.lock:
            rs = DAL.session.query(table).all()
            return list(filter(predicate, rs))

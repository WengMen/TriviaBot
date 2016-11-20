from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Init DB
engine = create_engine('sqlite:///trivia.db', echo=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)

# Utility functions
@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_user(session, nick):
    """Returns a User object matching the nickname from the database (case-insensitive)."""
    return session.query(User).filter(User.name.ilike(nick)).first()


def create_user(session, nick):
    """Creates a new User with score 0 and return it."""
    user = User(name=nick, score=0)
    session.add(user)
    return user


def update_score(session, nick, add_score):
    """Adds add_score to the score of the User matching nick (case-insensitive)."""
    user = session.query(User).filter(User.name.ilike(nick)).first()
    user.score += add_score

from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    score = Column(Integer)

    def __repr__(self):
        return '<User(name=\'%s\', score=\'%s\')>' % (self.name, self.score)

# Init DB
# TODO Move db file path to config, currently shared across all channels
engine = create_engine('sqlite:///trivia.db', echo=True)
Base.metadata.create_all(engine)  # TODO Once DB is out of memory, this needs to go into a seperate init_db.py file
Session = sessionmaker(bind=engine)


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

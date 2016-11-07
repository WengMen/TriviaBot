from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utilities import separate_name

Base = declarative_base()


def on_load(bot):
    bot.add_command('top', top)
    bot.add_command('myscore', myscore)
    bot.add_command('score', score)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    score = Column(Integer)

    def __repr__(self):
        return '<User(name=\'%s\', score=\'%s\')>' % (self.name, self.score)

# Init DB
engine = create_engine('sqlite:///:memory:', echo=True)  # Save in memory for testing purposes
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
    return session.query(User).filter_by(name=nick).first()


def create_user(session, nick):
    session.add(User(name=nick, score=0))


def update_score(session, nick, add_score):
    user = session.query(User).filter_by(name=nick).first()
    user.score += add_score


# Commands
def top(bot, user, channel, args):
    pass


def score(bot, user, channel, args):
    pass


def myscore(bot, user, channel, args):
    nick, identifier, hostname = separate_name(user)

    with session_scope() as session:
        user = get_user(session, nick)

        if not user:
            bot.send_msg(channel, 'Your score is 0. Everyone point and laugh at %s.' % nick)
        else:
            _score = str(user.score)
            bot.send_msg(channel, 'Your score is %s' % _score)

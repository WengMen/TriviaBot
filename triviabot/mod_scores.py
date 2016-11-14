from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from functools import partial

from utilities import separate_name

Base = declarative_base()


def on_load(bot):
    bot.add_command('top', top)
    bot.add_command('myscore', partial(score, self_score=True))
    bot.add_command('score', score)


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
    """Creates a new User and sets his score to 0."""
    session.add(User(name=nick, score=0))


def update_score(session, nick, add_score):
    """Adds add_score to the score of the User matching nick (case-insensitive)."""
    user = session.query(User).filter(User.name.ilike(nick)).first()
    user.score += add_score


# Commands
def top(bot, user, channel, args):
    """Displays a list of the top n=args[0] users in the channel."""
    with session_scope() as session:
        if args:
            n = args[0]
        else:
            n = 10

        users = session.query(User).order_by(User.score.desc()).all()

        msg = ''
        for i, user in enumerate(users):
            msg += '#{rank} {nick} ({score}) ||'.format(rank=i+1, nick=user.name, score=user.score)

            if i > n:
                break

        bot.send_msg(channel, msg[:-2])


def score(bot, user, channel, args, self_score=False):
    """Displays the score of User args[0], or user if no args given or self_score=True in the channel."""
    if not args or self_score:
        nick = separate_name(user)[0]
    else:
        nick = args[0]

    with session_scope() as session:
        user = get_user(session, nick)

        if not user:
            bot.send_msg(channel, '{nick} has not played trivia yet.'.format(nick=user.name))
        else:
            bot.send_msg(channel, '{nick}\'s score is {score}'.format(nick=user.name, score=user.score))

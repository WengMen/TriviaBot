from functools import partial

from utilities import separate_name
import db


def on_load(bot):
    bot.add_command('top', top)
    bot.add_command('myscore', partial(score, self_score=True))
    bot.add_command('score', score)


def top(bot, user, channel, args):
    """Displays a list of the top n=args[0] users in the channel."""
    with db.session_scope() as session:
        if args:
            n = args[0]
        else:
            n = 10

        users = session.query(db.User).order_by(db.User.score.desc()).all()

        msg = ''
        for i, user in enumerate(users):
            msg += '#{rank} {nick} ({score}) || '.format(rank=i+1, nick=user.name, score=user.score)

            if i > n:
                break

        bot.send_msg(channel, msg[:-3])


def score(bot, user, channel, args, self_score=False):
    """Displays the score of User args[0], or user if no args given or self_score=True in the channel."""
    if not args or self_score:
        nick = separate_name(user)[0]
    else:
        nick = args[0]

    with db.session_scope() as session:
        user = db.get_user(session, nick)

        if not user:
            bot.send_msg(channel, '{nick} has not played trivia yet.'.format(nick=user.name))
        else:
            bot.send_msg(channel, '{nick}\'s score is {score}'.format(nick=user.name, score=user.score))

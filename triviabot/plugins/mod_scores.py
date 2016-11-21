from functools import partial

from utilities import separate_name
from models import User


def on_load(bot):
    bot.add_command('top', top)
    bot.add_command('myscore', partial(score, self_score=True))
    bot.add_command('score', score)


def top(bot, user, channel, args):
    """Displays a list of the top n=args[0] users in the channel."""
    try:
        max_users = int(args[0])
    except (ValueError, IndexError) as e:
        max_users = 10

    msg = []
    for rank, user in enumerate(User.top_users(max_users), 1):
        msg.append('#{rank} {nick} ({score})'.format(
            rank=rank,
            nick=user.name,
            score=user.score))
    bot.send_msg(channel, ' || '.join(msg))

def score(bot, user, channel, args, self_score=False):
    """Displays the score of User args[0], or user if no args given or self_score=True in the channel."""
    if not args or self_score:
        nick = separate_name(user)[0]
    else:
        nick = args[0]

    user = User.find(nick)
    if not user:
        bot.send_msg(channel, '{nick} has not played trivia yet.'.format(nick=user.name))
    else:
        bot.send_msg(channel, "{nick}'s score is {score}".format(nick=user.name, score=user.score))

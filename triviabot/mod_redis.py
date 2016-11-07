import redis
from config import config
from mod_help import add_helptext
from utilities import separate_name

r = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=config['redis']['db'])


def on_load(bot):
    bot.add_command('top', top)
    add_helptext('top', 'Shows top scorers (Up to 10).')

    bot.add_command('myscore', my_score)
    add_helptext('myscore', 'Shows your score.')


def update_score(nick):
    current_score = r.get(nick)
    if not current_score:
        r.set(nick, 15)
    else:
        r.set(nick, int(current_score)+15)

    return r.get(nick)


def top(bot, user, channel, args):
    # WORK IN PROGRESS
    scores = r.scan(0, None, 10)
    print scores


def my_score(bot, user, channel, args):
    nick = get_nick(user)
    score = r.get(nick)
    if not score:
        bot.send_msg(channel, 'Your score is 0. Everyone point and laugh at %s.' % nick)
    else:
        bot.send_msg(channel, 'Your score is %s' % score)


def get_nick(user):
    return separate_name(user)[0]

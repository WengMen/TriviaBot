import redis
from config import config

r = redis.StrictRedis(host=config['redis']['host'], port=config['redis']['port'], db=config['redis']['db'])

def update_score(user):
    current_score = r.get(user)
    if current_score is None:
        r.set(user, 15)
    else:
        r.set(user, int(current_score)+15)

    return r.get(user)

def top(bot, channel):
    scores = r.scan(0,None,10)
    print scores

def my_score(bot, user, channel):
    score = r.get(user)
    if score is None:
        bot.send_msg(channel, 'Your score is 0. Everyone point and laugh at %s.' % user)
    else:
        bot.send_msg(channel, 'Your score is %s' % score)

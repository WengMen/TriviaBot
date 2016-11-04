import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def update_score(user):
    currentScore = r.get(user)
    if(currentScore is None):
        r.set(user, 15)
    else:
        r.set(user, int(currentScore)+15)

    return r.get(user)

def top(bot, channel):
    scores = r.scan(0,None,10);
    print scores

def my_score(bot, user, channel):
    score = r.get(user);
    if(score is None):
        bot.send_msg(channel, "Your score is 0. Everyone point and laugh at %s." % user)
    else:
        bot.send_msg(channel, "Your score is %s" % score)

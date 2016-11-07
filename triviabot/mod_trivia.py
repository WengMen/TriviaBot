import random
import time

from twisted.internet import reactor

import riotwatcher
from riotwatcher import RateLimit, EUROPE_WEST

from content.questions import question_generators
from config import config
from utilities import separate_name
from mod_help import add_helptext
from mod_redis import top, my_score


watcher = ''


def on_load(bot):
    bot.add_command('trivia', trivia)
    add_helptext('trivia', 'Stars a new round of trivia.')

    global watcher
    watcher = riotwatcher.RiotWatcher(config['api_key'], default_region=EUROPE_WEST,
                                      limits=(RateLimit(10, 10), RateLimit(500, 600), ))


def trivia(bot, user, channel, args):
    nick, identifier, hostname= separate_name(user)
    if ( not args ):
        ask_question(bot, nick, channel)
    elif( args[0] == "top" ):
        top(bot, channel)
    elif( args[0] == "myscore" ):
        my_score(bot, nick, channel)
    else:
        print("Shit's fucked yo")


def ask_question(bot, nick, channel):
    """Starts a new round of trivia."""
    # Notify the channel that someone started a new round
    bot.send_msg(channel, '%s has started a new trivia round! Get ready!' % nick)

    # Prepare the question
    question = random.choice(question_generators)(watcher)
    duration = 20.0  # in seconds

    event = bot.Event(question.answer, channel, question.solve_question)
    bot.add_event(event)

    # Wait 5s before showing the question
    reactor.callLater(5.0, bot.send_msg, channel, question.question)

    # Solve the question if nobody has answered correctly
    reactor.callLater(duration, question.expire, bot, channel, event)

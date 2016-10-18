import random
import time

from twisted.internet import reactor

import riotwatcher
from riotwatcher import RateLimit, EUROPE_WEST

from content.questions import question_generators
from config import config
from mod_help import add_helptext


watcher = ''


def on_load(bot):
    bot.add_command('trivia', trivia)
    add_helptext('trivia', 'Stars a new round of trivia.')

    global watcher
    watcher = riotwatcher.RiotWatcher(config['api_key'], default_region=EUROPE_WEST,
                                      limits=(RateLimit(10, 10), RateLimit(500, 600), ))


def trivia(bot, user, channel, args):
    """Starts a new round of trivia."""
    # Notify the channel that someone started a new round
    bot.send_msg(channel, '%s has started a new trivia round! Get ready!' % user)

    # Prepare the question
    question = random.choice(question_generators)(watcher)
    duration = 20.0  # in seconds

    event = bot.Event(question.answer, channel, question.solve_question)
    bot.add_event(event)

    # Wait 5s before showing the question
    reactor.callLater(5.0, bot.send_msg, channel, question.question)

    # Solve the question if nobody has answered correctly
    reactor.callLater(duration, question.expire, bot, channel, event)


import time
import random

import riotwatcher
from riotwatcher import RateLimit

from content.questions import question_generators
from config import config


watcher = ''


def on_load(bot):
    bot.add_command('trivia', trivia)

    global watcher
    watcher = riotwatcher.RiotWatcher(config['api_key'], default_region=riotwatcher.EUROPE_WEST,
                                      limits=(RateLimit(10, 10), RateLimit(500, 600), ))


def trivia(bot, user, channel, args):
    """Starts a new round of trivia."""
    global watcher
    question = random.choice(question_generators)(watcher)

    event = bot.Event(question.answer, channel, question.solve_question)
    bot.add_event(event)

    bot.send_msg(channel, question.question)

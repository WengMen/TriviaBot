from twisted.words.protocols import irc
from twisted.internet import reactor
import time

def on_load(bot):
    bot.add_command('trivia', trivia)


class Question:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer.lower()

        self.created = time.time()

    def solve_question(self, bot, user, channel):
        """Called when someone answered correctly."""
        bot.send_msg(channel, 'Correct answer, %s!' % user)

    def expire(self, bot, channel, event):
        """Called when the duration of question is over"""
        time.sleep(5.0)
        if not event.consumed:
            bot.del_event(event)
            bot.send_msg(channel, 'Time is up! The correct answer is \'%s\'' % self.answer)


def trivia(bot, user, channel, args):
    """Starts a new round of trivia."""
    question = Question('Is this real life?', 'This is just fantasy')
    duration = 60.0 # in seconds

    event = bot.Event(question.answer, channel, question.solve_question)
    bot.add_event(event)

    bot.send_msg(channel, question.question)
    reactor.callLater(duration, question.expire, bot, channel, event)
    reactor.run()

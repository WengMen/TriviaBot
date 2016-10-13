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


def trivia(bot, user, channel, args):
    """Starts a new round of trivia."""
    question = Question('Is this real life?', 'This is just fantasy')

    event = bot.Event(question.answer, channel, question.solve_question)
    bot.add_event(event)

    bot.send_msg(channel, question.question)

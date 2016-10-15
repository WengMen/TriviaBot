import random
import time

import riotwatcher


class Question:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer.lower()

        self.created = time.time()

    def solve_question(self, bot, user, channel):
        """Called when someone answered correctly."""
        bot.send_msg(channel, 'Correct answer, %s!' % user)


# def example_generator(watcher):
#     # type: (None) -> Question
#     question = random.choice([Question('Is this real life?', 'Is this just fantasy?'), Question('What\'s 1+1?', '2')])
#     return question


def champion_from_title(watcher):  # TODO Add caching & Exception handling
    champions = watcher.static_get_champion_list()['data']

    championid = champions[random.choice(champions.keys())]['id']

    champion = watcher.static_get_champion(championid)
    title = str(champion['title'])
    name = str(champion['name'])

    question = Question('Which champion has the title "%s"?' % title, name)

    return question

question_generators = [
    # Pretty name -> function callback
    # example_generator,
    champion_from_title,
]
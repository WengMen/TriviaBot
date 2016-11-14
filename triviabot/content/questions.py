import random
import time
from triviabot.utilities import strip_tags, separate_name

import triviabot.db as db


class Question:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer.lower()

        self.created = time.time()

    def solve_question(self, bot, user, channel, answer):
        """Called when someone answered correctly."""
        nick, identifier, hostname = separate_name(user)

        with db.session_scope() as session:
            user = db.get_user(session, nick)

            if not user:
                user = db.create_user(session, nick)

            user.score += 15  # TODO remove hardcoded score per question solved

            score = user.score

        bot.send_msg(channel, 'Correct answer \'%s\' by %s! Your new score is %s.' % (answer, nick, score))

    def expire(self, bot, channel, event):
        """Called when the duration of question is over."""
        time.sleep(5.0)
        if not event.consumed:
            bot.del_event(event)
            bot.send_msg(channel, 'Time is up! The correct answer is \'%s\'' % self.answer)


# Utility functions
def get_random_champion_id(watcher):
    """Returns a random champion_id."""
    champions = watcher.static_get_champion_list()['data']

    return champions[random.choice(champions.keys())]['id']


def strip_champion_name(text, name):
    """Removes the champion name from texts such as lore."""
    return text.replace(name, '-----')

# Generators
# def example_generator(watcher):
#     # type: (None) -> Question
#     question = random.choice([Question('Is this real life?', 'Is this just fantasy?'), Question('What\'s 1+1?', '2')])
#     return question


# Champion Data
def champion_from_spell_name(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='spells')

    name = str(champion['name'])
    spell = str(random.choice(champion['spells'])['name'])  # Choose a random spell

    question = Question('Which champion has a skill called "%s"?' % spell, name)

    return question


def spell_name_from_champion(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='spells')

    name = str(champion['name'])
    spell = random.choice(champion['spells'])  # Choose a random spell
    spell_name = str(spell['name'])
    spell_key = str(spell['key'][-1:])

    question = Question('What\'s the name of %s\'s %s?' % (name, spell_key.upper()), spell_name)

    return question


def spell_name_from_description(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='spells')

    name = str(champion['name'])
    spell = random.choice(champion['spells'])  # Choose a random spell
    spell_name = str(spell['name'])
    spell_description = strip_champion_name(strip_champion_name(str(spell['sanitizedDescription']), name), spell_name)

    question = Question('What\'s the name of the following spell? "%s"' % spell_description, spell_name)

    return question


def champion_from_title(watcher):  # TODO Add caching & Exception handling
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id)
    title = str(champion['title'])
    name = str(champion['name'])

    question = Question('Which champion has the title "%s"?' % title, name)

    return question


def champion_from_enemytips(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='enemytips,spells')
    name = str(champion['name'])
    tips = str(strip_champion_name(' '.join(champion['enemytips']), name))
    spells = champion['spells']

    for spell in spells:
        tips = strip_champion_name(tips, spell['name'])

    tips = str(tips)

    question = Question('Which champion are you playing against if you should follow these tips? \n%s' % tips, name)

    return question


def champion_from_allytips(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='allytips,spells')
    name = str(champion['name'])
    tips = str(strip_champion_name(' '.join(champion['allytips']), name))

    spells = champion['spells']

    for spell in spells:
        tips = strip_champion_name(tips, spell['name'])

    tips = str(tips)

    question = Question('Which champion do you have in your team if you should follow these tips? \n%s' % tips, name)

    return question


def champion_from_blurb(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='blurb')
    name = str(champion['name'])
    blurb = str(strip_champion_name(strip_tags(champion['blurb']), name))

    question = Question('Which champion\'s lore is this? %s' % blurb, name)

    return question


def champion_from_skins(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='skins')
    name = str(champion['name'])
    skins = champion['skins']

    skin_string = ''

    for skin in skins[1:]:  # [1:] to skip the default skin
        skin_string += str(skin['name']) + ', '

    skin_string = strip_champion_name(skin_string[:-2], name)  # remove trailing comma

    question = Question('Which champion\'s skins are these? %s' % skin_string, name)

    return question


def champion_from_passive(watcher):
    champion_id = get_random_champion_id(watcher)

    champion = watcher.static_get_champion(champion_id, champ_data='passive')
    name = str(champion['name'])
    passive = str(strip_champion_name(champion['passive']['sanitizedDescription'], name))

    question = Question('Which champion\'s passive is this? %s' % passive, name)

    return question


question_generators = [
    # Pretty name -> function callback
    # example_generator,
    spell_name_from_champion,
    spell_name_from_description,
    champion_from_title,
    champion_from_spell_name,
    champion_from_enemytips,
    champion_from_allytips,
    champion_from_blurb,
    champion_from_skins,
    champion_from_passive,
]

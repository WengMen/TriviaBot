from utilities import separate_name

command_dict = {}


def on_load(bot):
    bot.add_command('help', helpme)
    add_helptext('help', 'displays this message.')


def helpme(bot, user, channel, args):
    message = 'The following commands are available: '

    # Generates a list of available commands
    for command in command_dict:
        message += command + ' '

    # Sends a description of each command
    for command in command_dict:
        message += '\n' + command + ': ' + command_dict.get(command)

    # Copyright and stuff
    message += '\nThis product is not endorsed, certified or otherwise approved in any way by Riot Games, Inc. or any of its affiliates.'

    # Send message to user
    nickname = separate_name(user)
    bot.send_msg(nickname[0], message)


def add_helptext(command, helptext):
    """Adds info about the command to be displayed by the help command."""
    command_dict[command] = helptext

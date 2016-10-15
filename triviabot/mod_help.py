from utilities import separate_name

command_dict = {}


def on_load(bot):
    bot.add_command('help', helpme)
    command_help('help', 'displays this message.')


def helpme(bot, user, channel, args):
    message = '\nThe following commands are available: '
    # Generates a list of available commands
    for command in command_dict:
        message += command + ' '
    # Sends a description of each command
    for command in command_dict:
        message += '\n' + command + ': ' + command_dict.get(command)
    # Copyright and stuff
    message += '\n\nThis product is not endorsed, certified or otherwise approved in any way by Riot Games, Inc. or any of its affiliates.'
    # Send message to user
    nickname = separate_name(user)
    bot.send_msg(nickname[0], message)


def command_help(command, helptext):
    """Generate a entry in the command_dict dictionary that gives info about the command and it's usage when 'helpme' is used."""
    command_dict[command] = helptext

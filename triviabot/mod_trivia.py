def on_load(bot):
    bot.add_command('trivia', trivia)

garbage = None


def trivia(bot, user, channel, args):
    global garbage  # will be in database later
    if not args:
        bot.send_msg(channel, "Trivia question here")
    else:
        if args[0] == "setgarbage":
            garbage = args[1]
            bot.send_msg(channel, 'Garbage has been set to %s' % garbage)
        elif args[0] == "garbage":
            bot.send_msg(channel, '%s' % garbage if garbage else "Garbage has not been set.")
        else:
            bot.send_msg(channel, 'Shit\'s broke!')

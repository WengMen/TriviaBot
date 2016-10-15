from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import logging
import logging.config
import utilities

import time


class TriviaBot(irc.IRCClient):
    """A trivia IRC Bot."""

    class Event:
        """Events are channel specific commands without arguments that are deactivated if they are triggered once."""

        def __init__(self, trigger, channel, callback):
            self.trigger = trigger
            self.callback = callback
            self.channel = channel

            self.consumed = False
            self.created = time.time()

        def consume(self, bot, user, channel):
            """Consumes the event and calls the relevant function."""
            if self.consumed:
                return

            self.consumed = True
            self.callback(bot, user, channel)

        def is_consumed(self):
            return self.consumed

    def __init__(self, config):
        self.nickname = config['nickname']
        self.realname = config['realname']

        self.trigger = config['trigger']

        # Q Authentication
        self.q_user = config['q_user']
        self.q_password = config['q_password']

        # Logging
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('triviaBot')

        # List of commands & events
        self.commands = {}
        self.events = []

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger.info('Connected to the server.')

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.warn('Disconnected from the server. %s' % reason)

    def send_msg(self, entity, message):
        self.msg(entity, message, length=410)
        self.logger.info('[OUT] [%s] %s' % (entity, message))

    # manage commands
    def add_command(self, trigger, callback):
        """Adds a command that can be called by users using ?trigger and runs the function callback."""
        try:
            self.commands[trigger.lower()] = callback
            self.logger.info('[CMD] command \'%s\' registered to %s' % (trigger, callback))
        except KeyError:
            self.logger.warn('[CMD] attempted to create command \'%s\': already exists' % trigger)

    def del_command(self, trigger):
        """Deletes a command based on a given trigger."""
        try:
            del self.commands[trigger.lower()]
            self.logger.info('[CMD] command \'%s\' deleted' % trigger)
        except KeyError:
            self.logger.warn('[CMD] attempted to delete command \'%s\': does not exists' % trigger)

    # manage events
    def add_event(self, event):
        """Adds an event listener."""
        for e in self.events:
            if event.trigger == e.trigger and event.channel == e.channel:
                self.logger.warn('[EVT] events must be unique: %s already exists in %s' % (event.trigger, event.channel))
                raise Exception("Events must be unique.")  # TODO non-generic exception

        self.events.append(event)
        self.logger.info('[EVT] event \'%s\' registered to %s in %s' % (event.trigger, event.callback, event.channel))

    def del_event(self, event):
        """Deletes an event."""
        try:
            self.events.remove(event)
            self.logger.info('[EVT] event \'%s\' deleted' % event.trigger)
        except ValueError:
            self.logger.warn('[EVT] event %s in %s does not exists' % (event.trigger, event.channel))

    # event handling
    def signedOn(self):
        """Called when the bot has successfully signed on to the server."""
        # auth with Q and hide host
        self.send_msg('Q@CServe.quakenet.org', 'AUTH %s %s' % (self.q_user, self.q_password))
        self.mode(self.nickname, True, 'x')

        # setup modules
        modules = [utilities.make_module(module) for module in config['startup_modules']]
        self.load_modules(modules)

        # join channels
        for channel in self.factory.channels:
            self.join(channel)

    def load_modules(self, modules):
        for module in modules:
            try:
                module.on_load(self)
            except Exception, e:
                # self.logger.error('[ERROR] Module %s could not be loaded.' % module)
                self.logger.error(e)

    def joined(self, channel):
        """Called when the bot joins a channel."""
        self.logger.info('[JOIN] %s' % channel)

    def left(self, channel):
        """Called when the bot leaves a channel."""
        self.logger.info('[PART] %s' % channel)

    def privmsg(self, user, channel, message):
        """Called when the bot receives a message."""
        self.logger.info('[IN] [%s] <%s> %s' % (channel, user, message))

        # check if message is an event
        for event in self.events:
            if event.trigger == message.lower() and event.channel == channel:
                event.consume(self, user, channel)
                self.del_event(event)
                return

        # check if message is a command
        if not message.startswith(self.trigger):
            return

        # handle it
        # example: '?hello world :)' => command == 'hello', args == ['world', ':)']
        command, args = message.lower().split()[0][1:], message.lower().split()[1:]
        if command in self.commands.keys():
            self.commands[command](self, user, channel, args)

    def userJoined(self, user, channel):
        """Called when a user joins a channel."""
        self.logger.info('[IN] [%s] %s joined the channel' % (channel, user))

    def userLeft(self, user, channel):
        """Called when a user leaves a channel."""
        self.logger.info('[IN] [%s] %s left the channel' % (channel, user))

    def userQuit(self, user, quit_message):
        """Called when a user quits the network."""
        self.logger.info('[IN] %s quit (%s)' % (user, quit_message))

    def userKicked(self, kickee, channel, kicker, message):
        """Called when a user gets kicked from a channel."""
        self.logger.info('[IN] [%s] %s has been kicked by %s (%s)' % (channel, kickee, kicker, message))

    def userRenamed(self, oldname, newname):
        """Called when a user changes their nick."""
        self.logger.info('[IN] %s is now known as %s' % (oldname, newname))


class TriviaBotFactory(protocol.ClientFactory):
    """
    A factory for TriviaBots.

    A new protocol instance will be created whenever we connect to the server.
    """

    def __init__(self, config):
        self.config = config

        self.channels = config['channels']

    def buildProtocol(self, addr):
        p = TriviaBot(self.config)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """On disconnect, reconnect to the server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed:', reason)  # TODO add to log instead
        reactor.stop()


if __name__ == '__main__':
    from config import config
    # create factory protocol and application
    f = TriviaBotFactory(config)

    # connect factory to this host and port
    reactor.connectTCP(config['host'], config['port'], f)

    # run bot
    reactor.run()

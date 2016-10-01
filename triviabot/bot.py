from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import logging
import logging.config
import utilities

import re


class TriviaBot(irc.IRCClient):
    """A trivia IRC Bot."""

    def __init__(self, nickname, realname, q_user, q_password):
        self.nickname = nickname
        self.realname = realname

        self.trigger = config.trigger

        # Q Authentication
        self.q_user = q_user
        self.q_password = q_password

        # Logging
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('triviaBot')

        # List of commands
        self.commands = {}

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

    # event handling
    def signedOn(self):
        """Called when the bot has successfully signed on to the server."""
        # auth with Q and hide host
        self.send_msg('Q@CServe.quakenet.org', 'AUTH %s %s' % (self.q_user, self.q_password))
        self.mode(self.nickname, True, 'x')

        # setup modules
        modules = [utilities.make_module(module) for module in config.startup_modules]
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

        # parse hostmask TODO MAKE THIS SHIT WORK
        # user = re.match(r'^(.*?)!(.*?)@(.*?)$', user)  # TODO Better regex-string
        # nickname, ident, host = user.group(1), user.group(2), user.group(3)

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

    def __init__(self, channels, nickname, realname, q_user, q_password):
        self.channels = channels

        self.q_user, self.q_password = q_user, q_password
        self.nickname = nickname
        self.realname = realname

    def buildProtocol(self, addr):
        p = TriviaBot(self.nickname, self.realname, self.q_user, self.q_password)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """On disconnect, reconnect to the server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed:', reason)  # TODO add to log instead
        reactor.stop()


if __name__ == '__main__':
    import config
    # create factory protocol and application
    f = TriviaBotFactory(config.channels, config.nickname, config.realname, config.q_user, config.q_password)

    # connect factory to this host and port
    reactor.connectTCP(config.host, config.port, f)

    # run bot
    reactor.run()

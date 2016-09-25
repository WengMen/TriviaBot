from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import logging, logging.config


class TriviaBot(irc.IRCClient):
    """A trivia IRC Bot."""

    def __init__(self, nickname, realname, q_user, q_password):
        self.nickname = nickname
        self.realname = realname

        # Q Authentication
        self.q_user = q_user
        self.q_password = q_password

        # Logging
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('triviaBot')

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger.info('Connected to the server.')

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.warn('Disconnected from the server.')

    def send_msg(self, user, message):
        self.msg(user, message, length=410)
        self.logger.info('[OUT] [%s] %s' % (user, message))

    # event handling
    def signedOn(self):
        """Called when the bot has successfully signed on to the server."""
        # auth with Q and hide host
        self.send_msg('Q@CServe.quakenet.org', 'AUTH %s %s' % (self.q_user, self.q_password))
        self.mode(self.nickname, True, 'x')

        # join channels
        for channel in self.factory.channels:
            self.join(channel)

    def joined(self, channel):
        """Called when the bot joins a channel."""
        self.logger.info('[JOIN] %s' % channel)

    def left(self, channel):
        """Called when the bot leaves a channel."""
        self.logger.info('[PART] %s' % channel)

    def privmsg(self, user, channel, message):
        """Called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.info('[IN] [%s] <%s> %s' % (channel, user, message))

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import logging
import logging.config
import utilities

import time
import os

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
            self.callback(bot, user, channel, self.trigger)

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
        self.logger.warn('Disconnected from the server. {reason}'.format(reason=reason))

    def send_msg(self, entity, message):
        self.msg(entity, str(message), length=410)
        self.logger.info('[OUT] [{entity}] {message}'.format(entity=entity, message=message))

    # manage commands
    def add_command(self, trigger, callback):
        """Adds a command that can be called by users using ?trigger and runs the function callback."""
        try:
            self.commands[trigger.lower()] = callback
            self.logger.info('[CMD] command \'{trigger}\' registered to {callback}'
                             .format(trigger=trigger, callback=callback))
        except KeyError:
            self.logger.warn('[CMD] attempted to create command \'{trigger}\': already exists'.format(trigger=trigger))

    def del_command(self, trigger):
        """Deletes a command based on a given trigger."""
        try:
            del self.commands[trigger.lower()]
            self.logger.info('[CMD] command \'{trigger}\' deleted'.format(trigger=trigger))
        except KeyError:
            self.logger.warn('[CMD] attempted to delete command \'{trigger}\': does not exists'.format(trigger=trigger))

    # manage events
    def add_event(self, event):
        """Adds an event listener."""
        for e in self.events:
            if event.trigger == e.trigger and event.channel == e.channel:
                self.logger.warn('[EVT] events must be unique: {event} already exists in {channel}'
                                 .format(event=event.trigger, channel=event.channel))
                raise Exception('Events must be unique.')  # TODO non-generic exception

        self.events.append(event)
        self.logger.info('[EVT] event \'{trigger}\' registered to {callback} in {channel}'
                         .format(trigger=event.trigger, callback=event.callback, channel=event.channel))

    def del_event(self, event):
        """Deletes an event."""
        try:
            self.events.remove(event)
            self.logger.info('[EVT] event \'{trigger}\' deleted'.format(trigger=event.trigger))
        except ValueError:
            self.logger.warn('[EVT] event {trigger} in {channel} does not exists'
                             .format(trigger=event.trigger, channel=event.channel))

    # event handling
    def signedOn(self):
        """Called when the bot has successfully signed on to the server."""
        # auth with Q and hide host
        self.send_msg('Q@CServe.quakenet.org', 'AUTH {q_user} {q_password}'
                      .format(q_user=self.q_user, q_password=self.q_password))
        self.mode(self.nickname, True, 'x')

        # setup modules
        module_path = config['modules_path']
        modules = [utilities.make_module(module, module_path) for module in config['startup_modules']]
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
        self.logger.info('[JOIN] {channel}'.format(channel=channel))

    def left(self, channel):
        """Called when the bot leaves a channel."""
        self.logger.info('[PART] {channel}'.format(channel=channel))

    def privmsg(self, user, channel, message):
        """Called when the bot receives a message."""
        self.logger.info('[IN] [{channel}] <{user}> {message}'.format(channel=channel, user=user, message=message))

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
        command, args = message.lower().split()[0][1:], message.split()[1:]
        if command in self.commands.keys():
            self.commands[command](self, user, channel, args)

    def userJoined(self, user, channel):
        """Called when a user joins a channel."""
        self.logger.info('[IN] [{channel}] {user} joined the channel'.format(channel=channel, user=user))

    def userLeft(self, user, channel):
        """Called when a user leaves a channel."""
        self.logger.info('[IN] [{channel}] {user} left the channel'.format(channel=channel, user=user))

    def userQuit(self, user, quit_message):
        """Called when a user quits the network."""
        self.logger.info('[IN] {user} quit ({reason})'.format(user=user, reason=quit_message))

    def userKicked(self, kickee, channel, kicker, message):
        """Called when a user gets kicked from a channel."""
        self.logger.info('[IN] [{channel}] {kickee} has been kicked by {kicker} ({reason})'
                         .format(channel=channel, kickee=kickee, kicker=kicker, reason=message))

    def userRenamed(self, oldname, newname):
        """Called when a user changes their nick."""
        self.logger.info('[IN] {oldname} is now known as {newname}'.format(oldname=oldname, newname=newname))


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

import logging
import re

import cfg

LOG = logging.getLogger('debug')


class Message(object):
    """ Message class to easily deal with chat messages. """

    def __init__(self, author, content, type=None):
        self.author = author
        self.content = content
        self.type = type

    @staticmethod
    def factory(msg):
        matched = re.match(cfg.CHAT_RE, msg)
        author = matched.group(1)
        content = matched.group(2)
        msg = Message(author, content)
        if msg.is_command():
            matched = re.match(Command.REGEX, msg.content)
            command = matched.group(1)
            args = matched.group(2).split()
            msg = Command(msg.author, msg.content, command, args)
        return msg

    def is_command(self):
        return re.match(Command.REGEX, self.content)


class Command(Message):
    """ Command class (Message subclass). """

    REGEX = re.compile("^!(\w+)(.*)")

    def __init__(self, author, content, command, args):
        super(Command, self).__init__(author, content, "cmd")
        self.command = command
        self.args = args

    def process(self):
        command_result = []
        if self.command == "pyramid":
            command_result = Pyramid.build(self.author, self.args)
        return command_result


class Pyramid:
    """ Static class to build a pyramid. """

    MAX_SIZE = 8

    @staticmethod
    def _size_threshold(size):
        """ Threshold the pyramid size to avoid huge pyramids

        :param size: pyramid size set by the chatter
        :return: pyramid size after thresholding
        """
        return int(size) if int(size) < Pyramid.MAX_SIZE else Pyramid.MAX_SIZE

    @staticmethod
    def build(author, args):
        """ Build a pyramid based on input args

        :param author: chatter who requested for a pyramid
        :param args: input arguments
        :return: list of pyramid parts
        """
        size = cfg.DEFAULT_PYRAMID_SIZE
        symbol = cfg.DEFAULT_PYRAMID_SYMBOL

        if len(args):
            if len(args) == 1:
                if args[0].isdigit():
                    size = Pyramid._size_threshold(args[0])
                else:
                    symbol = args[0]
            else:
                if args[0].isdigit():
                    size = Pyramid._size_threshold(args[0])
                    symbol = args[1]
                elif args[1].isdigit():
                    size = Pyramid._size_threshold(args[1])
                    symbol = args[0]

        LOG.debug("A pyramid is sent (author:%s|size:%s|symbol:%s)", author, size, symbol)
        pyramid = []
        for i in range(2 * size - 1):
            block = [symbol] * (i + 1 if i < size else 2 * size - (i + 1))
            block = " ".join(block)
            pyramid.append(block)

        return pyramid

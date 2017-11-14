import abc
import logging
import re

import cfg

LOG = logging.getLogger('debug')


class Message(object):

    CHAT_RE = ":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.*)"

    def __init__(self, byte):
        matched = re.match(Message.CHAT_RE, byte)
        self.author = matched.group(1)
        self.content = matched.group(2)

    @staticmethod
    def is_message(byte):
        return True if re.match(Message.CHAT_RE, byte) else False


class Pyramid(abc.ABCMeta):
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
    def process(args=None):
        """ Build a pyramid based on input args

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

        LOG.debug("A pyramid is sent (size:%s|symbol:%s)", size, symbol)
        pyramid = []
        for i in range(2 * size - 1):
            block = [symbol] * (i + 1 if i < size else 2 * size - (i + 1))
            block = " ".join(block)
            pyramid.append(block)

        return pyramid


class Command(abc.ABC):

    REGEX = re.compile("^!(\w+)(.*)")

    subclasses = {
        'pyramid': Pyramid
    }

    @staticmethod
    def is_command(message):
        return True if re.match(Command.REGEX, message.content) else False

    @staticmethod
    def _get_command(message):
        matched = re.match(Command.REGEX, message.content)
        command = matched.group(1)
        args = matched.group(2).split()
        return command, args

    @staticmethod
    def process(message):
        command, args = Command._get_command(message)
        if command in Command.subclasses:
            return Command.subclasses[command].process(args)

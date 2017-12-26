import logging

import cfg
from twitch_bot import irc

LOG = logging.getLogger('debug')


class Pyramid(irc.Command):
    """ Static class to build a pyramid. """

    MAX_SIZE = 5

    @staticmethod
    def _size_threshold(size):
        """ Threshold the pyramid size to avoid huge pyramids

        :param size: pyramid size set by the chatter
        :return: pyramid size after thresholding
        """
        return int(size) if int(size) < Pyramid.MAX_SIZE else Pyramid.MAX_SIZE

    def process(self):
        """ Build a pyramid based on input args

        :return: list of pyramid parts
        """
        size = cfg.DEFAULT_PYRAMID_SIZE
        symbol = cfg.DEFAULT_PYRAMID_SYMBOL

        if len(self.args):
            if len(self.args) == 1:
                if self.args[0].isdigit():
                    size = Pyramid._size_threshold(self.args[0])
                else:
                    symbol = self.args[0]
            else:
                if self.args[0].isdigit():
                    size = Pyramid._size_threshold(self.args[0])
                    symbol = self.args[1]
                elif self.args[1].isdigit():
                    size = Pyramid._size_threshold(self.args[1])
                    symbol = self.args[0]

        LOG.debug("{author} has sent a pyramid (size:{size}|symbol:{symbol})".format(author=self.author,
                                                                                     size=size,
                                                                                     symbol=symbol))
        pyramid = []
        for i in range(2 * size - 1):
            block = [symbol] * (i + 1 if i < size else 2 * size - (i + 1))
            block = " ".join(block)
            pyramid.append(block)

        return pyramid

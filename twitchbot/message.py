import logging
import re

LOG = logging.getLogger('debug')


class Message(object):
    """ Message class to easily deal with chat messages. """

    def __init__(self, type, author, content):
        self.type = type
        self.author = author
        self.content = content


class PyramidHandler(object):
    """ Detect a pyramids in the chat. """

    def __init__(self):
        self.pyramid = []
        self.pyramid_size = 0
        self.increasing = True

    def _reset_pyramid(self):
        """ Reset all the pyramid attributes. """

        self.pyramid = []
        self.pyramid_size = 0
        self.increasing = True

    def need_to_break_pyramid(self):
        return len(self.pyramid) >= 2

    def detect_pyramid(self, msg):
        """ Detect if a chatter is making a pyramid.

        :param msg: The current chat message
        :return: return True if a pyramid has been completed, False otherwise
        """

        is_pyramid = False

        # If the message is a single word (a possible pyramid start)
        if re.match(r'\w+', msg.content) and not self.pyramid:
            self.pyramid.append(msg)

        else:
            last_message_pyramid_stage = self.pyramid[-1].content.count(self.pyramid[0].content)
            current_message_pyramid_state = msg.content.count(self.pyramid[0].content)

            # If the pyramid is increasing
            if current_message_pyramid_state - last_message_pyramid_stage == 1:

                # If the pyramid is increasing from the start
                if self.increasing:
                    LOG.debug("A '%s' pyramid is being build (lvl %s)", self.pyramid[0].content, current_message_pyramid_state)
                    self.pyramid.append(msg)

                # If the pyramid is starting increasing after a decrease
                else:
                    LOG.debug("The combo has been broken (%s -> %s)", self.pyramid[-1].content.content, msg.content)
                    self._reset_pyramid()

            # If the pyramid is decreasing
            elif current_message_pyramid_state - last_message_pyramid_stage == -1:

                # If the pyramid is completed
                if current_message_pyramid_state == 1:
                    is_pyramid = True
                    LOG.debug("A %s-leveled '%s' pyramid has been completed by %s",
                              self.pyramid_size, self.pyramid[0].content, msg.author)
                    self._reset_pyramid()

                else:
                    # If the pyramid just starts decreasing
                    if self.increasing:
                        self.increasing = False
                        self.pyramid_size = last_message_pyramid_stage
                        LOG.debug("The %s-leveled '%s' pyramid is now decreasing",
                                  self.pyramid_size, self.pyramid[0].content)

                    # If the pyramid keeps decreasing
                    else:
                        LOG.debug("The %s-leveled '%s' pyramid keeps decreasing",
                                  self.pyramid_size, self.pyramid[0].content)
                    self.pyramid.append(msg)
            else:
                self._reset_pyramid()
                LOG.debug("The combo has been broken (%s -> %s)", self.pyramid[-1].content, msg.content)

        return is_pyramid

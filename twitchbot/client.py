import asyncio
import json
import logging
import socket

import cfg
from twitchbot.message import Message
from twitchbot import utils

LOG = logging.getLogger('debug')


class IRCClient(object):
    """ Client to interact with the chat. """

    def __init__(self):
        self._socket = socket.socket()
        self._op_list = {}

    # BOT COMMANDS #

    def connect(self):
        """ Connect to the channel. """
        self._socket.connect((cfg.HOST, cfg.PORT))
        self._socket.send(bytes("PASS {password}\r\n".format(password=cfg.PASS), "utf-8"))
        self._socket.send(bytes("NICK {nickname}\r\n".format(nickname=cfg.NICK), "utf-8"))
        self._socket.send(bytes("JOIN #{channel}\r\n".format(channel=cfg.CHAN), "utf-8"))
        LOG.debug("Client connected")

    async def chat(self, msg):
        """ Send a message to the server.
        :param msg: the message to send
        """
        self._socket.send(bytes("PRIVMSG #{channel} :{message}\r\n".format(channel=cfg.CHAN, message=msg), "utf-8"))

    async def ban(self, user):
        """ Ban a user from the channel.
        :param user: The user to ban
        """
        await self.chat(".ban {user}".format(user=user))
        LOG.debug("%s has been banned", user)

    async def timeout(self, user, seconds=600):
        """ Ban a user from the channel.
        :param user: The user to ban
        :param seconds: the length of the timeout in seconds (default 600)
        """
        await self.chat(".timeout {}".format(user, seconds))
        LOG.debug("%s has been timed out for %ss", user, seconds)

    # CHAT TOOLS #

    def _is_op(self, username):
        """ Return True if the user is a moderator
        :param username: the username to check
        :return: True if the user is a moderator, False otherwise
        """
        return username in utils.flatten_dict_values(self._op_list)

    def _parse_irc_bytes(self, byte_sequence):
        """ Parse an IRC byte sequence.
        :param byte_sequence: byte sequence to parse
        :return: [(author, message), (author, message), ...]
        """
        byte_list = byte_sequence.split("\r\n")
        return [Message.factory(byte) for byte in byte_list if "PRIVMSG" in byte]

    # LOOPED COROUTINES #

    async def listen(self):
        """ Keep reading in the socket for new messages. """

        while True:
            received = self._socket.recv(1024).decode()
            if received:
                messages = self._parse_irc_bytes(received)
                for msg in messages:
                    if msg.type == "cmd":
                        command_result = msg.process()
                        for line in command_result:
                            await self.chat(line)

    async def fill_op_list(self):
        """ Fill the moderator list periodically (every 5s). """
        while True:
            body, status_code = await utils.request(url=cfg.CHAT_URL, headers={"accept": "*/*"})
            try:
                parsed_body = json.loads(body)
            except json.decoder.JSONDecodeError:
                LOG.warning("[%s] Cannot retrieve stream chatters information (bad json format)", status_code)
            except KeyError:
                LOG.warning("[%s] Cannot retrieve stream chatters information (empty body)", status_code)
            except (ValueError, TypeError):
                LOG.warning("[%s] Cannot retrieve stream chatters information", status_code)
            else:
                self._op_list = utils.reduce_dict(parsed_body['chatters'],
                                                  ["moderators", "global_mods", "admins", "staff"])
                LOG.debug("Reloading op list: %s", self._op_list)
            await asyncio.sleep(10)

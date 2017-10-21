import asyncio
import json
import re
import socket

import cfg
from twitchbot import message
from twitchbot import utils


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

    async def timeout(self, user, seconds=600):
        """ Ban a user from the channel.
        :param user: The user to ban
        :param seconds: the length of the timeout in seconds (default 600)
        """
        await self.chat(".timeout {}".format(user, seconds))

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
        parsed_messages = []
        for byte in byte_list:
            if byte:
                if 'PRIVMSG' in byte:
                    author = re.match(cfg.CHAT_RE, byte).group(1)
                    content = re.match(cfg.CHAT_RE, byte).group(2)
                    parsed_messages.append(message.Message('privmsg', author, content))
        return parsed_messages

    # LOOPED COROUTINES #

    async def listen(self):
        """ Keep reading in the socket for new messages. """
        pyramid_handler = message.PyramidHandler()
        while True:
            received = self._socket.recv(1024).decode()
            if received:
                messages = self._parse_irc_bytes(received)
                for msg in messages:
                    if pyramid_handler.detect_pyramid(msg):
                        await self.chat("@{} {}".format(msg.author, cfg.MESSAGE_PYRAMID_COMPLETED))

    async def fill_op_list(self):
        """ Fill the moderator list periodically (every 5s). """
        while True:
            body, status_code = await utils.request(url=cfg.CHAT_URL, headers={"accept": "*/*"})
            try:
                parsed_body = json.loads(body)
            except json.decoder.JSONDecodeError:
                print("[{code}] Cannot retrieve stream chatters information (bad json format)".format(code=status_code))
            except KeyError:
                print("[{code}] Cannot retrieve stream chatters information (empty body)".format(code=status_code))
            except (ValueError, TypeError):
                print("[{code}] Cannot retrieve stream chatters information".format(code=status_code))
            else:
                self._op_list = utils.reduce_dict(parsed_body['chatters'],
                                                  ["moderators", "global_mods", "admins", "staff"])
                print("op_list", self._op_list)
            await asyncio.sleep(5)

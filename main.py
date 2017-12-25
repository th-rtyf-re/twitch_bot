# main
# Program entry point

import sys

import asyncio

from twitch_bot import client
from twitch_bot import log

sys.path.append('twitch_bot')


def main():

    irc_client = client.IRCClient()
    irc_client.connect()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(irc_client.listen(), loop=loop)
    asyncio.ensure_future(irc_client.fill_mod_list(), loop=loop)
    loop.run_forever()


if __name__ == '__main__':
    main()

# main
# Program entry point

import sys

from twitchbot import async
from twitchbot import client

sys.path.append('twitchbot')

def main():

    irc_client = client.IRCClient()
    irc_client.connect()

    async.LoopManager(
        irc_client.listen,         # Listen to the input messages
        irc_client.fill_op_list    # Fill the viewers list
    ).start()


if __name__:
    main()

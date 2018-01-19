# cfg.py
# Configurations variables

HOST = "irc.twitch.tv"
PORT = 6667
NICK = "tw_ntys_vn"
PASS = "oauth:******************************"
CHAN = "lostdedew"

VALID_COMMANDS = ["baby"]

""" pyramid variables """
DEFAULT_PYRAMID_SYMBOL = "t"
DEFAULT_PYRAMID_SIZE = 3  # size is thresholded at 5

""" baby variables """
BABY_ACTIVE = False
DEFAULT_NGRAM_LENGTH = 3 # probably should be geq 2
BABY_NGRAM_TREE = {}
BABY_NGRAM_COUNT = 0
DEFAULT_SPEAK_LENGTH = 34
BABY_FREQ_THRESHOLD = 2
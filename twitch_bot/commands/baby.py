import random

import logging

import cfg
from twitch_bot import irc

LOG = logging.getLogger('debug')


class Baby(irc.Command):
	""" Imitates what people are saying using Markov things.
		Inherited methods, from irc.Command:
			- author: the author of the message for which the class is called
			- args: a list of the words that came after the command
		
		Baby uses a tree of ngrams to save on space. We use nested
		dictionaries, with characters as nodes and integers as leaves. The
		leaves count the number of occurences of the ngram associated with the
		leaf's branch.
	"""
	ngram_length = cfg.DEFAULT_NGRAM_LENGTH
	speak_length = cfg.DEFAULT_SPEAK_LENGTH
	# extra dialogue options
	dialogue_awake = {"wake": "Baby is already awake.",
					  "sausage": "SAUCISSON"}
	dialogue_asleep = {}
	confused = ["goo goo?", "ba ba?", "ma ma?", "aaa a"]
	
	def get_sub_tree(self, tree, branch):
		""" Given an ngram tree and an ngram prefix, return the sub tree of
			suffixes to the ngram
		"""
		view = tree
		for char in branch:
			view = view[char]
		return view
	
	def increment_ngram(self, tree, ngram):
		""" Increment the count of an ngram.
		"""
		view = tree
		for char in ngram[:-1]:
			if char in view:
				view = view[char]
			else:
				view[char] = {}
				view = view[char]
		if ngram[-1] in view:
			view[ngram[-1]] += 1
		else:
			view[ngram[-1]] = 1
		cfg.BABY_NGRAM_COUNT += 1
		return tree
	
	def get_occurences(self, tree):
		""" A recursive function that basically flattens the tree into a list
			of ngrams with their number of occurences.
		"""
		ngrams = []
		for char in tree:
			if type(tree[char]) is int:
				ngrams.append((char, tree[char]))
			else: #type is dict
				ngrams.extend([(char + mgram, count)
						for mgram, count in self.get_occurences(tree[char])])
		return ngrams
	
	def get_top_ngrams(self, tree):
		""" Return a list of the most probable ngrams.
		"""
		ngrams = self.get_occurences(tree)
		top_ngrams = []
		if len(ngrams) > 0:
			_, top = max(ngrams, key=lambda p: p[1])
			for ngram, count in ngrams:
				if count > 0 and top - count <= cfg.BABY_FREQ_THRESHOLD:
					top_ngrams.append(ngram)
		return top_ngrams
		
	def generate_babble(self, n, ngram_tree):
		""" Make a probable string of characters
		"""
		# Start with a random higher-probability ngram
		top_ngrams = self.get_top_ngrams(ngram_tree)
		if top_ngrams == []:	# Not enough data to babble
			return ["BabyRage " + random.choice(self.confused)]
		babble = random.choice(top_ngrams)
		
		# Add characters to the message. Tries adding one, using the (n-1)
		#	last characters as the starting point. If there are no good
		#	candidates, try using the (n-2) last characters and add two
		#	letters. And so on, until it appears that no continuation is
		#	plausible, or if the max length is reached, in which case the
		#	message ends.
		iteration = 0
		while iteration <= self.speak_length and babble[-2:] != "  ":
			m = 1
			mgram_tree = self.get_sub_tree(ngram_tree, babble[m-n:])
			top_mgrams = self.get_top_ngrams(mgram_tree)
			while top_mgrams == [] and m <= n-2:
				m += 1
				mgram_tree = self.get_sub_tree(ngram_tree, babble[m-n:])
				top_mgrams = self.get_top_ngrams(mgram_tree)
			
			if m < n:
				next_mgram = random.choice(top_mgrams)
				babble = babble + next_mgram
				iteration += m
		return ["BabyRage " + babble]
	
	def learn_message(self, ngram_tree):
		""" Add 1 to every ngram that appears in the read message.
		"""
		message = ' '.join(self.args)
		message_long = message + ' ' * self.ngram_length
		for i in range(len(message)):
			self.increment_ngram(ngram_tree, message_long[i:i+self.ngram_length])
	
	def active_process(self):
		""" Control what the baby is doing.
		"""
		if len(self.args) > 0:
			if self.args[0] == "wake" and not cfg.BABY_ACTIVE:
				cfg.BABY_ACTIVE = True
				if cfg.BABY_NGRAM_COUNT == 0:
					# Generate the ngram dictionary
					if len(self.args) > 1 and self.args[1].isdigit():
						self.ngram_length = int(self.args[1])
				LOG.debug("{author} has activated the baby.".format(author=self.author))																  
				return ["Baby has woken up."]
			
			elif cfg.BABY_ACTIVE:
				if self.args[0] == "speak":
					if len(self.args) > 1 and self.args[1].isdigit():
						self.speak_length = int(self.args[1])
					LOG.debug("{author} has asked the baby to speak.".format(author=self.author))
					return self.generate_babble(self.ngram_length, cfg.BABY_NGRAM_TREE)
				
				elif self.args[0] == "forget":
					forgotten = "everything"
					if len(self.args) > 1:
						message = ' '.join(self.args[1:])
						view = cfg.BABY_NGRAM_TREE
						try:
							for char in message[1:self.ngram_length]:
								view = view[char]
							view[message[self.ngram_length]] = 0
							LOG.debug(str(cfg.BABY_NGRAM_TREE))
							forgotten = "'" + message[1:self.ngram_length+1] + "'"
						except:
							pass
					else:
						cfg.BABY_NGRAM_TREE = {}
						cfg.BABY_NGRAM_COUNT = 0
					LOG.debug("{author} has made the baby forget.".format(author=self.author))
					return ["Baby has forgotten {thing}.".format(thing=forgotten)]
				
				elif self.args[0] == "sleep":
					cfg.BABY_ACTIVE = False
					LOG.debug("{author} has deactivated the baby.".format(author=self.author))
					return ["Baby has fallen asleep."]
				elif self.args[0] in list(self.dialogue_awake):
					LOG.debug("{author} is making conversation.".format(author=self.author))
					return [self.dialogue_awake[self.args[0]]]
				else:
					self.learn_message(cfg.BABY_NGRAM_TREE)
					LOG.debug("{author} has confused the baby.".format(author=self.author))
					return ["BabyRage " + random.choice(self.confused)]
			else:
				if self.args[0] in list(self.dialogue_asleep):
					return [dialogue_asleep[self.args[0]]]
				else:
					return ["ResidentSleeper"]
		return []
		
	def passive_process(self):
		""" Add to baby's memory.
		"""
		if cfg.BABY_ACTIVE:
			self.learn_message(cfg.BABY_NGRAM_TREE)
			LOG.debug("Baby has listened to {author} speak.".format(author=self.author))
		return []
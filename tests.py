import json
import unittest

from parse_cards import standardise_name

class TestCardParsing(unittest.TestCase):
	
	@classmethod
	def setUpClass(cls):
		with open("card_aliases.json", "r") as infile:
			cls._aliases = json.load(infile)
	
	@classmethod
	def tearDownClass(cls):
		del cls._aliases
	
	def get_alias(self, query):
		return self._aliases.get(standardise_name(query), "?")
	
	def test_card_names(self):
		test_names = {
			"bonecrusher giant": "Bonecrusher Giant // Stomp",
			"Stomp": "?",
			"akkilavarunner // toktokvolcanoborn": "Akki Lavarunner // Tok-Tok, Volcano Born",
			"You're Gonna Need a Bigger BOAT": "Abrade",
			"Kitezh, Sunken City": "Academy Ruins",
			"African Swallow": "Birds of Paradise",
			"European Swallow": "Birds of Paradise",
			"Titania, Gaea Incarnate": "?",
			"Bloomvine Regent": "Bloomvine Regent // Claim Territory",
			"Claim Territory": "?",
			"Chucky": "Kardur, Doomscourge",
			"theallspark": "Doubling Cube",
			"Dracula, the Voyager": "Edgar, Charmed Groom // Edgar Markov's Coffin",
			"casketofnativeearth": "Edgar, Charmed Groom // Edgar Markov's Coffin",
			"megatron": "Blightsteel Colossus",
			"Recyclops, Nature's Vengeance": "Garruk Relentless // Garruk, the Veil-Cursed"
		}
		for query, result in test_names.items():
			with self.subTest(query=query, result=result):
				self.assertEqual(self.get_alias(query), result)
		
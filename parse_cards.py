import json, requests, string, re
from unidecode import unidecode

remove_excess_pattern = re.compile(r"[^a-z0-9]", flags=re.I | re.A)


def standardise_name(full_name):
	standard_name = unidecode(full_name).lower()
	standard_name = remove_excess_pattern.sub("", standard_name)
	return standard_name

def compile_cards():
	cards_seen = set()
	aliases = dict()
	dupes = []
	
	meld_blacklist = set()
	meld_whitelist = set()
	#banned_layouts = ["art_series", "token", "planar", "scheme", "vanguard", "double_faced_token", "emblem", "host", "augment"]
	#banned_promo_types = {"playtest"}
	output_stuff = []
	with open("Default_Cards.jsonl", "r") as infile:
		for line in infile:
			card_obj = json.loads(line.strip())
			
			# By default, we only care about cards that are either Legal, Banned, or Restricted in Vintage
			# This excludes everything that is classified as "Not Legal", which includes things like:
			# 	- Silver bordered cards
			# 	- Attractions
			# 	- Sticker sheets
			# 	- Art series cards
			# 	- and so on
			legalities = card_obj.get("legalities", dict())
			if legalities.get("vintage", "not_legal") not in {"banned", "restricted", "legal"}:
				continue
			
			# To handle name input in a decklist, we standardise the name, and make aliases for the name if needed.
			# Standardising the name is done by:
			# 	1) Using unidecode on the name
			# 	2) Making the name all lowercase
			# 	3) Removing everything from the name that isn't an ASCII letter or a digit
			# 	Example: "Akki Lavarunner // Tok-Tok, Volcano Born" becomes "akkilavarunnertoktokvolcanoborn"
			# For cards with multiple names, the full name is always written as <name1> // <name2>
			# We alias both names to the main name, except in the following cases:
			# 	- The combined face of Meld cards aren't processed at all
			# 	- For Adventure or Prepare cards, we don't alias <name2> to the main name (because <name2> can sometimes be an existing magic card.)
			# TODO: Flavour names
			
			full_name = card_obj.get("name", "")
			flavour_name = card_obj.get("flavor_name", None)
			layout = card_obj.get("layout")
			
			if layout == "meld":
				# All three components of a Meld card are seperate objects in the data file.
				# For Meld Result cards (e.g. Urza, Planeswalker), we skip the result entirely.
				# Seeing the first component tells us whether we need to process or skip the following components.
				if full_name in meld_blacklist:
					continue
				if full_name not in meld_whitelist:
					skip = False
					for part in card_obj.get("all_parts"):
						match part:
							case {"component": "meld_result", "name": part_name}:
								meld_blacklist.add(part_name)
								if part_name == full_name:
									skip = True
							case {"component": "meld_part", "name": part_name}:
								meld_whitelist.add(part_name)
					if skip:
						continue
				
			if layout == "reversible_card":
				# oTL
				# TODO: This bullshit
				continue
			
			standard_name = standardise_name(full_name)
			
			def check_and_add_to_aliases(alias_to_add, full_card_name):
				# Quick and dirty: check if an alias points to something else already before adding it
				if aliases.get(alias_to_add, None) not in [None, full_card_name]:
					output_stuff.append(f"!! {alias_to_add} => {aliases.get(alias_to_add)} + {full_card_name}")
				aliases[alias_to_add] = full_card_name
			
			if full_name not in cards_seen:
				# If we haven't seen this card at all yet, then save the standard name as an alias
				cards_seen.add(full_name)
				check_and_add_to_aliases(standard_name, full_name)
			
			if flavour_name:
				standard_flavour_name = standardise_name(flavour_name)
				check_and_add_to_aliases(standard_flavour_name, full_name)
			
			#print(f"{full_name:<60} => {standard_name}")
			if layout in ["split", "flip", "transform", "modal_dfc", "adventure", "prepare"]:
				faces = card_obj.get("card_faces", [])
				for i in range(len(faces)):
					if layout in ["adventure", "prepare"] and i > 0:
						continue
					face_name_standard = standardise_name(faces[i].get("name", ""))
					face_flav_standard = standardise_name(faces[i].get("flavor_name", ""))
					if face_name_standard:
						check_and_add_to_aliases(face_name_standard, full_name)
					if face_flav_standard:
						check_and_add_to_aliases(face_flav_standard, full_name)
	
	print(output_stuff)
	with open("cards_parsed.json", "w") as outfile:
		json.dump(list(cards_seen), outfile)
	with open("card_aliases.json", "w") as outfile:
		json.dump(aliases, outfile)

def unidecode_testing():
	chars = ['é', 'ï', 'ú', 'ñ', 'ü', 'ó', 'û', 'ō', 'ö', 'à', 'í', 'â', 'á', '—', 'î', '꞉', 'ä', '®', 'É']
	for char in chars:
		print(f"{char}\t-\t{unidecode(char)}")

def main():
	"""
	Reads an MTGJSON file, parses the cards inside for the following information:
		- Name (converted to lowercase with punctuation and diacritics removed)
		- True Name (as printed)
		- Legalities (standard, modern, legacy, vintage, highlander, pioneer?, pauper?)
		- Restricted
		- Reserved List
		- Mana Cost
		- Colours
		- Types
	"""
	promo_types = []
	with open("oracle_cards.jsonl", "r") as infile:
		for line in infile:
			card_obj = json.loads(line.strip())
			for promo_type in card_obj.get("promo_types", []):
				if promo_type not in promo_types:
					print(f"Added {promo_type} from {card_obj.get("name")}")
					promo_types.append(promo_type)
		print(promo_types)

if __name__ == "__main__":
	compile_cards()
# Prints list of song titles (order significant) to use as playlist
# for ZiCardio and MaziCardio classes.
# Data source is hardcoded as Downloads/mazi_song - songs.csv
# This is very likely an overcomplicated mess, but it's just for my use.

import argparse
from collections import defaultdict, OrderedDict
import csv
from datetime import date, timedelta
import random


def make_intensity_dict():
	"""Create ordered dict using stringified ints from
	INTESITY_EXPLANATION as keys and empty list as items
	Returns: dict, example: {
		'0': [], ...
	}
	"""

	INTESITY_EXPLANATION = [
		('0', 'warm_up'),
		('1', 'low'),
		('2', 'mid'),
		('3', 'high'),
		('4', 'hyper'),
	]
	
	d = OrderedDict()
	for i, _ in INTESITY_EXPLANATION:
		d[i] = []
	return d

def to_date(date_text):
	"""Convert CSV text date to python date"""

	month, day, year = [int(t) for t in date_text.split('/')]
	return date(year, month, day)

def build_catalog_from_file(file):
	"""Build song catalog
	Arguments: file -- csv file
	Returns: dict, example: {
		'new': {
			'1': ['some song title', 'another title'],
			'2': [], ...
		},
		'recent': {
			'1': ['third title'],
			'2': [], ...
		},
		'old': {
			'1': ['forth title'],
			'2': [], ...
		}
	}
	"""

	catalog = {
		d: make_intensity_dict() 
		for d in ['new', 'recent', 'old']
	}

	with open(file) as f:
		reader = csv.DictReader(f)

		for r in reader:
			# Maybe later we'll use the type if I teach zicardio again
			if args.zi and 'bgirl' in r.get('Type').lower():
				continue
			
			try:  # Skip intensities leading with `~` (means song isn't ready)
				intensity = r['Intense']
				if intensity[0] == '~':
					raise KeyError
			except KeyError:
				continue

			# Decide if song is new, recent, or old
			debut_date = r.get('Debut')
			if debut_date:
				is_new_song = to_date(debut_date) + timedelta(days=13) > date.today()
			is_recent_song = to_date(r['6 month']) > date.today()
			
			# Catalog song by new-old and intensity
			song_title = r['Song']
			if is_new_song:
				catalog['new'][intensity].append(song_title)
			elif is_recent_song:
				catalog['recent'][intensity].append(song_title)
			else:
				catalog['old'][intensity].append(song_title)
	return catalog

def create_intensity_count_map(intensity_order):
	"""Tally each intensity
	Returns -- dict, example: {
		'0': 1,
		'1': 3, ...
	}
	"""

	d = defaultdict(int)
	for i in SONG_ORDER:
		d[i] += 1
	return d

def get_songlist_for_intensity(intensity, count):
	"""Get list of songs of given intensity.
	Arguments: 
	intensity -- str, corresponds to intesity levels from INTESITY_EXPLANATION
	count -- int, length of returned list 
	Returns: list of song titles (str) of given intensity (str) as a list.
	The length of the returned string will be equal to the count argument.
	New songs will be always be at the end of the list.
	"""
	
	def _choose_songs_for_age(age, intensity, count):
		if not count:
			return []
		refined_count = min([count, len(CATALOG[age][intensity])])  # Can't sample more songs than exist
		return random.sample(population=CATALOG[age][intensity], k=refined_count)

	# Use as many new songs as possible
	new_songs = _choose_songs_for_age('new', intensity, count)
	remaining_count = count - len(new_songs)
	
	# Fill out rest of the list with recent and old songs
	older_songs = []
	for age in ['recent', 'old']:
		remaining_count -= len(older_songs)
		
		# Add additional old song as "throwback" for variability 1/3 of time
		if age == 'old':
			remaining_count += random.randint(0, 2) % 2

		older_songs += _choose_songs_for_age(age, intensity, remaining_count)

	# Shuffle just the recent and old songs, we always want new songs.
	random.shuffle(older_songs) 

	# Add new songs to end- we'll pop from list so new songs will always be first
	songs = older_songs + new_songs
	return songs[-count:]

# Start
parser = argparse.ArgumentParser()
parser.add_argument("--zi", action="store_true")
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

# Define flow for playlist
REGULAR_SET = ['1', '2', '3']
HYPER_SET = ['1', '2', '4']
SONG_ORDER = \
	['0'] + \
	REGULAR_SET + \
	REGULAR_SET + \
	HYPER_SET + \
	REGULAR_SET + \
	REGULAR_SET

# Create song catalog
PLAYLIST_LOCATION = '../Downloads/mazi_song - songs.csv'
CATALOG = build_catalog_from_file(PLAYLIST_LOCATION)
BLANK_PLAYLIST = create_intensity_count_map(SONG_ORDER)

# Debugging checks
if args.debug:
	for _type in ['new', 'recent', 'old']:
		for intensity, songs in CATALOG[_type].items():
			for s in songs:
				debug_output = "{0:7}- {1:2}- {2}".format(_type, intensity, s)
				print(debug_output)

# Replace BLANK_PLAYLIST { 'some-intensity': int } item with song_titles
for intensity, count in BLANK_PLAYLIST.items():
	BLANK_PLAYLIST[intensity] = get_songlist_for_intensity(intensity, count)

# Construct playlist of chosen songs according to song order
playlist = [
	BLANK_PLAYLIST[i].pop()
	for i in SONG_ORDER
]

# Output playlist
for song_title in playlist:
	print song_title

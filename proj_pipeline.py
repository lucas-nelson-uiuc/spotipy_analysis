import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy.oauth2 as oauth2
import pandas as pd
import numpy as np
import re
from datetime import datetime

class Error(Exception):
	"""Base class for all exceptions"""
	pass

class URLError(Error):
	"""Invalid URL passed"""
	pass

class InvalidDateError(Error):
	"""Case of invalid date"""
	pass

class DateYearError(Error):
	"""Date does not match assumed structure: missing month and date entries."""
	pass

class DateMonthError(Error):
	"""Date does not match assumed structure: missing date entry."""
	pass

class SpotifyUser():
	def __init__(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret

# GENRE CLASSIFICATION FUNCTION

@st.cache
def pipeline_single_spotify(spotify_user, playlist_url):
	"""Gather spotify playlist data using user token and playlist url(s)"""

	auth_manager = SpotifyClientCredentials(client_id = spotify_user.client_id,
											client_secret = spotify_user.client_secret)
	sp = spotipy.Spotify(auth_manager=auth_manager)
	
	details_labels = ['title', 'artist', 'album', 'genre', 'track_url', 'img_url', 'duration', 'explicit', 'popularity',
					'artist_date', 'user_date', 'user_time']
	features_labels = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
						'liveness', 'valence', 'tempo', 'signature']
	track_details = []
	track_features = []
	playlist_index = 0

	while len(sp.playlist_tracks(playlist_url, offset = playlist_index)['items']) != 0:

		# gather track details
		for item in sp.playlist_tracks(playlist_url, offset = playlist_index)['items']:
			track_title = item['track']['name']
			track_artist = item['track']['artists'][0]['name']
			track_album = item['track']['album']['name']
			track_url = item['track']['external_urls']['spotify']
			track_img = item['track']['album']['images'][0]['url']
			track_length = item['track']['duration_ms']
			track_explicit = item['track']['explicit']
			track_popularity = item['track']['popularity']

			# add details for track genre(s)
			artist_genres = sp.artist(item['track']['album']['artists'][0]['external_urls']['spotify'])['genres']
			if len(artist_genres) == 0:
				track_genre = 'NA'
			else:
				track_genre = pipeline_select_genre(artist_genres)

			# add details for when track was added by SpotifyUser
			added_at = item['added_at']
			match = re.search('([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2})Z', added_at)
			added_date = datetime.strptime(match.group(1), '%Y-%m-%d').date()
			added_time = datetime.strptime(match.group(2), '%H:%M:%S').time()
			
			# add details for when track was added by artist
			track_added = item['track']['album']['release_date']
			try:
				if track_added == '0000':
					raise InvalidDateError
				if len(track_added) == 4:
					raise DateYearError
				if len(track_added) == 7:
					raise DateMonthError
				match = re.search('([0-9]{4}-[0-9]{2}-[0-9]{2})', track_added)
				track_date = datetime.strptime(match.group(1), '%Y-%m-%d').date()
			except InvalidDateError:
				track_date = added_date
			except DateYearError:
				proxy_date = track_added + '-01-01'
				track_date = datetime.strptime(proxy_date, '%Y-%m-%d').date()
			except DateMonthError:
				proxy_date = track_added + '-01'
				track_date = datetime.strptime(proxy_date, '%Y-%m-%d').date()

			track_details.append([track_title, track_artist, track_album, track_genre, track_url, track_img, track_length,
									track_explicit, track_popularity, track_date, added_date, added_time])
		
		# gather track features
		for track in track_details:
			audio_features = sp.audio_features(track[4])[0]
			track_danceability = audio_features['danceability']
			track_energy = audio_features['energy']
			track_loudness = audio_features['loudness']
			track_speechiness = audio_features['speechiness']
			track_acousticness = audio_features['acousticness']
			track_instrumentalness = audio_features['instrumentalness']
			track_liveness = audio_features['liveness']
			track_valence = audio_features['valence']
			track_tempo = audio_features['tempo']
			track_signature = audio_features['time_signature']
			track_features.append([track_danceability, track_energy, track_loudness, track_speechiness,
								track_acousticness, track_instrumentalness, track_liveness, track_valence,
								track_tempo, track_signature])

		playlist_index += 100

	# combine details and features per track
	for track, features in zip(track_details, track_features):
		track.extend(features)

	# combine labels
	details_labels.extend(features_labels)
	playlist_df = pd.DataFrame(track_details, columns=details_labels)
	
	# add playlist name
	playlist_df['playlist'] = sp.playlist(playlist_url)['name']
	
	return playlist_df

@st.cache
def pipeline_multip_spotify(spotify_user, playlist_url_string):
	"""Recall pipeline_single_spotify until end of playlist"""

	auth_manager = SpotifyClientCredentials(client_id = spotify_user.client_id,
											client_secret = spotify_user.client_secret)
	sp = spotipy.Spotify(auth_manager=auth_manager)

	playlist_df_list = []
	
	for playlist_url in playlist_url_string.split(','):

		tracker = 0
		
		try:
			playlist_url = playlist_url.strip()
			playlist_df_list.append(pipeline_single_spotify(spotify_user, playlist_url))

		except:
			playlist_name = sp.playlist(playlist_url)['name']
			url_link = playlist_url_string.split(',')[tracker]
			print(f'Sorry. Could not obtain {playlist_name}. Please ensure {url_link} entered correctly.')

		tracker += 1

	return pd.concat(playlist_df_list).drop_duplicates()

@st.cache
def pipeline_rick_roll(spotify_user):
	"""Get rick roll'd"""

	auth_manager = SpotifyClientCredentials(client_id = spotify_user.client_id,
											client_secret = spotify_user.client_secret)
	sp = spotipy.Spotify(auth_manager=auth_manager)
	
	track = sp.track('https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=c3785c9a0ab04252')
	audio_features = sp.audio_features('https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=c3785c9a0ab04252')[0]

	return pd.DataFrame({
		'index':'INDEX',
		'title':track['name'],
		'artist':track['artists'][0]['name'],
		'album':track['album']['name'],
		'genre':'pop',
		'url':track['external_urls']['spotify'],
		'duration':track['duration_ms'],
		'explicit':track['explicit'],
		'popularity':track['popularity'],
		'artist_date':track['album']['release_date'],
		'danceability':audio_features['danceability'],
		'energy':audio_features['energy'],
		'loudness':audio_features['loudness'],
		'speechiness':audio_features['speechiness'],
		'acousticness':audio_features['acousticness'],
		'instrumentalness':audio_features['instrumentalness'],
		'liveness':audio_features['liveness'],
		'valence':audio_features['valence'],
		'tempo':audio_features['tempo'],
		'signature':audio_features['time_signature']
		}, index=['index']).reset_index(drop=True).drop(columns='index')

def pipeline_select_genre(artist_genres):
	if len(artist_genres) == 0:
		return 'NA'
	else:
		for subgenre in artist_genres:
			if 'indie' in subgenre:
				return 'indie'
			elif 'lo-fi' in subgenre:
				return 'lo-fi'
			elif 'post' in subgenre and 'rock' in subgenre:
				return 'post-rock'
			elif 'rock' in subgenre:
				return 'rock'
			elif 'alternative' in subgenre:
				return 'alternative'
			elif 'pop' in subgenre:
				return 'pop'
			elif 'hip' in subgenre and 'hop' in subgenre:
				return 'hip-hop'
			elif 'rap' in subgenre:
				return 'rap'
			elif 'classical' in subgenre or 'british' in subgenre or 'orchestra' in subgenre or 'symphony' in subgenre:
				return 'classical'
			elif 'jazz' in subgenre:
				return 'jazz'
			else:
				return artist_genres[0]

@st.cache
def pipeline_genres_spotify(spotify_user):
	"""Retrieve 'spotify recognized' genres"""

	auth_manager = SpotifyClientCredentials(client_id = spotify_user.client_id,
											client_secret = spotify_user.client_secret)
	sp = spotipy.Spotify(auth_manager=auth_manager)

	return sp.recommendation_genre_seeds()['genres']

if __name__ == '__main__':
	user = SpotifyUser(client_id='3369a177760443e1ba8fdc24ffe8ee3a',
						client_secret='26557253d83447879b0ff7251d291517')

	playlists_str = """https://open.spotify.com/playlist/3Whz31feyEWBBJ1bgubprI"""

	pipeline_single_spotify(user, playlists_str)
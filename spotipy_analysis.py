import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import spotipy_workshop
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy.oauth2 as oauth2

import scipy
from plotly import figure_factory as ff
from datetime import datetime

class Error(Exception):
    """Base class for all other exceptions"""
    pass

# THEME settings
st.set_page_config(page_title='Spotify Analysis Dashboard',
                    page_icon=Image.open('spotipy_logo.png'),
                    layout='wide')

# BODY page layout
st.title('Spotify Analysis Dashboard')

st.write("""Welcome to `spotipy_analysis`, the application you run when you don't want to wait for Spotify Rewind!
            This application provides an up-to-date, on-command analysis of the user's requested Spotify playlist(s).
            Using Spotify's API functionality, all data is secure and not being collected by utilization of this app.
        """)

# SIDEBAR page layout
st.sidebar.header('Client Information')


client_id = st.sidebar.text_input('Client ID', '3369a177760443e1ba8fdc24ffe8ee3a')
client_secret = st.sidebar.text_input('Client secret', '26557253d83447879b0ff7251d291517')
playlist_input = st.sidebar.text_area('Playlist URL(s)', """https://open.spotify.com/playlist/2peFCkryOU68kcEueeBmcw,
    https://open.spotify.com/playlist/4gRAQPeK0VBqua9EVCk83i,
    https://open.spotify.com/playlist/24fobBkjvpmwUL6M55Ls41,
    https://open.spotify.com/playlist/7fzOIIrfWEifFp64mZr0Fp,
    https://open.spotify.com/playlist/4ruz6qz9UaJi0Uh9aXWd4e,
    https://open.spotify.com/playlist/1EffEt6r2PZiNoqJPBa53S,
    https://open.spotify.com/playlist/3PFpKt44V2PP5IvNqCn1ly,
    https://open.spotify.com/playlist/2dijCoBx6ktdHC7OjERJHD,
    https://open.spotify.com/playlist/4r3lbgLtB6OflmHdNAeFWt,
    https://open.spotify.com/playlist/55mC6DTHx1jWpHUfXpUaUC,
    https://open.spotify.com/playlist/4I9peD1SiBDaBhKsDNa4yg,
    https://open.spotify.com/playlist/3Whz31feyEWBBJ1bgubprI,
    https://open.spotify.com/playlist/0QPTp6QO7mt3icX7NiFax6,
    https://open.spotify.com/playlist/57Q4NLC64QOuJcqzzvAioi,
    https://open.spotify.com/playlist/2CcSamqgDw8BzN0RJp7qGA,
    https://open.spotify.com/playlist/45ZeJcyQ9oEIf4Eo9aJ4Bt,
    https://open.spotify.com/playlist/2JUdrxncd30zv3VRJkLaZS,
    https://open.spotify.com/playlist/5mNmEqtjAnqjXaVFkNZ5ET,
    https://open.spotify.com/playlist/3DInsqW7PC1gDisXkIV22x
""")

# FUNCTIONS defined
def retrieve_dataframe():

    if client_id and client_secret and playlist_input and ready_button:
        
        user = spotipy_workshop.SpotifyUser(client_id, client_secret)
        
        if len(playlist_input.split(',')) > 1:
            playlist_df = spotipy_workshop.multiple_playlists(user, playlist_input)
            playlist_df = playlist_df.drop_duplicates(subset=['title', 'artist'], keep='first').reset_index(drop=True)
        
        else:
            playlist_df = spotipy_workshop.get_playlist_df(user, playlist_input)
            playlist_df = playlist_df.drop_duplicates(subset=['title', 'artist'], keep='first').reset_index(drop=True)

        return playlist_df

ready_button = st.sidebar.checkbox('Gather Data Report', on_change=retrieve_dataframe)
st.sidebar.header("Resources")
st.sidebar.write("Follow the guides below if you are unsure of how to install and/or interact with the app.")
st.sidebar.write("`Installation Guide`")
st.sidebar.write("`User Interaction Guide`")
data = retrieve_dataframe()

def filter_dataframe(df):
    if ready_button:
        with st.beta_expander("Search or Filter", False):
            
            search_filter = st.radio(label='', options=['Search','Filter'])

            if search_filter == 'Search':
                
                search_cols = st.beta_columns(4)
                search_song = search_cols[0].text_input('Song')
                search_artist = search_cols[1].text_input('Artist')
                search_album = search_cols[2].text_input('Album')
                search_year = search_cols[3].slider('Minimum Year',
                                                            min_value=df['artist_date'].min().year,
                                                            max_value=df['artist_date'].max().year,
                                                            step=1, help='Filters selected minimum year to most recent year')

                submit = st.button(label='Search')
                if submit:
                    # ROC1: all empty fields
                    if (search_album == '') & (search_artist == '') & (search_song == '') & (search_year == df['artist_date'].min().year):
                        st.error('INPUT ERROR: Specify one or more parameters')

                    # R1C1: no empty fields
                    elif (search_song != '') & (search_artist != '') & (search_album != '') & (search_year != df['artist_date'].min().year):
                        if (search_song.strip() in df['title'].unique()) & (search_artist.strip() in df['artist'].unique()) & (search_album.strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.strip()) | (df['artist'] == search_artist.strip()) | (df['album'] == search_album.strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.upper().strip() in df['title'].unique()) & (search_artist.upper().strip() in df['artist'].unique()) & (search_album.upper().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.upper().strip()) | (df['artist'] == search_artist.upper().strip()) | (df['album'] == search_album.upper().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.lower().strip() in df['title'].unique()) & (search_artist.lower().strip() in df['artist'].unique()) & (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.lower().strip()) | (df['artist'] == search_artist.lower().strip()) | (df['album'] == search_album.lower().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.title().strip() in df['title'].unique()) & (search_artist.title().strip() in df['artist'].unique()) & (search_album.title().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.title().strip()) | (df['artist'] == search_artist.title().strip()) | (df['album'] == search_album.title().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_artist} or "{search_album}" or "{search_year}"')
                    
                    # R2C1: no song field
                    elif (search_artist != '') & (search_album != ''):
                        if (search_artist.strip() in df['artist'].unique()) & (search_album.strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.strip()) | (df['album'] == search_album.strip())].reset_index(drop=True))
                        elif (search_artist.upper().strip() in df['artist'].unique()) & (search_album.upper().strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.upper().strip()) | (df['album'] == search_album.upper().strip())].reset_index(drop=True))
                        elif (search_artist.lower().strip() in df['artist'].unique()) & (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.lower().strip()) | (df['album'] == search_album.lower().strip())].reset_index(drop=True))
                        elif (search_artist.title().strip() in df['artist'].unique()) & (search_album.title().strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.title().strip()) | (df['album'] == search_album.title().strip())].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_artist} or "{search_album}"')

                    # R2C2: no year field
                    elif (search_song != '') & (search_artist != '') & (search_album != ''):
                        if (search_song.strip() in df['title'].unique()) & (search_artist.strip() in df['artist'].unique()) & (search_album.strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.strip()) | (df['artist'] == search_artist.strip()) | (df['album'] == search_album.strip())].reset_index(drop=True))
                        elif (search_song.upper().strip() in df['title'].unique()) & (search_artist.upper().strip() in df['artist'].unique()) & (search_album.upper().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.upper().strip()) | (df['artist'] == search_artist.upper().strip()) | (df['album'] == search_album.upper().strip())].reset_index(drop=True))
                        elif (search_song.lower().strip() in df['title'].unique()) & (search_artist.lower().strip() in df['artist'].unique()) & (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.lower().strip()) | (df['artist'] == search_artist.lower().strip()) | (df['album'] == search_album.lower().strip())].reset_index(drop=True))
                        elif (search_song.title().strip() in df['title'].unique()) & (search_artist.title().strip() in df['artist'].unique()) & (search_album.title().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.title().strip()) | (df['artist'] == search_artist.title().strip()) | (df['album'] == search_album.title().strip())].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_artist} or "{search_album}"')

                    # R2C3: no album field
                    elif (search_song != '') & (search_artist != '') & (search_year != df['artist_date'].min().year):
                        if (search_song.strip() in df['title'].unique()) & (search_artist.strip() in df['artist'].unique()):
                            st.dataframe(df[(df['title'] == search_song.strip()) | (df['artist'] == search_artist.strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.upper().strip() in df['title'].unique()) & (search_artist.upper().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['title'] == search_song.upper().strip()) | (df['artist'] == search_artist.upper().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.lower().strip() in df['title'].unique()) & (search_artist.lower().strip() in df['artist'].unique()) & (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.lower().strip()) | (df['artist'] == search_artist.lower().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.title().strip() in df['title'].unique()) & (search_artist.title().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['title'] == search_song.title().strip()) | (df['artist'] == search_artist.title().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_artist} or "{search_year}"')

                    # R2C4" no artist field
                    elif (search_song != '') & (search_album != '') & (search_year != df['artist_date'].min().year):
                        if (search_song.strip() in df['title'].unique()) & (search_album.strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.strip()) | (df['album'] == search_album.strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.upper().strip() in df['title'].unique()) & (search_album.upper().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.upper().strip()) | (df['album'] == search_album.upper().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.lower().strip() in df['title'].unique()) & (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.lower().strip()) | (df['album'] == search_album.lower().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.title().strip() in df['title'].unique()) & (search_album.title().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.title().strip()) | (df['album'] == search_album.title().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_album}" or "{search_year}"')

                    # R3C1: no album field, no year field
                    elif (search_song != '') & (search_artist != ''):
                        if (search_song.strip() in df['title'].unique()) & (search_artist.strip() in df['artist'].unique()):
                            st.dataframe(df[(df['title'] == search_song.strip()) | (df['artist'] == search_artist.strip())].reset_index(drop=True))
                        elif (search_song.upper().strip() in df['title'].unique()) & (search_artist.upper().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['title'] == search_song.upper().strip()) | (df['artist'] == search_artist.upper().strip())].reset_index(drop=True))
                        elif (search_song.lower().strip() in df['title'].unique()) & (search_artist.lower().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['title'] == search_song.lower().strip()) | (df['artist'] == search_artist.lower().strip())].reset_index(drop=True))
                        elif (search_song.title().strip() in df['title'].unique()) & (search_artist.title().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['title'] == search_song.title().strip()) | (df['artist'] == search_artist.title().strip())].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_artist}')

                    # R3C2: no artist field, no year field
                    elif (search_song != '') & (search_album != ''):
                        st.write('SONG AND ALBUM')
                        if (search_song.strip() in df['title'].unique()) & (search_album.strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.strip()) | (df['album'] == search_album.strip())].reset_index(drop=True))
                        elif (search_song.upper().strip() in df['title'].unique()) & (search_album.upper().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.upper().strip()) | (df['album'] == search_album.upper().strip())].reset_index(drop=True))
                        elif (search_song.lower().strip() in df['title'].unique()) & (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.lower().strip()) | (df['album'] == search_album.lower().strip())].reset_index(drop=True))
                        elif (search_song.title().strip() in df['title'].unique()) & (search_album.title().strip() in df['album'].unique()):
                            st.dataframe(df[(df['title'] == search_song.title().strip()) | (df['album'] == search_album.title().strip())].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_album}')
                    
                    # R3C3: no artist field, no album field
                    elif (search_song != '') & (search_year != df['artist_date'].min().year):
                        if (search_song.strip() in df['title'].unique()):
                            st.dataframe(df[(df['title'] == search_song.strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.upper().strip() in df['title'].unique()):
                            st.dataframe(df[(df['title'] == search_song.upper().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.lower().strip() in df['title'].unique()):
                            st.dataframe(df[(df['title'] == search_song.lower().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_song.title().strip() in df['title'].unique()):
                            st.dataframe(df[(df['title'] == search_song.title().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_year}')

                    # R3C4: no song field, no year field
                    elif (search_artist != '') & (search_album != ''):
                        if (search_artist.strip() in df['artist'].unique()) & (search_album.strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.strip()) | (df['album'] == search_album.strip())].reset_index(drop=True))
                        elif (search_artist.upper().strip() in df['artist'].unique()) & (search_album.upper().strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.upper().strip()) | (df['album'] == search_album.upper().strip())].reset_index(drop=True))
                        elif (search_artist.lower().strip() in df['artist'].unique()) & (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.lower().strip()) | (df['album'] == search_album.lower().strip())].reset_index(drop=True))
                        elif (search_artist.title().strip() in df['artist'].unique()) & (search_album.title().strip() in df['album'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.title().strip()) | (df['album'] == search_album.title().strip())].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_artist}" or "{search_album}')

                    # R3C5: no song field, no album field
                    elif (search_artist != '') & (search_year != df['artist_date'].min().year):
                        if (search_artist.strip() in df['artist'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_artist.upper().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.upper().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_artist.lower().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.lower().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_artist.title().strip() in df['artist'].unique()):
                            st.dataframe(df[(df['artist'] == search_artist.title().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_year}')
                    
                    # R3C6: no song field, no artist field
                    elif (search_album != '') & (search_year != df['artist_date'].min().year):
                        if (search_album.strip() in df['album'].unique()):
                            st.dataframe(df[(df['album'] == search_album.strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_album.upper().strip() in df['album'].unique()):
                            st.dataframe(df[(df['album'] == search_album.upper().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_album.lower().strip() in df['album'].unique()):
                            st.dataframe(df[(df['album'] == search_album.lower().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        elif (search_album.title().strip() in df['album'].unique()):
                            st.dataframe(df[(df['album'] == search_album.title().strip()) | (df['artist_date'] >= datetime.date(datetime(search_year,1,1)))].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find one of "{search_song}" or "{search_year}')
                    
                    # R4C1: no aritst field, no album field, no year field
                    elif search_song != '':
                        st.write('SONG')
                        if search_song.strip() in df['title'].unique():
                            st.dataframe(df[df['title'] == search_song.strip()].reset_index(drop=True))
                        elif search_song.upper().strip() in df['title'].unique():
                            st.dataframe(df[df['title'] == search_song.upper().strip()].reset_index(drop=True))
                        elif search_song.lower().strip() in df['title'].unique():
                            st.dataframe(df[df['title'] == search_song.title().lower()].reset_index(drop=True))
                        elif search_song.title().strip() in df['title'].unique():
                            st.dataframe(df[df['title'] == search_song.title().strip()].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find song "{search_song}"')
                    
                    # R4C2: no song field, no album field, no year field
                    elif search_artist != '':
                        st.write('ARTIST')
                        if search_artist.strip() in df['artist'].unique():
                            st.dataframe(df[df['artist'] == search_artist.strip()].reset_index(drop=True))
                        elif search_artist.upper().strip() in df['artist'].unique():
                            st.dataframe(df[df['artist'] == search_artist.upper().strip()].reset_index(drop=True))
                        elif search_artist.lower().strip() in df['artist'].unique():
                            st.dataframe(df[df['artist'] == search_artist.lower().strip()].reset_index(drop=True))
                        elif search_artist.title().strip() in df['artist'].unique():
                            st.dataframe(df[df['artist'] == search_artist.title().strip()].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find artist "{search_artist}"')

                    # R4C2: no song field, no artist field, no year field
                    elif search_album != '':
                        st.write('ALBUM')
                        if search_album.strip() in df['album'].unique():
                            st.dataframe(df[df['album'] == search_album.strip()].reset_index(drop=True))
                        elif search_album.upper().strip() in df['album'].unique():
                            st.dataframe(df[df['album'] == search_album.upper().strip()].reset_index(drop=True))
                        elif search_album.lower().strip() in df['album'].unique():
                            st.dataframe(df[df['album'] == search_album.lower().strip()].reset_index(drop=True))
                        elif search_album.title().strip() in df['album'].unique():
                            st.dataframe(df[df['album'] == search_album.title().strip()].reset_index(drop=True))
                        else:
                            st.error(f'Cannot find album "{search_album}"')
                    
                    # R4C3: no song field, no artist field, no album field
                    elif search_year != df['artist_date'].min().year:
                        st.dataframe(df[df['artist_date'] >= datetime.date(datetime(search_year,1,1))].reset_index(drop=True))
                    
                    # R5C0: super weird exception; should never execute
                    else:
                        st.error("CODE ERROR: Please contact author to report bug.")



            if search_filter == 'Filter':
                
                filter_cols = st.beta_columns((3,3,2))
                filter_playlist = filter_cols[0].multiselect('Playlist', options=np.sort(data['playlist'].unique()))
                filter_artist = filter_cols[1].multiselect('Artist', options=np.sort(data['artist'].unique()))
                filter_release = filter_cols[2].slider('Year Range',
                                                            min_value=df['artist_date'].min().year,
                                                            max_value=df['artist_date'].max().year,
                                                            value = (df['artist_date'].min().year, df['artist_date'].max().year),
                                                            step=1)
                
                submit = st.button(label='Filter')
                
                if submit:

                    # R0C1: all empty fields
                    if (filter_playlist == []) & (filter_artist == []) & (filter_release == (df['artist_date'].min().year, df['artist_date'].max().year)):
                        st.dataframe(df)
                    
                    # R3C1: filter playlists, filter artists, filter date
                    elif (filter_playlist != []) & (filter_artist != []) & (filter_release != (df['artist_date'].min().year, df['artist_date'].max().year)):
                        st.dataframe(df[(df['playlist'].isin(filter_playlist)) & (df['artist'].isin(filter_artist)) & (df['artist_date'].astype(str).str[:4].astype(int).isin(range(filter_release[0],filter_release[1]+1)))].reset_index(drop=True))
                    
                    # R2C1: filter playlists, filter artists
                    elif (filter_playlist != []) & (filter_artist != []):
                        st.dataframe(df[(df['playlist'].isin(filter_playlist)) & (df['artist'].isin(filter_artist))].reset_index(drop=True))
                    
                    # R2C2: filter playlists, filter date
                    elif (filter_playlist != []) & (filter_release != (df['artist_date'].min().year, df['artist_date'].max().year)):
                        st.dataframe(df[(df['playlist'].isin(filter_playlist)) & (df['artist_date'].astype(str).str[:4].astype(int).isin(range(filter_release[0],filter_release[1]+1)))].reset_index(drop=True))
                    
                    # R2C3: filter artists, filter date
                    elif (filter_artist != []) & (filter_release != (df['artist_date'].min().year, df['artist_date'].max().year)):
                        st.dataframe(df[(df['artist'].isin(filter_artist)) & (df['artist_date'].astype(str).str[:4].astype(int).isin(range(filter_release[0],filter_release[1]+1)))].reset_index(drop=True))
                    
                    # R1C1: filter playlists
                    elif filter_playlist != []:
                        st.dataframe(df[(df['playlist'].isin(filter_playlist))]).reset_index(drop=True)
                    
                    # R1C2: filter artists
                    elif filter_artist != []:
                        st.dataframe(df[df['artist'].isin(filter_artist)].reset_index(drop=True))
                    
                    # R1C3: filter date
                    elif filter_release != (df['artist_date'].min().year, df['artist_date'].max().year):
                        st.dataframe(df[df['artist_date'].astype(str).str[:4].astype(int).isin(range(filter_release[0],filter_release[1]+1))].reset_index(drop=True))


filter_dataframe(data)
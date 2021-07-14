import streamlit as st
import pandas as pd
import numpy as np
import matplotlib

import spotify_agent
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy.oauth2 as oauth2

import scipy
from plotly import figure_factory as ff

class Error(Exception):
    """Base class for all other exceptions"""
    pass

# THEME settings
st.set_page_config(layout='wide')

# BODY page layout
st.title('Spotify Analysis Dashboard')

st.write("""Welcome to `spotify_analysis`, the application you run when you don't want to wait for Spotify Rewind!
            This application provides an up-to-date, on-command analysis of the user's requested Spotify playlist(s).
            Using Spotify's API functionality, all data is secure and not being collected by utilization of this app.
        """)

# SIDEBAR page layout
st.sidebar.header('Client Information')
st.sidebar.write("""Please follow the `Installation Guide` and `User Interaction Guide`
                    to properly interact with the application.
                """)

# FUNCTIONS defined
def retrieve_dataframe():
    
    client_id = st.sidebar.text_input('Client ID: ')
    client_secret = st.sidebar.text_input('Client secret: ')
    playlist_input = st.sidebar.text_area('Playlist URL(s): ')
    ready_button = st.sidebar.button('Gather Data Report')

    if client_id and client_secret and playlist_input and ready_button:

        user = spotify_agent.SpotifyUser(client_id, client_secret)

        if len(playlist_input.split(',')) > 1:
            playlists_df = spotify_agent.multiple_playlists(user, playlist_input)
            # select playlists
            # st.header('Playlist: {}'.format(sp.playlist(playlist_url)['name']))
            st.dataframe(playlists_df.drop_duplicates(subset=['title', 'artist'], keep='first').reset_index(drop=True))
            return playlists_df

        else:
            playlist_df = spotify_agent.get_playlist_df(user, playlist_input)
            st.dataframe(playlist_df.reset_index(drop=True))
            return playlist_df
data = retrieve_dataframe()

# def filter_dataframe(dataframe):
    # st.header('Filter by any of the parameters below:')
    # st.multiselect('Select playlists to include in analysis', )

# def retrieve_plot():
#    pass

# st.bar_chart(spotify_agent.histogram_plot(data, 'length'))

# CALLING functions
# plot = retrieve_plot()

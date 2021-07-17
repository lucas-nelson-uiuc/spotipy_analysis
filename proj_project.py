import proj_pipeline
import proj_analysis
import proj_plot

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

import spotipy as sp
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
                    page_icon=Image.open('logo.png'),
                    layout='wide')

# BODY page layout
st.title('Spotify Analysis Dashboard')

# SIDEBAR page layout
with st.sidebar.beta_expander('Enter Spotify Details', False):
    client_id = st.text_input('Client ID', '') # enter client_id
    client_secret = st.text_input('Client secret', '') # enter client_secret
    playlist_input = st.text_area('Playlist URL(s)', '') # enter playlist url(s)
    ready_button = st.checkbox('Gather Data Frame')

with st.sidebar.beta_expander('Dashboard Resources', False):
    st.write("[`Installation Guide`](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")
    st.write("[`Interaction Guide`](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")

with st.sidebar.beta_expander('Feedback', False):
    if st.slider("How much did you enjoy using this dashboard?", min_value=0, max_value=100, value=50, step=1):
        st.write('Are you sure about that?')
    if st.selectbox("Did you experience any bugs?", options=['Yes', 'No']):
        st.write("Thank you for reporting!")


st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)


# FUNCTIONS defined
def retrieve_dataframe():

    if client_id and client_secret and playlist_input and ready_button:
        
        user = proj_pipeline.SpotifyUser(client_id, client_secret)
        
        if len(playlist_input.split(',')) > 1:
            playlist_df = proj_pipeline.pipeline_multip_spotify(user, playlist_input)
            playlist_df = playlist_df.drop_duplicates(subset=['title', 'artist'], keep='first').reset_index(drop=True)
        
        else:
            playlist_df = proj_pipeline.pipeline_single_spotify(user, playlist_input)
            playlist_df = playlist_df.drop_duplicates(subset=['title', 'artist'], keep='first').reset_index(drop=True)

        return playlist_df

data = retrieve_dataframe()

def alter_dataframe(df):
    
    if ready_button:
        
        with st.beta_expander("Interact with Data Frame", False):
            
            search_filter = st.radio(label='', options=['Filter','Search'])

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
                    return proj_analysis.analysis_filter_dataframe(df, filter_playlist, filter_artist, filter_release)
            
            if search_filter == 'Search':
                
                search_cols = st.beta_columns(4)
                search_song = search_cols[0].text_input('Song')
                search_artist = search_cols[1].text_input('Artist')
                search_album = search_cols[2].text_input('Album')
                search_year = search_cols[3].slider('Year Range',
                                                            min_value=df['artist_date'].min().year,
                                                            max_value=df['artist_date'].max().year,
                                                            value = (df['artist_date'].min().year, df['artist_date'].max().year),
                                                            step=1)
                submit = st.button(label='Search')

                if submit:
                    return proj_analysis.analysis_search_dataframe(df, client_id, client_secret, search_song, search_artist, search_album, search_year)

f_data = alter_dataframe(data)

# placing basic statistics
with st.beta_container():

    row1 = st.beta_columns((1,1,0.8,1,1,1))

    row1_col1 = row1[0].header(f_data['title'].unique().shape[0])
    row1_col2 = row1[1].header(f_data['artist'].unique().shape[0])
    row1_col3 = row1[2].header(f_data['album'].unique().shape[0])
    row1_col4 = row1[3].header(proj_analysis.analysis_time_convert(f_data))
    row1_col5 = row1[4].header(round(f_data['popularity'].mean()))
    row1_col6 = row1[5].header(f_data['explicit'].sum())

    row1_col1 = row1[0].write('tracks')
    row1_col2 = row1[1].write('artists')
    row1_col3 = row1[2].write('albums')
    row1_col4 = row1[3].write('duration')
    row1_col5 = row1[4].write('popularity')
    row1_col6 = row1[5].write('explicit')

def plot_histogram(df):
    return proj_plot.proj_plot_hist(df, 'duration')

# plotting histogram
with st.beta_container():

    hist_row1 = st.beta_columns((4,6))
    hist_desc = hist_row1[0].header('Song Duration Over Time')
    hist_desc = hist_row1[0].markdown(
        "Visualize how the duration of your music has changed over time. Most trends follow a right skew, meaning there is a disproportionate amount"
        "of outliers on the right tail compared to the rest of the distribution."
        "Compared to historical data, [enter some cool insight about user's distribution.]"
        )
    hist_hist = hist_row1[1].pyplot(plot_histogram(f_data))
    

# def plot_nested_pies(df):
#     return st.pyplot(proj_plot.proj_plot_nestpie(df, 'genre'))

# plot_nested_pies(f_data)

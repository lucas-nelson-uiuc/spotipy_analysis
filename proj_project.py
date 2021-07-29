import proj_pipeline
import proj_analysis
import proj_plot

import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy.oauth2 as oauth2

# import scipy
# from plotly import figure_factory as ff
# from datetime import datetime

# THEME SETTINGS
st.set_page_config(page_title='Spotify Analysis Dashboard',
                    page_icon=Image.open('logo.png'),
                    layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)

# TITLE SECTION
st.title('Spotify Analysis Dashboard')

# GATHER INPUT DATA
with st.sidebar.beta_expander('Enter Input Data', True):
        client_id = st.text_input('Client ID', '3369a177760443e1ba8fdc24ffe8ee3a')
        client_secret = st.text_input('Client secret', '26557253d83447879b0ff7251d291517')
        playlist_input = st.text_area('Playlist URL(s)', """https://open.spotify.com/playlist/2peFCkryOU68kcEueeBmcw,
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
        ready_button = st.checkbox('Gather Data Frame')

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

# DATAFRAME FUNCTIONS
radio_page = st.empty()
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
def alter_dataframe(df):
    
    if ready_button:
        
        with st.sidebar.beta_expander("Select Data", False):
            global radio_page
            search_filter = st.radio(label='', options=['Filter','Search'])

            if search_filter == 'Filter':

                st.subheader('Filter Parameters')
                filter_playlist = st.multiselect('Playlist', options=list(np.sort(data['playlist'].unique())))
                filter_artist = st.multiselect('Artist', options=list(np.sort(data['artist'].unique())))
                filter_release = st.slider('Release Date',
                                            min_value=df['artist_date'].min().year,
                                            max_value=df['artist_date'].max().year,
                                            value = (df['artist_date'].min().year, df['artist_date'].max().year),
                                            step=1)
                st.subheader('Dashboard Views')
                radio_page = st.multiselect(label='Select at least one', options=['Tracks', 'Artists', 'Albums', 'Genre Breakdown', 'Listening Trends', 'Spotify Usage', 'Attribute Correlations', 'Random Statistics', 'Recommendations [Beta]'])
                submit = st.button(label='Filter')
                
                if submit:
                    return proj_analysis.analysis_filter_dataframe(df, filter_playlist, filter_artist, filter_release)
            
            if search_filter == 'Search':
                
                st.subheader('Search Parameters')
                search_song = st.text_input('Song')
                search_artist = st.text_input('Artist')
                search_album = st.text_input('Album')
                search_year = st.slider('Release Date',
                                        min_value=df['artist_date'].min().year,
                                        max_value=df['artist_date'].max().year,
                                        value = (df['artist_date'].min().year, df['artist_date'].max().year),
                                        step=1)
                st.subheader('Dashboard Views')
                radio_page = st.multiselect(label='Select at least one', options=['Tracks', 'Artists', 'Albums', 'Genre Breakdown', 'Listening Trends', 'Spotify Usage', 'Attribute Correlations', 'Random Statistics', 'Recommendations [Beta]'])
                submit = st.button(label='Search')

                if submit:
                    return proj_analysis.analysis_search_dataframe(df, client_id, client_secret, search_song, search_artist, search_album, search_year)
def project_pretty_time(time):
    duration_mins = time / 60000
    hours = int(duration_mins // 60)
    minutes = int(((duration_mins / 60) - hours) * 60)
    seconds = abs(round((((duration_mins / 60) - hours) * 60 - round(((duration_mins / 60) - hours) * 60)) * 60))
    if hours >= 1:
        return f'{hours}h{minutes}m{seconds}s'
    elif minutes >= 1:
        return f'{minutes}m{seconds}s'
    elif seconds >= 1:
        return f'{seconds}s'
    else:
        return 'unspecified'

# PAGE SKELETONS
def project_quick_stats():
    row1 = st.beta_columns((1, 0.8,0.8,0.8,0.8,0.8))
    row1_col0 = row1[0].subheader(proj_analysis.analysis_pretty_time(f_data))
    row1_col1 = row1[1].subheader(f_data['title'].unique().shape[0])
    row1_col2 = row1[2].subheader(f_data['artist'].unique().shape[0])
    row1_col3 = row1[3].subheader(f_data['album'].unique().shape[0])
    row1_col4 = row1[4].subheader(f_data[f_data['genre'] != 'NA']['genre'].unique().shape[0])
    row1_col5 = row1[5].subheader("{}%".format(round(f_data['popularity'].mean())))

    row1_col0 = row1[0].write('duration')
    row1_col1 = row1[1].write('tracks')
    row1_col2 = row1[2].write('artists')
    row1_col3 = row1[3].write('albums')
    row1_col4 = row1[4].write('genres')
    row1_col5 = row1[5].write('popularity')

    return row1, row1_col0, row1_col1, row1_col2, row1_col3, row1_col4, row1_col5
def project_tracks_page(df):
    
    for col in df.columns:
        if col in ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']:
            df[col] = df[col].multiply(100).round(2)
        if col == 'loudness':
            df[col] = df[col].multiply(-(100/60)).round(2)

    #max length
    cols_group = st.beta_columns((1,1,1,1))
    cols_group[0].title('{}'.format(project_pretty_time(df.loc[df['duration'].argmax(), 'duration'])))
    cols_group[0].image('{}'.format(df.loc[df['duration'].argmax(), 'img_url']))
    cols_group[0].subheader('Longest Track')
    cols_group[0].write('{}'.format(df.loc[df['duration'].argmax(), 'title']))
    #min length
    cols_group[1].title('{}'.format(project_pretty_time(df.loc[df['duration'].argmin(), 'duration'])))
    cols_group[1].image('{}'.format(df.loc[df['duration'].argmin(), 'img_url']))
    cols_group[1].subheader('Shortest Track')
    cols_group[1].write('{}'.format(df.loc[df['duration'].argmin(), 'title']))
    #oldest track
    cols_group[2].title('{}'.format(df[df['artist_date'] == min(df['artist_date'])]['artist_date'].iloc[0,]))
    cols_group[2].image('{}'.format(df[df['artist_date'] == min(df['artist_date'])]['img_url'].iloc[0,]))
    cols_group[2].subheader('Oldest Track')
    cols_group[2].write('{}'.format(df[df['artist_date'] == min(df['artist_date'])]['title'].iloc[0,]))
    #newest track
    cols_group[3].title('{}'.format(df[df['artist_date'] == max(df['artist_date'])]['artist_date'].iloc[0,]))
    cols_group[3].image('{}'.format(df[df['artist_date'] == max(df['artist_date'])]['img_url'].iloc[0,]))
    cols_group[3].subheader('Newest Track')
    cols_group[3].write('{}'.format(df[df['artist_date'] == max(df['artist_date'])]['title'].iloc[0,]))

    # ADDED TRACK GROUPS
    #added recent
    adds_group = st.beta_columns((1,1,1,1))
    adds_group[0].title('{}'.format(df[df['user_date'] == max(df['user_date'])]['user_date'].iloc[0,]))
    adds_group[0].image('{}'.format(df[df['user_date'] == max(df['user_date'])]['img_url'].iloc[0,]))
    adds_group[0].subheader('Added Most Recently')
    adds_group[0].write('{}'.format(df[df['user_date'] == max(df['user_date'])]['title'].iloc[0,]))
    #added old
    adds_group[1].title('{}'.format(df[df['user_date'] == min(df['user_date'])]['user_date'].iloc[0,]))
    adds_group[1].image('{}'.format(df[df['user_date'] == min(df['user_date'])]['img_url'].iloc[0,]))
    adds_group[1].subheader('Added Least Recently')
    adds_group[1].write('{}'.format(df[df['user_date'] == min(df['user_date'])]['title'].iloc[0,]))
    #added earliest day
    adds_group[2].title('{}'.format(df[df['user_time'] == min(df['user_time'])]['user_time'].iloc[0,]))
    adds_group[2].image('{}'.format(df[df['user_time'] == min(df['user_time'])]['img_url'].iloc[0,]))
    adds_group[2].subheader('Added Earliest in Day')
    adds_group[2].write('{}'.format(df[df['user_time'] == min(df['user_time'])]['title'].iloc[0,]))
    #added latest day
    adds_group[3].title('{}'.format(df[df['user_time'] == max(df['user_time'])]['user_time'].iloc[0,]))
    adds_group[3].image('{}'.format(df[df['user_time'] == max(df['user_time'])]['img_url'].iloc[0,]))
    adds_group[3].subheader('Added Latest in Day')
    adds_group[3].write('{}'.format(df[df['user_time'] == max(df['user_time'])]['title'].iloc[0,]))
    
    #POPULAR
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Popularity')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].write('''
        The popularity of a track is a value between 0 and 100, with 100 being the most popular.
        The popularity is calculated by algorithm and is based, in the most part, on the total
        number of plays the track has had and how recent those plays are.
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['popularity'].argmax(), 'popularity']))
    attr_group[1].image('{}'.format(df.loc[df['popularity'].argmax(), 'img_url']))
    attr_group[1].subheader('Most Popular Track')
    attr_group[1].write('{}'.format(df.loc[df['popularity'].argmax(), 'title']))
    #least popular
    arg_df = df[df['popularity'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['popularity'].argmin(), 'popularity']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['popularity'].argmin(), 'img_url']))
    attr_group[2].subheader('Least Popular Track')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['popularity'].argmin(), 'title']))

    #DANCEABILITY
    attr_group = st.beta_columns((2,1,1))
    #danceable description
    attr_group[0].title('Danceability')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].markdown('''
        Danceability describes how suitable a track is for dancing based on a
        combination of musical elements including tempo, rhythm stability, beat strength,
        and overall regularity. A value of 0 is least danceable and 100 is most danceable.
    ''')
    #most danceable
    attr_group[1].title('{}'.format(df.loc[df['danceability'].argmax(), 'danceability']))
    attr_group[1].image('{}'.format(df.loc[df['danceability'].argmax(), 'img_url']))
    attr_group[1].subheader('Most Danceable Track')
    attr_group[1].write('{}'.format(df.loc[df['danceability'].argmax(), 'title']))
    #least danceable
    arg_df = df[df['danceability'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['danceability'].argmin(), 'danceability']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['danceability'].argmin(), 'img_url']))
    attr_group[2].subheader('Least Danceable Track')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['danceability'].argmin(), 'title']))

    #ENERGY
    attr_group = st.beta_columns((2,1,1))
    #energetic description
    attr_group[0].title('Energy')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].markdown('''
        Energy is a measure from 0 to 100 and represents a perceptual measure of
        intensity and activity. Typically, energetic tracks feel fast, loud, and noisy.
        For example, death metal has high energy, while a Bach prelude scores low on the 
        scale. Perceptual features contributing to this attribute include dynamic range,
        perceived loudness, timbre, onset rate, and general entropy.
    ''')
    #most energetic
    attr_group[1].title('{}'.format(df.loc[df['energy'].argmax(), 'energy']))
    attr_group[1].image('{}'.format(df.loc[df['energy'].argmax(), 'img_url']))
    attr_group[1].subheader('Most Popular Track')
    attr_group[1].write('{}'.format(df.loc[df['energy'].argmax(), 'title']))
    #least energetic
    arg_df = df[df['energy'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['energy'].argmin(), 'energy']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['energy'].argmin(), 'img_url']))
    attr_group[2].subheader('Least Popular Track')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['energy'].argmin(), 'title']))
    
    #LOUDNESS
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Loudness')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].write('''
        Overall loudness of a track in adjusted decibels (dB * -100/60). Loudness values
        are averaged across the entire track and are useful for comparing relative loudness
        of tracks. Loudness is the quality of a sound that is the primary psychological 
        correlate of physical strength (amplitude).
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['loudness'].argmax(), 'loudness']))
    attr_group[1].image('{}'.format(df.loc[df['loudness'].argmax(), 'img_url']))
    attr_group[1].subheader('Loudest Track')
    attr_group[1].write('{}'.format(df.loc[df['loudness'].argmax(), 'title']))
    #least popular
    arg_df = df[df['loudness'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['loudness'].argmin(), 'loudness']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['loudness'].argmin(), 'img_url']))
    attr_group[2].subheader('Quietest Track')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['loudness'].argmin(), 'title']))

    #SPEECHINESS
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Speechiness')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].write('''
        Speechiness detects the presence of spoken words in a track. The more exclusively
        speech-like the recording (e.g. talk show, audio book, poetry), the closer to 100
        the attribute value. Values above 66 describe tracks that are probably made entirely
        of spoken words. Values between 33 and 66 describe tracks that may contain both music
        and speech, either in sections or layered, including such cases as rap music. Values
        below 33 most likely represent music and other non-speech-like tracks.
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['speechiness'].argmax(), 'speechiness']))
    attr_group[1].image('{}'.format(df.loc[df['speechiness'].argmax(), 'img_url']))
    attr_group[1].subheader('Highest Speechiness')
    attr_group[1].write('{}'.format(df.loc[df['speechiness'].argmax(), 'title']))
    #least popular
    arg_df = df[df['speechiness'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['speechiness'].argmin(), 'speechiness']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['speechiness'].argmin(), 'img_url']))
    attr_group[2].subheader('Lowest Speechiness')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['speechiness'].argmin(), 'title']))

    #ACOUSTICNESS
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Acousticness')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].markdown('''
        Confidence measure from 0 to 100 of whether the track is acoustic.
        100 represents high confidence the track is acoustic.
        0 represents low confidence the track is not acoustic.
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['acousticness'].argmax(), 'acousticness']))
    attr_group[1].image('{}'.format(df.loc[df['acousticness'].argmax(), 'img_url']))
    attr_group[1].subheader('Highest Acousticness')
    attr_group[1].write('{}'.format(df.loc[df['acousticness'].argmax(), 'title']))
    #least popular
    arg_df = df[df['acousticness'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['acousticness'].argmin(), 'acousticness']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['acousticness'].argmin(), 'img_url']))
    attr_group[2].subheader('Lowest Acousticness')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['acousticness'].argmin(), 'title']))

    #INSTRUMENTALNESS
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Instrumentalness')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].write('''
        Predicts whether a track contains no vocals. Rap or spoken word tracks are clearly “vocal”.
        The closer the instrumentalness value is to 100, the greater likelihood the track contains
        no vocal content. Values above 50 are intended to represent instrumental tracks,
        but confidence is higher as the value approaches 100.
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['instrumentalness'].argmax(), 'instrumentalness']))
    attr_group[1].image('{}'.format(df.loc[df['instrumentalness'].argmax(), 'img_url']))
    attr_group[1].subheader('Highest Instrumentalness')
    attr_group[1].write('{}'.format(df.loc[df['instrumentalness'].argmax(), 'title']))
    #least popular
    arg_df = df[df['instrumentalness'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['instrumentalness'].argmin(), 'instrumentalness']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['instrumentalness'].argmin(), 'img_url']))
    attr_group[2].subheader('Lowest Instrumentalness')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['instrumentalness'].argmin(), 'title']))

    #LIVENESS
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Liveness')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].write('''
        Detects the presence of an audience in the recording. Higher liveness values
        represent an increased probability that the track was performed live.
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['liveness'].argmax(), 'liveness']))
    attr_group[1].image('{}'.format(df.loc[df['liveness'].argmax(), 'img_url']))
    attr_group[1].subheader('Highest Liveness')
    attr_group[1].write('{}'.format(df.loc[df['liveness'].argmax(), 'title']))
    #least popular
    arg_df = df[df['liveness'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['liveness'].argmin(), 'liveness']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['liveness'].argmin(), 'img_url']))
    attr_group[2].subheader('Lowest Liveness')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['liveness'].argmin(), 'title']))

    #VALENCE
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Valence')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].write('''
        Measure from 0 to 100 describing the musical positiveness conveyed by a track.
        Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while
        tracks with low valence sound more negative (e.g. sad, depressed, angry).
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['valence'].argmax(), 'valence']))
    attr_group[1].image('{}'.format(df.loc[df['valence'].argmax(), 'img_url']))
    attr_group[1].subheader('Highest Valence')
    attr_group[1].write('{}'.format(df.loc[df['valence'].argmax(), 'title']))
    #least popular
    arg_df = df[df['valence'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['valence'].argmin(), 'valence']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['valence'].argmin(), 'img_url']))
    attr_group[2].subheader('Lowest Valence')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['valence'].argmin(), 'title']))

    #TEMPO
    attr_group = st.beta_columns((2,1,1))
    #popular description
    attr_group[0].title('Tempo')
    attr_group[0].subheader('How does Spotify determine...')
    attr_group[0].write('''
        Overall estimated tempo of a track in beats per minute (BPM). In musical terminology,
        tempo is the speed or pace of a given piece and derives directly from the average beat
        duration.
    ''')
    #most popular
    attr_group[1].title('{}'.format(df.loc[df['tempo'].argmax(), 'tempo']))
    attr_group[1].image('{}'.format(df.loc[df['tempo'].argmax(), 'img_url']))
    attr_group[1].subheader('Fastest Tempo')
    attr_group[1].write('{}'.format(df.loc[df['tempo'].argmax(), 'title']))
    #least popular
    arg_df = df[df['tempo'] > 0].reset_index(drop=True)
    attr_group[2].title('{}'.format(arg_df.loc[arg_df['tempo'].argmin(), 'tempo']))
    attr_group[2].image('{}'.format(arg_df.loc[arg_df['tempo'].argmin(), 'img_url']))
    attr_group[2].subheader('Slowest Tempo')
    attr_group[2].write('{}'.format(arg_df.loc[arg_df['tempo'].argmin(), 'title']))

    #random song stats
def project_randm_page(df):
    idx = random.randint(0, df.shape[0])
    idx_title = df.loc[idx,'title']
    idx_artist = df.loc[idx,'artist']
    idx_album = df.loc[idx,'album']
    idx_genre = df.loc[idx,'genre']
    idx_track_url = df.loc[idx,'track_url']
    idx_img_url = df.loc[idx,'img_url']
    idx_duration = df.loc[idx,'duration']
    idx_explicit = df.loc[idx,'explicit']
    idx_popularity = df.loc[idx,'popularity']
    idx_artist_date = df.loc[idx,'artist_date']
    idx_user_date = df.loc[idx,'user_date']
    idx_user_time = df.loc[idx,'user_time']
    idx_danceability = (df.loc[idx,'danceability'] * 100).round(2)
    idx_energy = (df.loc[idx,'energy'] * 100).round(2)
    idx_loudness = (df.loc[idx,'loudness'] * (-100/60)).round(2)
    idx_speechiness = (df.loc[idx,'speechiness'] * 100).round(2)
    idx_acousticness = (df.loc[idx,'acousticness'] * 100).round(2)
    idx_instrumentalness = (df.loc[idx,'instrumentalness'] * 100).round(2)
    idx_liveness = (df.loc[idx,'liveness'] * 100).round(2)
    idx_valence = (df.loc[idx,'valence']* 100).round(2)
    idx_playlist = df.loc[idx,'playlist']

    
    rand_group = st.beta_columns((2,7))
    with rand_group[0]:
        st.image(idx_img_url)
    with rand_group[1]:
        spotify_logo = '[![this is an image link]({})]({})'.format('https://i.imgur.com/TejSfM3.png', idx_track_url)
        youtube_logo = '[![this is an image link]({})](https://www.youtube.com/results?search_query={})'.format('https://i.imgur.com/LkMsDsO.png', '+'.join(str(idx_artist + ' ' +  idx_title).split(' ')))
        wikiped_logo = '[![this is an image link]({})](https://en.wikipedia.org/wiki/{})'.format('https://i.imgur.com/UIllM9Y.png', '_'.join(idx_artist.split(' ')))
        googlee_logo = '[![this is an image link]({})](https://www.google.com/search?q={})'.format('https://i.imgur.com/SbD92XG.png', '+'.join(str(idx_artist + ' ' +  idx_title).split(' ')))
        twitter_logo = '[![this is an image link]({})](https://twitter.com/search?q={}&src=typed_query)'.format('https://i.imgur.com/XMNpp3p.png', '%20'.join(idx_artist.split(' ')))
        facebok_logo = '[![this is an image link]({})](https://www.facebook.com/search/top?q={})'.format('https://i.imgur.com/kvkQy1h.png', '%20'.join(idx_artist.split(' ')))
        redditt_logo = '[![this is an image link]({})](https://www.reddit.com/search/?q={})'.format('https://i.imgur.com/idnSbNj.png', '%20'.join(idx_artist.split(' ')))
        st.title(idx_title)
        st.subheader('Explore the music...')
        st.markdown(f"""
            {spotify_logo}&nbsp&nbsp&nbsp
            {youtube_logo}&nbsp&nbsp&nbsp
            {wikiped_logo}&nbsp&nbsp&nbsp
            {googlee_logo}&nbsp&nbsp&nbsp
            {twitter_logo}&nbsp&nbsp&nbsp
            {facebok_logo}&nbsp&nbsp&nbsp
            {redditt_logo}
        """)

    rand_group = st.beta_columns((1.5,2,2,1.5))
    rand_group[0].title('Artist')
    rand_group[0].subheader(idx_artist)
    rand_group[0].write('Songs: {}'.format(df[df['artist'] == idx_artist].shape[0]))
    rank_df = df['artist'].value_counts().sort_values(ascending=False).rank(method='max', ascending=False)
    rand_group[0].write('Rank: \#{}'.format(int(rank_df.loc[rank_df.index == idx_artist].item())))

    rand_group[1].title('Album')
    rand_group[1].subheader(idx_album)
    rand_group[1].write('Songs: {}'.format(df[df['album'] == idx_album].shape[0]))
    rank_df = df['album'].value_counts().sort_values(ascending=False).rank(method='max', ascending=False)
    rand_group[1].write('Rank: \#{}'.format(int(rank_df.loc[rank_df.index == idx_album].item())))
    
    rand_group[2].title('Genre')
    rand_group[2].subheader(idx_genre)
    rand_group[2].write('Songs: {}'.format(df[df['genre'] == idx_genre].shape[0]))
    rank_df = df['genre'].value_counts().sort_values(ascending=False).rank(method='max', ascending=False)
    rand_group[2].write('Rank: \#{}'.format(int(rank_df.loc[rank_df.index == idx_genre].item())))
    
    rand_group[3].title('Playlist')
    rand_group[3].subheader(idx_playlist)
    rand_group[3].write('Songs: {}'.format(df[df['playlist'] == idx_playlist].shape[0]))
    rank_df = df['playlist'].value_counts().sort_values(ascending=False).rank(method='max', ascending=False)
    rand_group[3].write('Rank: \#{}'.format(int(rank_df.loc[rank_df.index == idx_playlist].item())))

    rand_group = st.beta_columns((1.5,2,2,1.5))
    rand_group[0].title('Released')
    rand_group[0].subheader(idx_artist_date)
    rank_df = df['artist_date'].rank(ascending=True)
    rand_group[0].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))

    rand_group[1].title('Date Added')
    rand_group[1].subheader(idx_user_date)
    rank_df = df['user_date'].rank(ascending=True)
    rand_group[1].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
    
    rand_group[2].title('Time Added')
    rand_group[2].subheader(idx_user_time)
    rank_df = df['user_time'].rank(ascending=True)
    rand_group[2].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
    
    rand_group[3].title('Duration')
    rand_group[3].subheader(project_pretty_time(idx_duration))
    rank_df = df['duration'].rank(ascending=False)
    rand_group[3].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))

    # ATTR GROUP 1
    rand_group = st.beta_columns((1.5,2,2,1.5))
    rand_group[0].title('Popularity')
    rand_group[0].subheader(idx_popularity)
    rank_df = df['popularity'].rank(ascending=False)
    rand_group[0].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))

    rand_group[1].title('Danceability')
    rand_group[1].subheader(idx_danceability)
    rank_df = df['danceability'].rank(ascending=False)
    rand_group[1].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
    
    rand_group[2].title('Energy')
    rand_group[2].subheader(idx_energy)
    rank_df = df['energy'].rank(ascending=False)
    rand_group[2].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
    
    rand_group[3].title('Loudness')
    rand_group[3].subheader(idx_loudness)
    rank_df = df['loudness'].rank(ascending=True)
    rand_group[3].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))

    # ATTR GROUP 2
    rand_group = st.beta_columns((1.5,2,2,1.5))
    rand_group[0].title('Acoustic')
    rand_group[0].subheader(idx_acousticness)
    rank_df = df['acousticness'].rank(ascending=False)
    rand_group[0].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
    
    rand_group[1].title('Speechiness')
    rand_group[1].subheader(idx_speechiness)
    rank_df = df['speechiness'].rank(ascending=False)
    rand_group[1].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
    
    rand_group[2].title('Instrumental')
    rand_group[2].subheader(idx_instrumentalness)
    rank_df = df['instrumentalness'].rank(ascending=False)
    rand_group[2].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
    
    rand_group[3].title('Liveness')
    rand_group[3].subheader(idx_liveness)
    rank_df = df['liveness'].rank(ascending=True)
    rand_group[3].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))

    # ATTR GROUP 3
    rand_group = st.beta_columns((1.5,2,2,1.5))
    rand_group[0].title('Valence')
    rand_group[0].subheader(idx_valence)
    rank_df = df['valence'].rank(ascending=False)
    rand_group[0].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))

    rand_group[1].title('Explicit')
    rand_group[1].subheader(idx_explicit)
    rank_df = df['explicit'].rank(ascending=False)
    rand_group[1].write('Rank: \#{}'.format(int(rank_df.iloc[idx,])))
def project_artist_page(df):
    
    st.title('Artists by Song Count')
    cols_group = st.beta_columns((1,1))
    with cols_group[0].beta_expander('Description'):
        st.write("""
            Here is a graph displaying how many artists released a certain number
            of songs in your playlists.
        """)
    rank_df = df['artist'].value_counts().sort_values(ascending=False)
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(rank_df)
    cols_group[1].pyplot(sns.displot(rank_df).set(xlabel='Song Count', ylabel='Number of Artists'))
    
    st.title('Artists by Genre')
    cols_group = st.beta_columns((1,1))
    with cols_group[0].beta_expander('Description'):
        st.write("""
            Here is a graph displaying how many artists released a certain number
            of songs in your playlists.
        """)
    rank_df = df['artist'].value_counts().sort_values(ascending=False)
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(rank_df)
    cols_group[1].pyplot(sns.displot(rank_df).set(xlabel='Song Count', ylabel='Number of Artists'))
def project_albums_page():
    return None
def project_genres_page():
    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Top Genres and Attribute Distributions')
    cols_group[0].write('Here is a pie chart detailing your top genres of the playlist you selected.')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pd(f_data).drop(columns='value'))
    cols_group[1].pyplot(proj_plot.proj_plot_nestpie(f_data, 'genre'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Genres by Date Released')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_genre(f_data, 'artist_date'))
    cols_group[1].pyplot(proj_plot.proj_plot_hist(f_data, 'genre'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Genres by Date Added')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_genre(f_data, 'user_date'))
    cols_group[1].pyplot(proj_plot.proj_plot_hist(f_data, 'user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Popularity by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'popularity'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'popularity', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'popularity'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'popularity'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Danceability by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'danceability'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'danceability', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'danceability'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'danceability'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Energy by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'energy'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'energy', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'energy'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'energy'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Loudness by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'loudness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'loudness', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'loudness'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'loudness'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Speechiness by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'speechiness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'speechiness', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'speechiness'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'speechiness'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Acousticness by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'acousticness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'acousticness', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'acousticness'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'acousticness'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Instrumentalness by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'instrumentalness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'instrumentalness', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'instrumentalness'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'instrumentalness'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Liveness by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'liveness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'liveness', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'liveness'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'liveness'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Valence by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'valence'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'valence', 'genre'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'valence'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'valence'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Tempo by Genre')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_sums(f_data, 'tempo'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'tempo', 'genre'))
    cols_group[1].subheader('Annual Percent Changes')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_genre_pctchange(f_data, 'tempo'))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'tempo'))
def project_trends_page():
    
    st.header('Listening Trends Over Time')
    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Song Count by Release Date')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_decade_statistics(f_data))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'artist_date'))
    cols_group[1].subheader('Song Duration by Release Date')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_song_decades(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_hist(f_data, 'duration', 'decade'))

    st.header('Attribute Trends Over Time')
    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Attribute Trends Over Time')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, col=None))
    cols_group[0].pyplot(proj_plot.proj_plot_attribute(f_data, 'mean'))
    cols_group[1].subheader('Attribute Trends Annual Percent Changes')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Popularity: Today\'s hits or yesterday\'s classics?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'popularity'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'popularity', 'decade'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, method='pct_change', col='popularity', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Danceability: Does my music reflect my age?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'danceability'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'danceability', 'decade'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'danceability', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Energy: Intense or passive?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'energy'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'energy', 'decade'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'energy', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Loudness: More or less volume?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'loudness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'loudness', 'decade'))
    cols_group[1].subheader('Annual Percent Change')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'loudness', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Speechiness: Spoken words or ambient tracks?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'speechiness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'speechiness', 'decade'))
    cols_group[1].subheader('Annual Percent Changes')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'speechiness', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Acousticness: Ambient or nah?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'acousticness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'acousticness', 'decade'))
    cols_group[1].subheader('Annual Percent Changes')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'acousticness', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Instrumentalness: More or less vocals?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'instrumentalness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'instrumentalness', 'decade'))
    cols_group[1].subheader('Annual Percent Changes')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'instrumentalness', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Liveness: Audience or isolation?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'liveness'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'liveness', 'decade'))
    cols_group[1].subheader('Annual Percent Changes')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'liveness', hue='user_date'))

    cols_group = st.beta_columns((1,1))
    cols_group[0].subheader('Valence: Positivity or negativity?')
    with cols_group[0].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_trends(f_data, 'valence'))
    cols_group[0].pyplot(proj_plot.proj_plot_hist(f_data, 'valence', 'decade'))
    cols_group[1].subheader('Annual Percent Changes')
    with cols_group[1].beta_expander('DataFrame'):
        st.dataframe(proj_analysis.analysis_attribute_pctchange(f_data))
    cols_group[1].pyplot(proj_plot.proj_plot_attribute(f_data, 'pct_change', 'valence', hue='user_date'))
def project_spuser_page():
    titl00  = st.header('Your Spotify History...')
    desc00  = st.markdown(
        """
        This is how you utilize Spotify. This is how you utilize Spotify. This is how you utilize Spotify. This is how you utilize Spotify.
        This is how you utilize Spotify. This is how you utilize Spotify. This is how you utilize Spotify.

        This is how you utilize Spotify. This is how you utilize Spotify. This is how you utilize Spotify. This is how you utilize Spotify. 
        """)
    cols00a = st.beta_columns((4,6))
    desc00a = cols00a[0].subheader('Addition by Year')
    data00a = cols00a[0].dataframe(proj_analysis.analysis_cat_df(f_data))
    plot00a = cols00a[1].pyplot(proj_plot.proj_plot_factor(f_data))

    cols00b = st.beta_columns((4,6))
    desc00b = cols00b[0].subheader('Addition by Hour of Day')
    data00b = cols00b[0].dataframe(proj_analysis.analysis_user_trends2(f_data))
    plot00b = cols00b[1].pyplot(proj_plot.plot_user_datetime(f_data))
    return titl00, desc00, cols00a, desc00a, data00a, plot00a, cols00b, desc00b, data00b, plot00b
def project_correl_page(df):
    #descrition
    st.title('Correlation Page')
    st.markdown('''
        Welcome to the "Correlation Page", a page where you can explore which musical attributes relate
        and by how much they relate, if at all. There are two main plots, the correlation plot and the
        pair plot. Descriptions can be found in their respective portions of the page.

        If you are not familiar with correlations, correlations are defined as: "a statistical measure that
        expresses the extent to which two variables are linearly related." Essentially, how strong is the
        relationship between two variables and to what extent is the positivity or negativity of that relationship.
        
        Values closer to +1 are strongly positive correlated, meaning both variables increase together in linear fashion.
        Values closer to -1 are strongly negatively correlated, meaning both variables decrease together in linear fashion.
        Values closer to 0 are not correlated, meaning the change in one variable cannot explain the change in the other variable.
    ''')
    
    #data ETL-L
    corr_df = df[df['genre'] != 'NA'].groupby('genre').filter(lambda x : len(x) > 10).reset_index(drop=True).copy()
    prpt_df = df[df['genre'] != 'NA'].groupby('genre').filter(lambda x : len(x) > 10).reset_index(drop=True).copy()
    prpt_cols = ['popularity', 'danceability', 'energy', 'loudness',
                    'acousticness', 'genre']
    corr_cols = prpt_cols + ['duration', 'speechiness', 'instrumentalness', 'liveness', 'valence']
    for column in corr_cols:
        if column not in ['popularity', 'loudness', 'genre', 'duration']:
            try:
                prpt_df[column] = prpt_df[column].multiply(100).round(2)
                corr_df[column] = corr_df[column].multiply(100).round(2)
            except:
                pass
        if column == 'loudness':
            prpt_df[column] = prpt_df[column].multiply(-(100/60)).round(2)
            corr_df[column] = corr_df[column].multiply(-(100/60)).round(2)
    
    # correlation graph
    cols_group = st.beta_columns((3,7))
    cols_group[0].title('Plot 01: Correlation Plot')
    cols_group[0].write('Here is my description. dawg.')
    sns.set_theme(style="white")
    d = corr_df[corr_cols]
    corr = d.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    f, ax = plt.subplots()
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    ax = sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})
    cols_group[1].pyplot(f)

    # pairplot graph
    cols_group = st.beta_columns((3,7))
    cols_group[0].title('Plot 02: Pair Plot')
    cols_group[0].write('Here is my description. dawg.')
    fig = sns.pairplot(data=prpt_df[prpt_cols], hue='genre', palette='turbo', diag_kind='kde').set(xlim=(0,100), ylim=(0,100))
    cols_group[1].pyplot(fig)
def project_recomm_page(df, client_id, client_secret):
    auth_manager = SpotifyClientCredentials(client_id = client_id,
                                            client_secret = client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    st.title('Randomly Generated Recommendations')
    
    idx = random.randint(0,df.shape[0])
    st.write('index: {}'.format(idx))
    st.write('title: {}'.format(df.loc[idx,'title']))
    
    st.title('Create Your Own Recommendations')

    df['danceability'] = (df['danceability']* 100).round(2)
    df['energy'] = (df['energy']* 100).round(2)
    df['loudness'] = (df['loudness']* 100).round(2)
    df['speechiness'] = (df['speechiness']* 100).round(2)
    df['acousticness'] = (df['acousticness']* 100).round(2)
    df['instrumentalness'] = (df['instrumentalness']* 100).round(2)
    df['liveness'] = (df['liveness']* 100).round(2)
    df['valence'] = (df['valence']* 100).round(2)
    df['loudness'] = (df['loudness'] * (-1/60)).round(2)
    
    st.subheader('Communal')
    slid_group = st.beta_columns((1,0.05,1))
    slid_group[0].write('Control communal variables that are determined by the listening of users worldwide.')
    popu_slid = slid_group[2].slider(label='Popularity', min_value=0, max_value=100, step=1, value=(int(df['popularity'].mean()) - 3, int(df['popularity'].mean()) + 3))
    st.subheader('Mood')
    slid_group = st.beta_columns((1,0.05,1))
    slid_group[0].write('Control variables that dictate the mood(s) you experience listening to a song.')
    danc_slid = slid_group[2].slider(label='Danceability', min_value=0, max_value=100, step=1, value=(int(df['danceability'].mean()) - 3, int(df['danceability'].mean()) + 3))
    slid_group = st.beta_columns((1,0.05,1))
    ener_slid = slid_group[0].slider(label='Energy', min_value=0, max_value=100, step=1, value=(int(df['energy'].mean()) - 3, int(df['energy'].mean()) + 3))
    vale_slid = slid_group[2].slider(label='Valence', min_value=0, max_value=100, step=1, value=(int(df['valence'].mean()) - 3, int(df['valence'].mean()) + 3))
    st.subheader('Properties')
    slid_group = st.beta_columns((1,0.05,1))
    slid_group[0].write('Control variables inherent to any piece of music that artists optimize throughout their songs.')
    inst_slid = slid_group[2].slider(label='Instrumentalness', min_value=0, max_value=100, step=1, value=(int(df['instrumentalness'].mean()) - 3, int(df['instrumentalness'].mean()) + 3))
    slid_group = st.beta_columns((1,0.05,1))
    loud_slid = slid_group[0].slider(label='Loudness', min_value=0, max_value=100, step=1, value=(int(df['loudness'].mean()) - 3, int(df['loudness'].mean()) + 3))
    tempo_slid = slid_group[2].slider(label='Tempo', min_value=int(df[df['tempo'] > 0]['tempo'].min()) - 1, max_value=int(df['tempo'].max()) + 1, step=1, value=(int(df['tempo'].mean()) - 3, int(df['tempo'].mean()) + 3))
    st.subheader('Context')
    slid_group = st.beta_columns((1,0.15,1))
    slid_group[0].write('Control variables reliant on the atmosphere surrounding the artists performing the music you are listening to.')
    acou_slid = slid_group[2].slider(label='Acousticness', min_value=0, max_value=100, step=1, value=(int(df['acousticness'].mean()) - 3, int(df['acousticness'].mean()) + 3))
    slid_group = st.beta_columns((1,0.05,1))
    live_slid = slid_group[0].slider(label='Liveness', min_value=0, max_value=100, step=1, value=(int(df['liveness'].mean()) - 3, int(df['liveness'].mean()) + 3))
    spee_slid = slid_group[2].slider(label='Speechiness', min_value=0, max_value=100, step=1, value=(int(df['speechiness'].mean()) - 2, int(df['speechiness'].mean()) + 2))
    st.subheader('Personal')
    st.slider(label='Number of Results', min_value=1, max_value=100, step=1, value=20)

    if st.button('Gather Recommendations', key='gather'):
        st.write('YESSIR')
    
def project_search_page():
    return None

# PAGE CONTAINER
if ready_button:

    #try:
        
    data = retrieve_dataframe()
    f_data = alter_dataframe(data)

    if not f_data.empty:
            
            #try:
                
        if len(radio_page) == 0: st.error('Please select analysis dashboard(s) in "Select Data" sidebar')
        if (len(radio_page) > 0) & (radio_page != ['Random Statistics']): project_quick_stats()
        if 'Tracks' in radio_page: project_tracks_page(f_data)
        if 'Random Statistics' in radio_page: project_randm_page(f_data)
        if 'Artists' in radio_page: project_artist_page(f_data)
        if 'Albums' in radio_page: project_albums_page()
        if 'Genre Breakdown' in radio_page: project_genres_page()
        if 'Listening Trends' in radio_page: project_trends_page()
        if 'Attribute Correlations' in radio_page: project_correl_page(f_data)
        if 'Spotify Usage' in radio_page: project_spuser_page()
        if 'Recommendations [Beta]' in radio_page: project_recomm_page(f_data, client_id, client_secret)
                    
            # except:
            #     st.error('Cannot generate dashboard for requested view.')

    # except:
    #     st.error('Please select dashboard view in the "Select Data" sidebar tab.')

with st.sidebar.beta_expander('Resources', False):
        st.write("[GitHub Documentation](https://github.com/lucas-nelson-uiuc/academia_epidemia/tree/main/spotipy_analysis)")
        st.write("[Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)")
        st.write("[Stats for Spotify](https://www.statsforspotify.com/)")

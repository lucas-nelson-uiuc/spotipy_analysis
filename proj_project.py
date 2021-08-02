import proj_pipeline
import proj_analysis
import proj_plot

import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots   
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageFilter
from PIL.ImageFilter import (
   BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE,
   EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN
)
import requests

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy.oauth2 as oauth2

# THEME SETTINGS
st.set_page_config(page_title='Spotify Analysis Dashboard',
                    page_icon=Image.open('logo.png'),
                    layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

# TITLE SECTION
st.sidebar.title('Spotify Analysis Dashboard')

# GATHER INPUT DATA
with st.sidebar.beta_expander('Enter Input Data', True):
        client_id = st.text_input('Client ID', '2da713ea3fa74b69b02a4e57dd719de1')
        client_secret = st.text_input('Client secret', 'e46a2c2fecca41d99fbca809f191c71a')
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
                radio_page = st.selectbox(label='Select at least one', options=['Brief History', 'Tracks', 'Artists + Albums', 'Genre Breakdown', 'Listening Trends', 'Spotify Usage', 'Attribute Correlations', 'Random Statistics', 'Recommendations [Beta]'])
                submit = st.checkbox(label='Filter')
                
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
                radio_page = st.selectbox(label='Select at least one', options=['Brief History', 'Tracks', 'Artists + Albums', 'Genre Breakdown', 'Listening Trends', 'Spotify Usage', 'Attribute Correlations', 'Random Statistics', 'Recommendations [Beta]'])
                submit = st.checkbox(label='Search')

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
def project_histry_page(df):
    st.title('Spotify Activity Over Time')
    with st.beta_expander('Description...'):
        st.write('enter description here...')
    year = st.selectbox('Year', options=['All Years'] + sorted(df['user_date'].astype(str).str[:4].unique()), key='13:36_0802')
    px_df = df.copy()
    px_df = px_df[['user_date', 'artist_date', 'title', 'artist', 'album']]
    px_df['user_date'] = px_df['user_date'].astype(str).str[:4].astype(int)
    px_df = px_df.groupby('user_date').agg({
        'title' : lambda x : x.nunique(),
        'artist' : lambda x : x.nunique(),
        'album' : lambda x : x.nunique(),
    })
    fig = go.Figure(data=
        [go.Bar(name=px_df.columns[i].title(), x=list(px_df.index), y=px_df[px_df.columns[i]], text=px_df[px_df.columns[i]], textposition='auto') for i in range(len(px_df.columns))]
    )
    st.plotly_chart(fig, use_container_width=True)

    px_df = df.copy()
    px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
    px_df['user_mnth'] = px_df['user_date'].astype(str).str[5:7].astype(int)
    if year != 'All Years':
        sng_df = px_df[px_df['user_date'].astype(str).str[:4] == year].groupby('user_mnth').agg({'title':'nunique'})
        art_df = px_df[px_df['user_date'].astype(str).str[:4] == year].groupby('user_mnth').agg({'artist':'nunique'})
        alb_df = px_df[px_df['user_date'].astype(str).str[:4] == year].groupby('user_mnth').agg({'album':'nunique'})
    else:
        sng_df = px_df.groupby('user_mnth').agg({'title':'nunique'})
        art_df = px_df.groupby('user_mnth').agg({'artist':'nunique'})
        alb_df = px_df.groupby('user_mnth').agg({'album':'nunique'})
    yr_df = pd.DataFrame(data=[[df.loc[i].item() if i in list(df.index) else 0 for i in range(1,13)] for df in [sng_df, art_df, alb_df]],
                    index=['Titles', 'Artists', 'Albums'])
    yr_df = yr_df.rename(columns={
        0:'January', 1:'February', 2:'March', 3:'April', 4:'May', 5:'June',
        6:'July', 7:'August', 8:'September', 9:'October', 10:'November', 11:'December'
    })
    yr_df = yr_df.transpose().cumsum()

    test_df = pd.DataFrame({
        'month':['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] * 3,
        'type':['song'] * 12 + ['artist'] * 12 + ['album'] * 12,
        'value':[yr_df.iloc[i][col] for col in list(yr_df.columns) for i in range(12)]
    })
    fig = px.bar(test_df, x="value", y="month",
                text='value',
                color="type", orientation='h')
    st.plotly_chart(fig, use_container_width=True)
    ##############################################
    st.title('Taste of Music Over Time')
    with st.beta_expander('Description'):
        st.write('explanation goes here i think...')
    options_cols = st.beta_columns((1,1))
    year = options_cols[0].selectbox('Year', options=['All Years'] + sorted(df['user_date'].astype(str).str[:4].unique()), key='15:41_0802')
    by = options_cols[1].radio('Group', options=['Artist', 'Genre'])
    px_df = df[df['genre'] != 'NA'].copy()
    if year != 'All Years':
        px_df = px_df[px_df['user_date'].astype(str).str[:4] == year]
    if by == 'Artist':
        key = 'artist'
        tt_artist = px_df.groupby('artist').size().sort_values(ascending=False)[:10].index
        tt_filter = sorted(tt_artist)
        df_art = px_df[px_df['artist'].isin(tt_filter)]
        polar_df = df_art.groupby('artist')[['popularity', 'danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness', 'valence']].agg('mean')
    if by =='Genre':
        key = 'genre'
        tt_genre = px_df.groupby('genre').size().sort_values(ascending=False)[:10].index
        tt_filter = sorted(tt_genre)
        df_gnr = px_df[px_df['genre'].isin(tt_filter)]
        polar_df = df_gnr.groupby('genre')[['popularity', 'danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness', 'valence']].agg('mean')
    for col in polar_df.columns:
        if col not in ['popularity', 'loudness', 'artist']:
            polar_df[col] = polar_df[col].multiply(100)
        if col == 'loudness':
            polar_df[col] = polar_df[col].multiply(-(100/60))
    polar_df = pd.melt(polar_df)
    polar_df[key] = list(tt_filter) * 8

    fig = px.line_polar(polar_df, r="value", theta="variable", color=key, line_close=True,
                    color_discrete_sequence=px.colors.sequential.Magenta,
                    template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)
def project_tracks_page(df):
    
    # data transformations
    for col in df.columns:
        if col in ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence']:
            df[col] = df[col].multiply(100).round(2)
        if col == 'loudness':
            df[col] = df[col].multiply(-(100/60)).round(2)
    
    # locating and creating instances for specific categories
    attributes = ['duration', 'duration', 'artist_date', 'artist_date', 'user_date', 'user_date', 'user_time', 'user_time']
    categories = ['Longest Track', 'Shortest Track', 'Newest Track', 'Oldest Track', 'Added Most Recently', 'Added Least Recently',
                    'Added Latest in Day', 'Added Earliest in Day']
    
    for i, cat, attr in zip(range(8), categories, attributes):
        if i % 4 == 0:
            cols_group = st.beta_columns((1,1,1,1))
        if i % 2 == 0:
            if attr == 'duration':
                cols_group[i % 4].title('{}'.format(project_pretty_time(df.loc[df['duration'].argmax(), 'duration'])))
                cols_group[i % 4].image('{}'.format(df.loc[df['duration'].argmax(), 'img_url']))
                cols_group[i % 4].subheader('Longest Track')
                cols_group[i % 4].write('{}'.format(df.loc[df['duration'].argmax(), 'title']))
            else:
                cols_group[i % 4].title('{}'.format(df[df[attr] == max(df[attr])][attr].iloc[0,]))
                cols_group[i % 4].image('{}'.format(df[df[attr] == max(df[attr])]['img_url'].iloc[0,]))
                cols_group[i % 4].subheader(cat)
                cols_group[i % 4].write('{}'.format(df[df[attr] == max(df[attr])]['title'].iloc[0,]))
        if i % 2 != 0:
            if attr == 'duration':
                cols_group[i % 4].title('{}'.format(project_pretty_time(df.loc[df['duration'].argmin(), 'duration'])))
                cols_group[i % 4].image('{}'.format(df.loc[df['duration'].argmin(), 'img_url']))
                cols_group[i % 4].subheader('Shortest Track')
                cols_group[i % 4].write('{}'.format(df.loc[df['duration'].argmin(), 'title']))
            else:
                cols_group[i % 4].title('{}'.format(df[df[attr] == min(df[attr])][attr].iloc[0,]))
                cols_group[i % 4].image('{}'.format(df[df[attr] == min(df[attr])]['img_url'].iloc[0,]))
                cols_group[i % 4].subheader(cat)
                cols_group[i % 4].write('{}'.format(df[df[attr] == min(df[attr])]['title'].iloc[0,]))
    
    # locating and creating instances for highest/lowest attribute score
    attributes = ['popularity', 'danceability', 'energy', 'loudness', 'instrumentalness', 'acousticness', 'liveness', 'valence', 'tempo']
    descriptions = [
        '''The popularity of a track is a value between 0 and 100, with 100 being the most popular.
        The popularity is calculated by algorithm and is based, in the most part, on the total
        number of plays the track has had and how recent those plays are.''',
        '''Danceability describes how suitable a track is for dancing based on a
        combination of musical elements including tempo, rhythm stability, beat strength,
        and overall regularity. A value of 0 is least danceable and 100 is most danceable.''',
        '''Energy is a measure from 0 to 100 and represents a perceptual measure of
        intensity and activity. Typically, energetic tracks feel fast, loud, and noisy.
        For example, death metal has high energy, while a Bach prelude scores low on the 
        scale. Perceptual features contributing to this attribute include dynamic range,
        perceived loudness, timbre, onset rate, and general entropy.''',
        '''Overall loudness of a track in adjusted decibels (dB * -100/60). Loudness values
        are averaged across the entire track and are useful for comparing relative loudness
        of tracks. Loudness is the quality of a sound that is the primary psychological 
        correlate of physical strength (amplitude).''',
        '''Predicts whether a track contains no vocals. Rap or spoken word tracks are clearly “vocal”.
        The closer the instrumentalness value is to 100, the greater likelihood the track contains
        no vocal content. Values above 50 are intended to represent instrumental tracks,
        but confidence is higher as the value approaches 100.''',
        '''Confidence measure from 0 to 100 of whether the track is acoustic.
        100 represents high confidence the track is acoustic.
        0 represents low confidence the track is not acoustic.''',
        '''Detects the presence of an audience in the recording. Higher liveness values
        represent an increased probability that the track was performed live.''',
        '''Measure from 0 to 100 describing the musical positiveness conveyed by a track.
        Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while
        tracks with low valence sound more negative (e.g. sad, depressed, angry).''',
        '''Overall estimated tempo of a track in beats per minute (BPM). In musical terminology,
        tempo is the speed or pace of a given piece and derives directly from the average beat
        duration.''',
        '''The overall estimated tempo of a track in beats per minute (BPM). In musical terminology,
        tempo is the speed or pace of a given piece and derives directly from the average beat duration.'''
    ]
    for attr, desc in zip(attributes, descriptions):
        if attr != 'tempo':
            x_axis_range = [0, 100]
        else:
            x_axis_range = (df[df['tempo'] > 0]['tempo'].min(), df['tempo'].max())
        attr_group = st.beta_columns((2,1,1))
        # attribute desription and tabs (expanders)
        attr_group[0].title(attr.title())
        with attr_group[0].beta_expander('How does Spotify determine...'):
            st.write(desc)
        with attr_group[0].beta_expander('{} rankings...'.format(attr.title())):
            rank_df = pd.DataFrame(df[['title', 'artist', attr]].set_index(['title', 'artist'])[attr].sort_values(ascending=False).rank(method='max', ascending=False)).rename(columns={attr:'rank'})
            vals_df = df[['title', 'artist', attr]].set_index(['title', 'artist'])[attr].sort_values(ascending=False)
            rank_df['value'] = vals_df.values
            rank_df['rank'] = rank_df['rank'].astype(int)
            st.dataframe(rank_df)
        with attr_group[0].beta_expander('{} distribution...'.format(attr.title())):
            fig = px.histogram(df[attr])
            fig.update_xaxes(range=x_axis_range)
            st.plotly_chart(fig, use_container_width=True)
        # "best" (highest) attribute score track
        attr_group[1].title('{}'.format(df.loc[df[attr].argmax(), attr]))
        attr_group[1].image('{}'.format(df.loc[df[attr].argmax(), 'img_url']))
        attr_group[1].subheader('Highest {}'.format(attr.title()))
        attr_group[1].write('{}'.format(df.loc[df[attr].argmax(), 'title']))
        # "worst" (lowest) attribute score track
        arg_df = df[df[attr] > 0].reset_index(drop=True)
        attr_group[2].title('{}'.format(arg_df.loc[arg_df[attr].argmin(), attr]))
        attr_group[2].image('{}'.format(arg_df.loc[arg_df[attr].argmin(), 'img_url']))
        attr_group[2].subheader('Lowest {}'.format(attr.title()))
        attr_group[2].write('{}'.format(arg_df.loc[arg_df[attr].argmin(), 'title']))
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
        twitter_logo = '[![this is an image link]({})](https://twitter.com/search?q={}&src=typed_query)'.format('https://i.imgur.com/XMNpp3p.png', '%20'.join(str(idx_artist + ' ' +  idx_title).split(' ')))
        facebok_logo = '[![this is an image link]({})](https://www.facebook.com/search/top?q={})'.format('https://i.imgur.com/kvkQy1h.png', '%20'.join(str(idx_artist + ' ' +  idx_title).split(' ')))
        redditt_logo = '[![this is an image link]({})](https://www.reddit.com/search/?q={})'.format('https://i.imgur.com/idnSbNj.png', '%20'.join(str(idx_artist + ' ' +  idx_title).split(' ')))
        st.title(idx_title)
        st.subheader('Explore the music...')
        st.markdown(f"""
            {spotify_logo}&nbsp&nbsp&nbsp&nbsp
            {youtube_logo}&nbsp&nbsp&nbsp&nbsp
            {wikiped_logo}&nbsp&nbsp&nbsp&nbsp
            {googlee_logo}&nbsp&nbsp&nbsp&nbsp
            {twitter_logo}&nbsp&nbsp&nbsp&nbsp
            {facebok_logo}&nbsp&nbsp&nbsp&nbsp
            {redditt_logo}
        """)

    attributes = ['artist', 'album', 'genre', 'playlist',
                    'artist_date', 'user_date', 'user_time', 'duration',
                    'popularity', 'danceability', 'energy', 'loudness',
                    'acousticness', 'instrumentalness', 'liveness', 'valence',
                    'explicit']
    idx_attributes = [idx_artist, idx_album, idx_genre, idx_playlist,
                    idx_artist_date, idx_user_date, idx_user_time, idx_duration,
                    idx_popularity, idx_danceability, idx_energy, idx_loudness,
                    idx_acousticness, idx_instrumentalness, idx_liveness, idx_valence,
                    idx_explicit]
    labels = ['Artist', 'Album', 'Genre', 'Playlist',
                'Released', 'Date Added', 'Time Added', 'Duration',
                'Popularity', 'Danceability', 'Energy', 'Loudness',
                'Acoustic', 'Instrumental', 'Liveness', 'Valence',
                'Explicitness']

    for i, attr, idx_attr, label in zip(range(len(attributes)), attributes, idx_attributes, labels):
        if i % 4 == 0:
            rand_group = st.beta_columns((1.5,2,2,1.5))
        
        # duration cell; sole use of `project_pretty_time`
        if attr == 'duration':
            rand_group[i % 4].title(label)
            rand_group[i % 4].subheader(project_pretty_time(idx_duration))
            rank_df = df[attr].rank(ascending=True)
            rand_group[i % 4].write('Rank #{}'.format(int(rank_df.iloc[idx,])))
        # first row; filtered data is strictly non-numeric
        elif attr in ['artist', 'album', 'genre', 'playlist']:
            rand_group[i % 4].title(label)
            rand_group[i % 4].subheader(idx_attr)
            rand_group[i % 4].write('Songs: {}'.format(df[df[attr] == idx_attr].shape[0]))
            rank_df = df[attr].value_counts().sort_values(ascending=False).rank(method='max', ascending=False)
            rand_group[i % 4].write('Rank #{}'.format(int(rank_df.loc[rank_df.index == idx_attr].item())))
        # sort ascending = True
        elif attr in ['liveness', 'loudness']:
            rand_group[i % 4].title(label)
            rand_group[i % 4].subheader(idx_attr)
            rank_df = df[attr].rank(ascending=True)
            rand_group[i % 4].write('Rank #{}'.format(int(rank_df.iloc[idx,])))
        # sort ascending = False
        else:
            rand_group[i % 4].title(label)
            rand_group[i % 4].subheader(idx_attr)
            rank_df = df[attr].rank(ascending=False)
            rand_group[i % 4].write('Rank #{}'.format(int(rank_df.iloc[idx,])))
def project_artist_page(df):
    st.title('Top Artists by User Date Added')
    with st.beta_expander('Description...'):
        st.write('My description will go here sometime in the future...')
    temp_df = df.copy()
    temp_df['user_date']  = temp_df['user_date'].astype(str).str[:4].astype(int)
    columns = st.beta_columns((1,1))
    yr_options = ['All Years'] + [year for year in set(temp_df['user_date'])]
    yr_slctbox = columns[0].selectbox(label='Time Interval', options=yr_options, key='time_select')
    radio = columns[1].radio(label='Parameter', options=['Song Count', 'Song Duration', 'Album Count'], key='time_radio')
    if yr_slctbox == 'All Years':
        if 'Song Count' in radio:
            pie_df = temp_df.groupby('artist').size().sort_values(ascending=False)[:10]
            values = pie_df
        if 'Song Duration' in radio:
            pie_df = temp_df.groupby('artist').agg({'duration':'sum'}).sort_values('duration', ascending=False)[:10]
            values = pie_df['duration']
        if 'Album Count' in radio:
            pie_df = temp_df.groupby('artist').agg({'album':'nunique'}).sort_values('album', ascending=False)[:10]
            values = pie_df['album']
    else:
        temp_df = temp_df[temp_df['user_date'] == yr_slctbox]
        if 'Song Count' in radio:
            pie_df = temp_df.groupby('artist').size().sort_values(ascending=False)[:10]
            values = pie_df
        if 'Song Duration' in radio:
            pie_df = temp_df.groupby('artist').agg({'duration':'sum'}).sort_values('duration', ascending=False)[:10]
            values = pie_df['duration']
        if 'Album Count' in radio:
            pie_df = temp_df.groupby('artist').agg({'album':'nunique'}).sort_values('album', ascending=False)[:10]
            values = pie_df['album']

    
    labels = list(pie_df.index)
    colors = px.colors.diverging.curl
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "bar"}]])

    fig.add_trace(
        go.Pie(
        values=values,
        labels=labels),
        row=1, col=1
    ).update_traces(hoverinfo='label', textinfo='percent', textfont_size=14,
                    marker=dict(colors=colors, line=dict(color='#000000', width=2)))

    fig.add_trace(
        go.Bar(x=labels, y=values,
            marker=dict(color=values, colorscale=px.colors.diverging.curl, reversescale=True)),
        row=1, col=2
    )

    st.plotly_chart(fig, use_container_width=True)
    ####################
    st.title('Attribute Distribution by Artist')
    with st.beta_expander('Description...'):
        st.write('Normalized values. Why?')
    attributes = ['popularity', 'danceability', 'energy', 'loudness', 'instrumentalness', 'acousticness', 'liveness', 'valence']

    temp_df = df[attributes + ['title', 'artist', 'user_date', 'duration', 'album']].copy()
    temp_df['user_date']  = temp_df['user_date'].astype(str).str[:4].astype(int)
    columns = st.beta_columns((1,1))
    yr_options = ['All Years'] + [year for year in set(temp_df['user_date'])]
    yr_slctbox = columns[0].selectbox(label='Time Interval', options=yr_options, key='keytime')
    radio = columns[1].radio(label='Parameter', options=['Song Count', 'Song Duration', 'Album Count'], key='keytime2')
    if yr_slctbox == 'All Years':
        if 'Song Count' in radio:
            tt_artist = temp_df.groupby('artist').size().sort_values(ascending=False)[:10].index
        if 'Song Duration' in radio:
            tt_artist = temp_df.groupby('artist').agg({'duration':'sum'}).sort_values('duration', ascending=False)[:10].index
        if 'Album Count' in radio:
            tt_artist = temp_df.groupby('artist').agg({'album':'nunique'}).sort_values('album', ascending=False)[:10].index
    else:
        temp_df = temp_df[temp_df['user_date'] == yr_slctbox]
        if 'Song Count' in radio:
            tt_artist = temp_df.groupby('artist').size().sort_values(ascending=False)[:10].index
        if 'Song Duration' in radio:
            tt_artist = temp_df.groupby('artist').agg({'duration':'sum'}).sort_values('duration', ascending=False)[:10].index
        if 'Album Count' in radio:
            tt_artist = temp_df.groupby('artist').agg({'album':'nunique'}).sort_values('album', ascending=False)[:10].index
    
    temp_df['loudness'] = temp_df['loudness'].multiply(-(100/60))
    for col in temp_df.columns:
        if col not in ['popularity', 'loudness', 'artist', 'title', 'user_date', 'album']:
            temp_df[col] = temp_df[col].multiply(100)

    wk_df = temp_df[temp_df['artist'].isin(tt_artist)].groupby('artist').agg({
        'title':'size',
        'popularity':'mean',
        'danceability':'mean',
        'energy':'mean',
        'loudness':'mean',
        'instrumentalness':'mean',
        'acousticness':'mean',
        'liveness':'mean',
        'valence':'mean'
    }).sort_values('title', ascending=False).drop(columns='title')

    for i in range(len(wk_df.index)):
        wk_df.iloc[i] = wk_df.iloc[i] * 100 / wk_df.iloc[i].sum()

    # top_labels = [attr.title() for attr in attributes]

    colors = px.colors.sequential.Cividis

    x_data = [list(wk_df.iloc[wk_df.shape[0] - 1 - i].values) for i in range(wk_df.shape[0])]

    y_data = tt_artist[::-1]

    fig = go.Figure()

    for i in range(0, len(x_data[0])):
        for xd, yd in zip(x_data, y_data):
            fig.add_trace(go.Bar(
                x=[xd[i]], y=[yd],
                orientation='h',
                marker=dict(
                    color=colors[i],
                    line=dict(color='rgb(248, 248, 249)', width=1)
                )
            ))

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        margin=dict(l=120, r=10, t=140, b=80),
        showlegend=False,
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        annotations.append(dict(xref='paper', yref='y',
                                x=0.14, y=yd,
                                xanchor='right',
                                text=str(yd),
                                font=dict(family='Arial', size=14,
                                        color='rgb(255,255,255)'),
                                showarrow=False, align='right'))

    fig.update_layout(annotations=annotations)

    st.plotly_chart(fig, use_container_width=True)
    ####################
    st.title('Artist Album Workshop')
    with st.beta_expander('Description...'):
        st.write('LOOK AT ALL THE FUN SHIT YOU CAN DO!!')
    
    wksp = st.beta_columns((1,2))
    filters = ['RGB Inverse', 'Blur', 'Contour', 'Detail', 'Edges', 'Enhance', 'Enhance+', 'Emboss', 'Smooth', 'Smooth+', 'Sharpen']
    #BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE,EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN
    option = wksp[0].radio(label='Operation', options=filters)
    artist = wksp[1].selectbox('Artist', options=list(sorted(df['artist'].unique())), key='it_is_1:56_dude')
    
    pict_df = df.copy()
    img_list = []
    if artist != 'None':
        art_df = pict_df[pict_df['artist'] == artist]
        if art_df['img_url'].unique().shape[0] > 1:
            album = wksp[1].selectbox('Album', options=list(art_df['album'].unique()), key='it_is_2:05_dude')
            img_url = art_df[art_df['album'] == album]['img_url'].iloc[0]
            img_list.append(img_url)
        else:
            img_url = art_df['img_url'].iloc[0]
            album = wksp[1].selectbox('Album', options=list(art_df['album'].unique()), key='it_is_2:05_dude')
            img_list.append(img_url)

    wksp = st.beta_columns((1,1,0.5))
    if option == 'RGB Inverse':
        image = Image.open(requests.get(img_list[0], stream=True).raw)
        wksp[0].subheader('Before')
        wksp[0].image(image)
        r, g, b = image.split()
        image = Image.merge("RGB", (b, g, r))
        wksp[1].subheader('After')
        wksp[1].image(image)
    if option == 'Blur':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(BLUR))
    if option == 'Contour':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(CONTOUR))
    if option == 'Detail':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(DETAIL))
    if option == 'Edges':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(FIND_EDGES))
    if option == 'Enhance':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(EDGE_ENHANCE))
    if option == 'Enhance+':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(EDGE_ENHANCE_MORE))
    if option == 'Emboss':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(EMBOSS))
    if option == 'Smooth':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(SMOOTH))
    if option == 'Smooth+':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(SMOOTH_MORE))
    if option == 'Sharpen':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before'); wksp[0].image(image)
        wksp[1].subheader('After'); wksp[1].image(image.filter(SHARPEN))
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
def project_trends_page(df):
    ##################################
    st.title('Listening Trends Over Time')
    with st.beta_expander('Description...'):
        desc_cols = st.beta_columns((1,1))
        desc_cols[0].subheader('Percent of Total Songs by User Date Added')
        desc_cols[0].write('Description of this section')
        desc_cols[1].subheader('Percent of Total Songs by Release Date')
        desc_cols[1].write('Description of this section')
        desc_cols[0].subheader('Genre Songs by User Date Added')
        desc_cols[0].write('Description of this section')
        desc_cols[1].subheader('Genre Songs by Release Date')
        desc_cols[1].write('Description of this section')
    
    option_cols = st.beta_columns((1,1))
    option_01 = option_cols[0].radio(label='Metric', options=['Total Songs', 'Percent of Total Songs'], key='tomato17:12')
    option_02 = option_cols[1].radio(label='By', options=['User Date Added', 'Release Date'], key='tomato17:13')

    px_df = df.copy()
    px_df['user_year'] = df['user_date'].astype(str).str[:4]
    px_df['user_month'] = df['user_date'].astype(str).str[5:7]
    px_df['user_yrmn'] = px_df['user_year'] + '-' + px_df['user_month']
    px_df['artist_year'] = df['artist_date'].astype(str).str[:4]
    px_df['artist_month'] = df['artist_date'].astype(str).str[5:7]
    px_df['artist_yrmn'] = px_df['artist_year'] + '-' + px_df['artist_month']

    if option_01 == 'Total Songs':
        if option_02 == 'User Date Added':
            test_df = pd.pivot(px_df.groupby(['user_yrmn', 'genre']).size().reset_index().rename(columns={0:'count'}),
                                index='user_yrmn', columns='genre', values='count').fillna(0).cumsum()
            x = list(test_df.index)
        if option_02 == 'Release Date':
            test_df = pd.pivot(px_df.groupby(['artist_yrmn', 'genre']).size().reset_index().rename(columns={0:'count'}),
                                index='artist_yrmn', columns='genre', values='count').fillna(0).cumsum()
            x = list(test_df.index)
        fig = go.Figure()
        for i, genre in enumerate(test_df.columns):
            if genre != 'NA':
                fig.add_trace(go.Scatter(x=list(test_df.index), y=test_df[genre]))
                fig.data[-1].name = genre
            fig.update_layout(legend_title='Genre')
        st.plotly_chart(fig, use_container_width=True)

    if option_01 == 'Percent of Total Songs':
        if option_02 == 'User Date Added':
            test_df = pd.pivot(px_df.groupby(['user_yrmn', 'genre']).size().reset_index().rename(columns={0:'count'}),
                                index='user_yrmn', columns="genre", values="count").fillna(0).cumsum().reset_index()
            x = test_df['user_yrmn']
        if option_02 == 'Release Date':
            test_df = pd.pivot(px_df.groupby(['artist_yrmn', 'genre']).size().reset_index().rename(columns={0:'count'}),
                                index='artist_yrmn', columns="genre", values="count").fillna(0).cumsum().reset_index()
            x = test_df['artist_yrmn']
    
        css = px.colors.sequential.Blugrn
        fig = go.Figure()

        for i in range(len(test_df.columns) - 2):
            fig.add_trace(go.Scatter(
                x=x, y=test_df[test_df.columns[i+2]],
                mode='lines',
                line=dict(width=0.5, color='{}'.format(css[i % len(css)])),
                stackgroup='one',
                groupnorm='percent',
                name=test_df.columns[2:][i]
            ))

        fig.update_layout(
            showlegend=True,
            #xaxis_type='category',
            yaxis=dict(
                type='linear',
                range=[1, 100],
                ticksuffix='%'),
            xaxis_title="Year-Month",
            yaxis_title="Percent of Total Songs (%)")

        st.plotly_chart(fig, use_container_width=True)
    ##############################################
    st.title('Attribute Trends Over Time')
    with st.beta_expander('Description...'):
        st.write('Here is a description of the grpah you are looking at.')
    
    top_ten_genre = list(df.groupby('genre').size().sort_values(ascending=False)[:10].index)
    for col in df.columns:
        if col in ['danceability', 'energy', 'instrumentalness', 'acousticness', 'liveness', 'valence']:
            df[col] = df[col].multiply(100)
        if col == 'loudness':
            df[col] = df[col].multiply(- (100 / 60))
    px_df = df[(df['genre'] != 'NA') & (df['genre'].isin(top_ten_genre))].copy()
    px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
    px_df = px_df.groupby('user_year').agg('mean').reset_index()
    agg_df = px_df.groupby('user_year').agg('mean').reset_index()
    agg_df = agg_df.set_index('user_year').pct_change().reset_index().replace({np.nan:0, np.inf:0})

    attr_cols = [
        'popularity', 'danceability', 'energy', 'loudness',
        'acousticness', 'instrumentalness', 'liveness', 'valence'
    ]
    fig = px.line(px_df, x='user_year', y=attr_cols,
                labels=dict(user_date="User Year", value="Score", variable="Attribute")
                )

    for col in attr_cols:
        fig.add_bar(x=px_df['user_year'], y=px_df[attr_cols].pct_change().replace({np.nan:0, np.inf:1}).multiply(100)[col], name=col[:4]+'% change',)

    
    fig.update_layout(
        showlegend=True,
        yaxis=dict(
            range=[-50, 100]),
        xaxis_title="Year",
        yaxis_title="Value")
    st.plotly_chart(fig, use_container_width=True)
    ###############################################
    st.title('Attribute Trends Over Time by Genre')
    with st.beta_expander('Description...'):
        st.write('Here is a description of the grpah you are looking at.')
    cols_group = st.beta_columns((3,7))
    radio = cols_group[0].radio(label='Dimensions', options=['2D', '3D'], key='tomato1')
    if '2D' in radio:
        px_df = df[(df['genre'] != 'NA') & (df['genre'].isin(top_ten_genre))].copy()
        attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                'Acousticness', 'Liveness', 'Valence']
        x = cols_group[0].selectbox(label='Attribute 01',
                                    options = attributes,
                                    key='tomato2')
        y = cols_group[0].selectbox(label='Attribute 02',
                                    options = attributes,
                                    key='tomato3')
        fig = px.scatter(px_df, x=x.lower(), y=y.lower(), color='genre')
        cols_group[1].plotly_chart(fig)
    
    if '3D' in radio:
        attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                'Acousticness', 'Liveness', 'Valence']
        x = cols_group[0].selectbox(label='Attribute 01',
                                    options = attributes,
                                    key='tomato4')
        y = cols_group[0].selectbox(label='Attribute 02',
                                    options = attributes,
                                    key='tomato5')
        px_df = df[(df['genre'] != 'NA') & (df['genre'].isin(top_ten_genre))].copy()
        px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
        px_df['user_month'] = px_df['user_date'].astype(str).str[5:7].astype(int)
        px_df['user_day'] = px_df['user_date'].astype(str).str[-2:].astype(int)
        px_df['user_ym'] = px_df['user_year'] + (px_df['user_month'] / 12) + (px_df['user_day'] / 365)
        fig = px.scatter_3d(px_df, x=x.lower(), y=y.lower(), z='user_ym', color='genre')
        cols_group[1].plotly_chart(fig)
    ################################################
    st.title('Attribute Trends Over Time by User Date Added')
    with st.beta_expander('Description...'):
        st.write('Here is a description of the graph you are looking at.')
    cols_group = st.beta_columns((3,7))
    radio = cols_group[0].radio(label='Dimensions', options=['2D', '3D'], key='tomato6')
    if '2D' in radio:
        px_df = df.copy()
        px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
        attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                'Acousticness', 'Liveness', 'Valence']
        x = cols_group[0].selectbox(label='Attribute 01',
                                    options = attributes,
                                    key='tomato7')
        y = cols_group[0].selectbox(label='Attribute 02',
                                    options = attributes,
                                    key='tomato8')
        fig = px.scatter(px_df, x=x.lower(), y=y.lower(), color='user_year')
        cols_group[1].plotly_chart(fig)
    
    if '3D' in radio:
        attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                'Acousticness', 'Liveness', 'Valence']
        x = cols_group[0].selectbox(label='Attribute 01',
                                    options = attributes,
                                    key='tomato9')
        y = cols_group[0].selectbox(label='Attribute 02',
                                    options = attributes,
                                    key='tomato10')
        px_df = df[(df['genre'] != 'NA') & (df['genre'].isin(top_ten_genre))].copy()
        px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
        px_df['user_month'] = px_df['user_date'].astype(str).str[5:7].astype(int)
        px_df['user_day'] = px_df['user_date'].astype(str).str[-2:].astype(int)
        px_df['user_ym'] = px_df['user_year'] + (px_df['user_month'] / 12) + (px_df['user_day'] / 365)
        fig = px.scatter_3d(px_df, x=x.lower(), y=y.lower(), z='user_ym', color='user_ym')
        cols_group[1].plotly_chart(fig)
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
    #data ETL-L
    corr_df = df[df['genre'] != 'NA'].groupby('genre').filter(lambda x : len(x) > 10).reset_index(drop=True).copy()
    prpt_df = df[df['genre'] != 'NA'].groupby('genre').filter(lambda x : len(x) > 10).reset_index(drop=True).copy()
    prpt_cols = ['popularity', 'danceability', 'energy', 'loudness', 'acousticness', 'genre']
    corr_cols = prpt_cols + ['duration', 'instrumentalness', 'liveness', 'valence']
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
    topten_genre = list(df[df['genre'] != 'NA'].groupby('genre').size().sort_values(ascending=False)[:10].index)
    scat_df = df[df['genre'].isin(topten_genre)]
    scat_cols = ['popularity', 'danceability', 'energy', 'loudness', 'acousticness']
    
    fig = px.scatter_matrix(scat_df, dimensions=scat_cols,
                    color='genre', color_discrete_sequence=px.colors.sequential.RdBu)
    
    cols_group[1].plotly_chart(fig, use_container_width=True)
    # fig = sns.pairplot(data=prpt_df[prpt_cols], hue='genre', palette='turbo', diag_kind='kde').set(xlim=(0,100), ylim=(0,100))
    # cols_group[1].pyplot(fig)

    cols_group = st.beta_columns((3,7))
    cols_group[0].title('Plot 03a: Attributes Over Time')
    cols_group[0].write('Here is my description. dawg.')
    min_year = df['user_date'].astype(str).str[:4].astype(int).min()
    max_year = df['user_date'].astype(str).str[:4].astype(int).max()
    group_labels = [str(year) for year in range(min_year, max_year + 1)]

    heat_data = []
    for year in range(min_year, max_year + 1):
        loop_df = df[df['user_date'].astype(str).str[:4].astype(int) == year]
        pop_avg = loop_df['popularity'].mean().round(2)
        dnc_avg = loop_df['danceability'].multiply(100).mean().round(2)
        nrg_avg = loop_df['energy'].multiply(100).mean().round(2)
        lud_avg = loop_df['loudness'].multiply(-(100/60)).mean().round(2)
        acs_avg = loop_df['acousticness'].multiply(100).mean().round(2)
        ins_avg = loop_df['instrumentalness'].multiply(100).mean().round(2)
        liv_avg = loop_df['liveness'].multiply(100).mean().round(2)
        val_avg = loop_df['valence'].multiply(100).mean().round(2)
        heat_data.append([pop_avg, dnc_avg, nrg_avg, lud_avg, acs_avg, ins_avg, liv_avg, val_avg])
        
    fig = px.imshow(heat_data,
                    labels=dict(x='Attribute', y='User Year', color='Score'),
                    x=['Popularity', 'Danceability', 'Energy', 'Loudness',
                    'Acousticness', 'Instrumentalness',
                    'Liveness', 'Valence'],
                    y=group_labels,
                    color_continuous_scale='Agsunset')
    fig.update_xaxes(side='top')
    cols_group[1].plotly_chart(fig, use_container_width=True)

    cols_group = st.beta_columns((3,7))
    cols_group[0].title('Plot 03b: Attribute Derivatives')
    cols_group[0].write('Here is my description. dawg.')
    prct_data = []
    for i in range(1, len(heat_data)):
        row_data = []
        for j in range(len(heat_data[i])):
            row_data.append(((heat_data[i][j] - heat_data[i-1][j]) / heat_data[i-1][j]) * 100)
        prct_data.append(row_data)

    fig = px.imshow(prct_data,
                    labels=dict(x='Attribute', y='User Year', color='Score'),
                    x=['Popularity', 'Danceability', 'Energy', 'Loudness',
                    'Acousticness', 'Instrumentalness',
                    'Liveness', 'Valence'],
                    y=group_labels[1:],
                    color_continuous_scale='haline')
    fig.update_xaxes(side='top')
    cols_group[1].plotly_chart(fig, use_container_width=True)
def project_recomm_page(df, client_id, client_secret):
    
    st.title('Randomly Generated Recommendations')
    rec_cols = st.beta_columns((1,1,1,1))

    auth_manager = SpotifyClientCredentials(client_id = client_id,
                                                    client_secret = client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    rec = sp.recommendations(seed_tracks=['https://open.spotify.com/track/3duBO7LP1cbSvnXVULMrZn?si=4b1b205e12124a9c'],
                                limit=1, min_popularity=50)

    with rec_cols[0].beta_expander('Song'):
        rand_idx = np.random.randint(df.shape[0])
        
    
    with rec_cols[1].beta_expander('Artist'):
        st.write('hi')
    
    with rec_cols[2].beta_expander('Album'):
        st.write('hi')
    
    with rec_cols[3].beta_expander('Album'):
        st.write('hi')
    
    st.title('Create Your Own Recommendations')

    with st.beta_expander('How it Works...'):
        cols = st.beta_columns((1,0.05,1))
        cols[0].subheader('Parameters')
        cols[0].write('''
            Here you can tweak specific attributes to find music that falls within
            the range of the specified minimum and maximum values per parameter.

            If you do not adjust the values, recommendations will be generated within
            a +/- 10 range of your average value for the specific parameter.
            ''')
        cols[2].subheader('User Input')
        cols[2].write('''
            Here you can enter a specific track (URL), artist (URL), or genre
            (based on Spotify's list of recognized genres) to specify your recommendation
            futher.

            These parameters do not need to be from any of the playlists you have entered
            in the sidebar and will generate a list of recommended songs based on your
            desired maximum number of results.
            ''')
    
    with st.beta_expander('Customize Parameters...'):

        df['danceability'] = (df['danceability']* 100).round(2)
        df['energy'] = (df['energy']* 100).round(2)
        df['acousticness'] = (df['acousticness']* 100).round(2)
        df['instrumentalness'] = (df['instrumentalness']* 100).round(2)
        df['liveness'] = (df['liveness']* 100).round(2)
        df['valence'] = (df['valence']* 100).round(2)
        df['loudness'] = (df['loudness'] * (-1/60)).round(2)
        
        genre_options = ['None']
        for genre in sp.recommendation_genre_seeds()['genres']:
            genre_options.append(genre.title())
        
        slid_group = st.beta_columns((1,0.05,1))

        slid_group[0].subheader('Communal Statistic')
        slid_group[0].write('Control communal variables that are determined by the listening of users worldwide.')
        popu_slid = slid_group[0].slider(label='Popularity', min_value=0, max_value=100, step=1, value=(0,100))
        # slid_group[0].subheader('Mood Parameters')
        # #slid_group[0].write('Control variables that dictate the mood(s) you experience listening to a song.')
        # danc_slid = slid_group[0].slider(label='Danceability', min_value=0, max_value=100, step=1, value=(0,100))
        # ener_slid = slid_group[0].slider(label='Energy', min_value=0, max_value=100, step=1, value=(0,100))
        # vale_slid = slid_group[0].slider(label='Valence', min_value=0, max_value=100, step=1, value=(0,100))
        # slid_group[0].subheader('Musical Properties')
        #slid_group[0].write('Control variables inherent to any piece of music that artists optimize throughout their songs.')
        inst_slid = slid_group[0].slider(label='Instrumentalness', min_value=0, max_value=100, step=1, value=(0,100))
        temp_slid = slid_group[0].slider(label='Tempo', min_value=0, max_value=300, step=1, value=(0,300))
        # slid_group[0].subheader('Contextual Attributes')
        # #slid_group[0].write('Control variables reliant on the atmosphere surrounding the artists performing the music you are listening to.')
        # acou_slid = slid_group[0].slider(label='Acousticness', min_value=0, max_value=100, step=1, value=(0,100))
        # live_slid = slid_group[0].slider(label='Liveness', min_value=0, max_value=100, step=1, value=(0,100))

        slid_group[2].subheader('User Input')
        user_input = slid_group[2].radio(label='', options=['Track URL', 'Artist URL', 'Genre'])
        track_url, artist_url, genre_url = '', '', ''
        if user_input == 'Track URL':
            track_url = slid_group[2].text_input('Track URL', key='track')
        if user_input == 'Artist URL':
            artist_url = slid_group[2].text_input('Artist URL', key='artist')
        if user_input == 'Genre':
            genre_url = slid_group[2].selectbox(label='Select Genre', options=genre_options, key='genre')
        slid_group[2].subheader('Customize Results')
        limit = slid_group[2].slider(label='Maximum Number of Results', min_value=1, max_value=100, step=1, value=20)
        gather = slid_group[2].button('Gather Results')

    if gather:
        
        st.subheader('Because you listened to...')
        
        if track_url != '':
            image = sp.track(track_url)['album']['images'][0]['url']
            track_url = [track_url]
            track_name = sp.track(track_url[0])['name']
            artist_url = None
            artist_name = sp.track(track_url[0])['artists'][0]['name']
            genre_url = None
            genre_name = ''
        elif artist_url != '':
            image = sp.artist(artist_url)['images'][0]['url']
            track_url = None
            track_name = ''
            artist_url = [artist_url]
            artist_name = sp.artist(artist_url[0])['name']
            genre_url = None
            genre_name = sp.artist(artist_url[0])['genres']
        elif genre_url != 'None':
            try:
                genr_df = df[df['genre'] == genre_url].iloc[np.random.randint(df.shape[0])]
                image = sp.track(genr_df['track_url'])['album']['images'][0]['url']
                track_url = None
                track_name = ''
                artist_url = None
                artist_name = ''
                genre_url = [genre_url]
                genre_name = genre_url[0].title()
            except:
                rand_idx = np.random.randint(df.shape[0])
                image = 'https://i.imgur.com/m8vVWiu.jpg'
                track_url = None
                track_name = ''
                artist_url = None
                artist_name = ''
                genre_url = [genre_url]
                genre_name = genre_url[0].title()
        elif (track_url == '') & (artist_url == '') & (genre_url == 'None'):
            rand_idx = np.random.randint(df.shape[0])
            image = df.iloc[rand_idx]['img_url']
            track_url = [df.iloc[rand_idx]['track_url']]
            track_name = df.iloc[rand_idx]['title']
            artist_url = None
            artist_name = df.iloc[rand_idx]['artist']
            genre_url = None
            genre_name = df.iloc[rand_idx]['genre'].title()
        else:
            st.error('ummmm what')
        
        rec_cols = st.beta_columns((2,8))
        rec_cols[0].image(image)
        rec_cols[1].markdown(f'''
            Track: {track_name}

            Artist: {artist_name}

            Genre: {genre_name}
            ''')
        
        recs = sp.recommendations(seed_tracks=track_url,
                                    seed_artists=artist_url,
                                    seed_genres=genre_url,
                                    limit=limit)

        rec_lists = []
        for track in recs['tracks']:
            rec_track = track['name']
            rec_artst = track['artists'][0]['name']
            rec_trurl = track['external_urls']['spotify']
            rec_arurl = track['artists'][0]['external_urls']['spotify']
            rec_igurl = track['album']['images'][0]['url']
            rec_lists.append([rec_track, rec_artst, rec_trurl, rec_arurl, rec_igurl])
            

        st.subheader('You may also like...')
        for i, rec_data in enumerate(rec_lists):
            if i % 4 == 0:
                finaler_cols = st.beta_columns((1,1,1,1))
            finaler_cols[i % 4].image(rec_data[-1])
            finaler_cols[i % 4].subheader('{} || {}'.format(rec_data[0], rec_data[1]))
            finaler_cols[i % 4].markdown('''
                    [![this is an image link]({})]({})
                    [![this is an image link]({})](https://www.youtube.com/results?search_query={})
                    [![this is an image link]({})](https://en.wikipedia.org/wiki/{})
                    [![this is an image link]({})](https://www.google.com/search?q={})
                '''.format(
                    'https://i.imgur.com/TejSfM3.png', rec_data[2],
                    'https://i.imgur.com/LkMsDsO.png', '+'.join(str(rec_data[1] + ' ' +  rec_data[0]).split(' ')),
                    'https://i.imgur.com/UIllM9Y.png', '_'.join(rec_data[1].split(' ')),
                    'https://i.imgur.com/SbD92XG.png', '+'.join(str(rec_data[1] + ' ' +  rec_data[0]).split(' '))
                )
            )

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
        if 'Brief History' in radio_page: project_histry_page(f_data)
        if 'Tracks' in radio_page: 
            st.title('Tracks Page')
            st.markdown('''
                Welcome to the "Tracks Page", the page for anything related to the specific quirks about the
                music you listen to.
                
                From learning more about a brief history of your music to your highest
                and lowest ranking songs per attribute, this page will answer any questions you have (and
                possibly leave you asking yourself more) about how your music ranks in comparison to itself.
            ''')
            project_quick_stats(); project_tracks_page(f_data)
        if 'Artists + Albums' in radio_page:
            st.title('Artists + Albums Page')
            st.markdown('''
                Welcome to the "Artists + Albums Page", the page for anything related to the specific quirks about the
                music you listen to.
                
                From learning more about a brief history of your music to your highest
                and lowest ranking songs per attribute, this page will answer any questions you have (and
                possibly leave you asking yourself more) about how your music ranks in comparison to itself.
            ''')
            project_quick_stats(); project_artist_page(f_data)
        if 'Genre Breakdown' in radio_page: project_quick_stats(); project_genres_page()
        if 'Listening Trends' in radio_page:
            st.title('Listening Trends Page')
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
            st.write('Here is a description that I will write more of later...')
            project_quick_stats(); project_trends_page(f_data)
        if 'Spotify Usage' in radio_page: project_quick_stats(); project_spuser_page()
        if 'Attribute Correlations' in radio_page:
            st.title('Attribute Correlation Page')
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
            project_correl_page(f_data)
        if 'Random Statistics' in radio_page: project_randm_page(f_data)
        if 'Recommendations [Beta]' in radio_page: project_recomm_page(f_data, client_id, client_secret)
                    
            # except:
            #     st.error('Cannot generate dashboard for requested view.')

    # except:
    #     st.error('Please select dashboard view in the "Select Data" sidebar tab.')

with st.sidebar.beta_expander('Resources', False):
        st.write("[GitHub Documentation](https://github.com/lucas-nelson-uiuc/academia_epidemia/tree/main/spotipy_analysis)")
        st.write("[Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)")
        st.write("[Stats for Spotify](https://www.statsforspotify.com/)")

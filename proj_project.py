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
from plotly.colors import n_colors  
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
        ready_button = st.checkbox('Gather DataFrame')

# DATAFRAME FUNCTIONS
radio_page = st.empty()
def raw_dataframe():
    if client_id and client_secret and playlist_input and ready_button:
        
        user = proj_pipeline.SpotifyUser(client_id, client_secret)
        
        if len(playlist_input.split(',')) > 1:
            playlist_df = proj_pipeline.pipeline_multip_spotify(user, playlist_input)
        else:
            playlist_df = proj_pipeline.pipeline_single_spotify(user, playlist_input)
    
    return playlist_df
def retrieve_dataframe():
    return raw_dataframe().drop(columns=['inv_dt', 'imp_dt']).drop_duplicates(subset=['title', 'artist'], keep='first').reset_index(drop=True)
def alter_dataframe(df):
    if ready_button:
        with st.sidebar.beta_expander("Select Data", False):
            global radio_page
            search_filter = st.radio(label='', options=['Filter','Search'])

            if search_filter == 'Filter':
                st.subheader('Filter Parameters')
                filter_playlist = st.multiselect('Playlist', options=list(np.sort(data['playlist'].unique())))
                filter_release = st.slider('Release Date',
                                            min_value=df['artist_date'].min().year,
                                            max_value=df['artist_date'].max().year,
                                            value = (df['artist_date'].min().year, df['artist_date'].max().year),
                                            step=1)
                st.subheader('Dashboard Views')
                radio_page = st.selectbox(label='Select at least one', options=['Brief History', 'Tracks', 'Artists + Albums', 'Listening Trends', 'Random Statistics', 'Recommendations [Beta]'])
                submit = st.checkbox(label='Filter')
                
                if submit:
                    return proj_analysis.analysis_filter_dataframe(df, filter_playlist, filter_release)
            
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
                radio_page = st.selectbox(label='Select at least one', options=['Brief History', 'Tracks', 'Artists + Albums', 'Listening Trends', 'Random Statistics', 'Recommendations [Beta]'])
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
def project_welcm_page():
    with st.sidebar.beta_expander('Resources', False):
        st.write("[GitHub Documentation](https://github.com/lucas-nelson-uiuc/academia_epidemia/tree/main/spotipy_analysis)")
        st.write("[Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)")
        st.write("[Stats for Spotify](https://www.statsforspotify.com/)")

    st.markdown("<h1 style='text-align: center;'>Welcome to Spotify Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>The data hub for all your music listening...</h2>", unsafe_allow_html=True)
    img_cols = st.beta_columns((0.2,1,0.2))
    img_cols[1].image('https://images.prismic.io/soundcharts/727545d02420e55c5c6a376f633a1f02ebc59dc5_mapspot2.png?auto=compress,format')
    
    data_grp = st.beta_columns((1,1,1))
    data_grp[0].markdown("<h3><b>01. How to Access Your Data</b></h3>", unsafe_allow_html=True)
    data_grp[0].markdown('''
        Data for your dashboard is gathered by generating a Spotify token and providing playlist URLs

        Visit the [`Walkthrough Document`](https://github.com/lucas-nelson-uiuc/academia_epidemia/blob/main/spotipy_analysis/WALKTHROUGH_DOCUMENT.md#Interacting-with-Plotly-Graphs)
        to learn how to properly prepare your input data
    ''')
    
    data_grp[1].markdown("<h3><b>02. Manipulating Your Data</b></h3>", unsafe_allow_html=True)
    data_grp[1].markdown('''
        Filter to include all observations that fit your criteria or search individual attributes

        Both requests are limited to the data provided
    ''')
    
    data_grp[2].markdown("<h3><b>03. Dashboard Interaction</b></h3>", unsafe_allow_html=True)
    data_grp[2].markdown('''
        Analyze your music listening habits of the past and present

        Leverage your unique insights to develop curtailed recommendations for future listening
    ''')
def project_dataq_page(r_df):
    page_cols = st.beta_columns((6,4,4))
    page_cols[0].title('Gathered Data')
    page_cols[0].markdown('''
        This is the page to view your requested data before it is shipped off for analysis.
        You can always come back to get a second glance, or you can assume that the data gathering
        process works perfectly all the time.
        
        However, even if you are confident the request is perfect, you might be better equipped
        to learn more about your music taste by taking a brief glance at your unique dataset.
    ''')

    duration = proj_analysis.analysis_pretty_time(r_df)
    playlists = r_df['playlist'].unique().shape[0]
    titles = r_df['title'].unique().shape[0]
    artists = r_df['artist'].unique().shape[0]
    albums = r_df['album'].unique().shape[0]
    genres = r_df[r_df['genre'] != 'NA']['genre'].unique().shape[0]
    items = [duration, playlists, titles, artists, albums, genres]
    labels = ['Duration', 'Playlists', 'Songs', 'Artists', 'Albums', 'Genres']

    colors = n_colors('rgb(4,74,4)', 'rgb(96,223,96)', 6, colortype='rgb')
    page_cols[1].title(''); page_cols[2].title('')
    for i, color, item, label in zip(range(len(items)), colors, items, labels):
        if i % 2 == 0:
            page_cols[1].markdown(f'''
                <h3 style="background-color:{color};color:#ffffff;style=padding-left:20px;">&nbsp{item}</h3>
                <p style="background-color:{color};color:#ffffff;">&nbsp{label}</p>
                ''', unsafe_allow_html=True)
        if i % 2 == 1:
            page_cols[2].markdown(f'''
                <h3 style="background-color:{color};color:#ffffff;border-radius:2%;">&nbsp{item}</h3>
                <p style="background-color:{color};color:#ffffff;border-radius:2%;">&nbsp{label}</p>
                ''', unsafe_allow_html=True)
    
    page_cols = st.beta_columns((4,4,6))
    page_cols[2].title('Faulty Data')
    page_cols[2].markdown('''
        Given the limitations of Spotify's API, some inaccuracies may occur,
        most commonly incorrect or broad genre labeling, imprecise artist release dates, and
        missing data entries.
        
        `NA` entries are accounted for by either a proxy or a zero (Spotify-generated)
        whereas duplicate entries are reduced to the first instance.
    ''')

    attributes = ['popularity','danceability','energy','loudness','acousticness',
            'instrumentalness','liveness','valence']
    skipped = len(playlist_input.split(',')) - r_df['playlist'].unique().shape[0]
    un_gnr = r_df[r_df['genre'] == 'NA'].shape[0]
    na_entr = r_df[r_df[attributes] == 0].notna().sum().sum()
    dups = r_df.shape[0] - r_df.drop_duplicates(subset=['title', 'artist'], keep='first').reset_index(drop=True).shape[0]
    inv_dt = r_df['inv_dt'].sum()
    imp_dt = r_df['imp_dt'].sum()
    items = [skipped, un_gnr, na_entr, dups, inv_dt, imp_dt]
    labels = ['Skipped Playlists', 'Unlabeled Genres', 'NA Entries', 'Duplicate Entries', 'Invalid Dates', 'Imprecise Dates']

    colors = n_colors('rgb(74,4,4)', 'rgb(223,96,96)', 6, colortype='rgb')
    page_cols[0].title(''); page_cols[1].title('')
    for i, color, item, label in zip(range(len(items)), colors, items, labels):
        if i % 2 == 0:
            page_cols[0].markdown(f'''
                <h3 style="background-color:{color};color:#ffffff;style=padding-left:20px;">&nbsp{item}</h3>
                <p style="background-color:{color};color:#ffffff;">&nbsp{label}</p>
                ''', unsafe_allow_html=True)
        if i % 2 == 1:
            page_cols[1].markdown(f'''
                <h3 style="background-color:{color};color:#ffffff;border-radius:2%;">&nbsp{item}</h3>
                <p style="background-color:{color};color:#ffffff;border-radius:2%;">&nbsp{label}</p>
                ''', unsafe_allow_html=True)
    
    cols = st.beta_columns((6,4,4))
    cols[0].title('Data Fixer')
    cols[0].markdown('''
        *Coming soon...*
        
        Although the analyses attempt to mitigate these differences, now is your chance to label
        data as you see best fit.
    ''')

    items = ['Enter genre for ...', 'Enter statistic for ...', 'Enter release date for ...', 'Many more ...']
    labels = ['Indie', '83.3', '2013-05-16' , 'User input here']
    colors = n_colors('rgb(0,76,153)', 'rgb(0,128,255)', 4, colortype='rgb')
    cols[1].title(''); cols[2].title('')
    for i, color, item, label in zip(range(len(items)), colors, items, labels):
        if i % 2 == 0:
            cols[1].markdown(f'''
                <h3 style="background-color:{color};color:#ffffff;style=padding-left:20px;">&nbsp{item}</h3>
                <p style="background-color:{color};color:#ffffff;">&nbsp{label}</p>
                ''', unsafe_allow_html=True)
        if i % 2 == 1:
            cols[2].markdown(f'''
                <h3 style="background-color:{color};color:#ffffff;border-radius:2%;">&nbsp{item}</h3>
                <p style="background-color:{color};color:#ffffff;border-radius:2%;">&nbsp{label}</p>
                ''', unsafe_allow_html=True)
def project_histry_page(df):
    st.title('Spotify Activity Over Time')
    with st.beta_expander('Description...'):
        desc_cols = st.beta_columns((1,1))
        desc_cols[0].subheader('Total Songs by User Date Added')
        desc_cols[0].write('Returns graph of all songs, artists, albums, and genres that were added by the user in the provided `User Year` selectbox')
        desc_cols[1].subheader('Total Songs by Release Date')
        desc_cols[1].write('Returns graph of all songs, artists, albums, and genres that were released by all artists in the provided `User Year` selectbox')
        desc_cols[0].subheader('Percentage by User Date Added')
        desc_cols[0].write('Returns graph of all songs, artists, albums, and genres as a percentage of the sum of songs, artists, albums, and genres, respectively, as a function of the provided `User Year` selectbox')
        desc_cols[1].subheader('Percentage by Release Date')
        desc_cols[1].write('Returns graph of all songs, artists, albums, and genres as a percentage of the sum of songs, artists, albums, and genres, respectively, as a function of the provided `User Year` selectbox')
    option_cols = st.beta_columns((1,1,1,1))
    year = option_cols[0].selectbox('User Year', options=['All Years'] + sorted(df['user_date'].astype(str).str[:4].unique()), key='13:58_0804')
    if year != 'All Years':
        genre = option_cols[1].selectbox('Genre',
                                        options=['All Genres']
                                                + [attr.title() for attr in sorted(df[(df['genre'] != 'NA')
                                                                                    & (df['user_date'].astype(str).str[:4] == year)]['genre'].unique())],
                                        key='13:36_0804')
    else:
        genre = option_cols[1].selectbox('Genre',
                                        options=['All Genres']
                                                + [attr.title() for attr in sorted(df[df['genre'] != 'NA']['genre'].unique())],
                                        key='13:36_0804')
    option_01 = option_cols[2].radio(label='Metric', options=['Total', 'Percentage'], key='tomato17:12')
    option_02 = option_cols[3].radio(label='By', options=['User Date Added', 'Artist Release Date'], key='tomato17:13')
    # plot 1,colspan(2)
    if year == 'All Years':
        px_df = df.copy()
    if year != 'All Years':
        px_df = df[df['user_date'].astype(str).str[:4] == year].copy()
    if genre != 'All Genres':
        px_df = px_df[px_df['genre'] == genre.lower()]
    if option_01 == 'Total':
        y_axis_title = 'Count (#)'
    if option_01 == 'Percentage':
        y_axis_title = 'Percentage (%)'
    if option_02 == 'User Date Added':
        px_df = px_df[['user_date', 'title', 'artist', 'album', 'genre']]
        px_df['date'] = px_df['user_date'].astype(str).str[:4].astype(int)
    if option_02 == 'Artist Release Date':
        px_df = px_df[['artist_date', 'title', 'artist', 'album', 'genre']]
        px_df['date'] = px_df['artist_date'].astype(str).str[:4].astype(int)

    px_df = px_df.groupby('date').agg({
        'title' : lambda x : x.nunique(),
        'artist' : lambda x : x.nunique(),
        'album' : lambda x : x.nunique(),
        'genre' : lambda x : x.nunique()
    })

    if option_01 == 'Percentage':
        for col in px_df.columns:
            px_df[col] = px_df[col].apply(lambda x : x / px_df[col].sum() * 100).round(2)

    fig = make_subplots(rows=2, cols=1)
    for i in range(len(px_df.columns)):
        fig.add_trace(
            go.Bar(
                name=px_df.columns[i].title(),
                x=list(px_df.index),
                y=px_df[px_df.columns[i]],
                text=px_df[px_df.columns[i]],
                textposition='auto'
            ),
            row=1, col=1
        )
        fig.update_layout(
            yaxis_title=y_axis_title,
            legend_title="Legend"
        )
    # plot 2,1
    px_df = df.copy()
    px_df['user_mnth'] = px_df['user_date'].astype(str).str[5:7].astype(int)
    px_df['artist_mnth'] = px_df['artist_date'].astype(str).str[5:7].astype(int)
    if year != 'All Years':
        if option_02 == 'User Date Added':
            sng_df = px_df[px_df['user_date'].astype(str).str[:4] == year].groupby('user_mnth').agg({'title':'nunique'})
            art_df = px_df[px_df['user_date'].astype(str).str[:4] == year].groupby('user_mnth').agg({'artist':'nunique'})
            alb_df = px_df[px_df['user_date'].astype(str).str[:4] == year].groupby('user_mnth').agg({'album':'nunique'})
            gnr_df = px_df[px_df['user_date'].astype(str).str[:4] == year].groupby('user_mnth').agg({'genre':'nunique'})
        else:
            sng_df = px_df[px_df['artist_date'].astype(str).str[:4] == year].groupby('artist_mnth').agg({'title':'nunique'})
            art_df = px_df[px_df['artist_date'].astype(str).str[:4] == year].groupby('artist_mnth').agg({'artist':'nunique'})
            alb_df = px_df[px_df['artist_date'].astype(str).str[:4] == year].groupby('artist_mnth').agg({'album':'nunique'})
            gnr_df = px_df[px_df['artist_date'].astype(str).str[:4] == year].groupby('artist_mnth').agg({'genre':'nunique'})
    else:
        if option_02 == 'User Date Added':
            sng_df = px_df.groupby('user_mnth').agg({'title':'nunique'})
            art_df = px_df.groupby('user_mnth').agg({'artist':'nunique'})
            alb_df = px_df.groupby('user_mnth').agg({'album':'nunique'})
            gnr_df = px_df.groupby('user_mnth').agg({'genre':'nunique'})
        else:
            sng_df = px_df.groupby('artist_mnth').agg({'title':'nunique'})
            art_df = px_df.groupby('artist_mnth').agg({'artist':'nunique'})
            alb_df = px_df.groupby('artist_mnth').agg({'album':'nunique'})
            gnr_df = px_df.groupby('artist_mnth').agg({'genre':'nunique'})
    yr_df = pd.DataFrame(data=[[df.loc[i].item() if i in list(df.index) else 0 for i in range(1,13)] for df in [sng_df, art_df, alb_df, gnr_df]],
                    index=['Titles', 'Artists', 'Albums', 'Genres'])
    yr_df = yr_df.rename(columns={
        0:'January', 1:'February', 2:'March', 3:'April', 4:'May', 5:'June',
        6:'July', 7:'August', 8:'September', 9:'October', 10:'November', 11:'December'
    })

    if option_01 == 'Total':
        xaxis = 'Aggregate Count (#)'
        yaxis = 'Month'
        yr_df = yr_df.transpose().cumsum()
    if option_01 == 'Percentage':
        xaxis = 'Aggregate Percentage (%)'
        yaxis = 'Month'
        yr_df = yr_df.transpose()
        for column in yr_df.columns:
            yr_df[column] = yr_df[column].apply(lambda x : x / yr_df[column].sum() * 100).round(0)

    test_df = pd.DataFrame({
        'month':['Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec '] * 4,
        'type':['song'] * 12 + ['artist'] * 12 + ['album'] * 12 + ['genre'] * 12,
        'value':[yr_df.iloc[i][col] for col in list(yr_df.columns) for i in range(12)]
    })

    fig.add_trace(
        go.Bar(
            x=test_df['value'],
            y=test_df['month'],
            orientation='h',
            marker=dict(
                color=['#636EFA'] * 12 + ['#EF553B'] * 12 + ['#00CC96'] * 12 + ['#AB63FA'] * 12
            ),
            showlegend=False
        ),
        row=2, col=1
    )

    fig['layout']['xaxis2']['title']=xaxis
    fig['layout']['yaxis2']['title']=yaxis

    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    st.plotly_chart(fig, use_container_width=True)
    ##############################################
    # polar graph
    st.title('Taste of Music Over Time')
    with st.beta_expander('Description'):
        cols = st.beta_columns((1,1))
        cols[0].subheader('Attribute Distribution')
        cols[0].write('Distribution of Spotify-generated attributes over all songs added by the user in the provided `Year` range')
        cols[1].subheader('Attribute Polar Plot')
        cols[1].write('Spread of attribute scores (from 0 to 100) over all songs added by the user in the provided `Year` range and grouped by top ten artists, top ten genres, or as an average')
    options_cols = st.beta_columns((1,1))
    year = options_cols[0].selectbox('Year', options=['All Years'] + sorted(df['user_date'].astype(str).str[:4].unique()), key='15:41_0802')
    by = options_cols[1].radio('Group', options=['Artist', 'Genre', 'None'])
    px_df = df[df['genre'] != 'NA'].copy()
    if year != 'All Years':
        px_df = px_df[px_df['user_date'].astype(str).str[:4] == year]
    if by != 'None':
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
        attributes = ['popularity','danceability','energy','loudness','acousticness',
            'instrumentalness','liveness','valence']
        colors = n_colors('rgb(0,153,76)', 'rgb(153,255,204)', 10, colortype='rgb')

        fig = px.line_polar(polar_df, r="value", theta="variable", color=key, line_close=True,
                    color_discrete_sequence=colors[::-1],
                    template='plotly_dark')
    if by == 'None':
        key = ''
        tt_filter = ['Average']
        polar_df = px_df[['popularity', 'danceability', 'energy', 'loudness', 'acousticness', 'instrumentalness', 'liveness', 'valence']]
        for col in polar_df.columns:
            if col not in ['popularity', 'loudness', 'artist']:
                polar_df[col] = polar_df[col].multiply(100)
            if col == 'loudness':
                polar_df[col] = polar_df[col].multiply(-(100/60))
        
        polar_df.loc['mean'] = polar_df.mean()
        polar_df = pd.melt(polar_df)
        polar_df = polar_df.groupby('variable').agg('mean').reset_index()
        polar_df[key] = ['Average'] * 8

        fig = px.bar_polar(polar_df, r="value", theta="variable",
                    color_discrete_sequence=px.colors.sequential.PuBuGn[::-1],
                    template='plotly_dark')
    plot_cols = st.beta_columns((1,1))
    plot_cols[1].plotly_chart(fig, use_container_width=True)
    # violin plot
    attributes = ['popularity','danceability','energy','loudness','acousticness',
            'instrumentalness','liveness','valence']
    px_df = df.copy()
    if year != 'All Years':
        px_df = df[df['user_date'].astype(str).str[:4] == year].copy()
    px_df = px_df[attributes]
    for col in px_df:
        if col not in ['popularity', 'loudness']:
            px_df[col] = px_df[col].multiply(100)
        if col == 'loudness':
            px_df[col] = px_df[col].multiply(-(100/60))

    colors = n_colors('rgb(0, 102, 51)', 'rgb(5, 255, 164)', 8, colortype='rgb')

    fig = go.Figure()
    for col, color in zip(list(px_df.columns)[::-1], colors):
        fig.add_trace(go.Violin(x=px_df[col], line_color=color, name=col.title()))

    fig.update_traces(orientation='h', side='positive', width=3, points=False)
    fig.update_layout(xaxis_showgrid=True, showlegend=False)
    plot_cols[0].plotly_chart(fig, use_container_width=True)
    ########################################################
    # heat map absolute
    st.title('Change in Attribute Preferences Over Time')
    with st.beta_expander('Description'):
        cols = st.beta_columns((1,1))
        cols[0].subheader('Attribute Scores per Year')
        cols[0].write('Color coding based on attribute scores by `User Year`')
        cols[1].subheader('Attribute Derivatives')
        cols[1].write('Color coding based on percent change in the attribute scores of the previous `User Year`')
    heat_cols = st.beta_columns((1,1))
    
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
                    labels=dict(x='Attribute', y='User Year', color='Attr Score'),
                    x=['Popularity', 'Danceability', 'Energy', 'Loudness',
                    'Acousticness', 'Instrumentalness',
                    'Liveness', 'Valence'],
                    y=group_labels,
                    color_continuous_scale='Agsunset')
    fig.update_xaxes(side='top')
    heat_cols[0].plotly_chart(fig, use_container_width=True)
    # heat map derivative
    prct_data = [[0,0,0,0,0,0,0,0]]
    for i in range(1, len(heat_data)):
        row_data = []
        for j in range(len(heat_data[i])):
            row_data.append(((heat_data[i][j] - heat_data[i-1][j]) / heat_data[i-1][j]) * 100)
        prct_data.append(row_data)

    fig = px.imshow(prct_data,
                    labels=dict(x='Attribute', y='User Year', color='Pct Change'),
                    x=['Popularity', 'Danceability', 'Energy', 'Loudness',
                    'Acousticness', 'Instrumentalness',
                    'Liveness', 'Valence'],
                    y=group_labels,
                    color_continuous_scale='haline')
    fig.update_xaxes(side='top')
    heat_cols[1].plotly_chart(fig, use_container_width=True)
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
def project_artist_page(df):
    st.title('Top Artists by User Date Added')
    with st.beta_expander('Description...'):
        cols = st.beta_columns((1,1,1))
        cols[0].subheader('Song Count')
        cols[0].write('Filters the dataset to include all data from the top ten artists by song count')
        cols[1].subheader('Duration')
        cols[1].write('Filters the dataset to include all data from the top ten artists by song duration (milliseconds)')
        cols[2].subheader('Album Count')
        cols[2].write('Filters the dataset to include all data from the top ten artists by album count')
    temp_df = df.copy()
    temp_df['user_date']  = temp_df['user_date'].astype(str).str[:4].astype(int)
    columns = st.beta_columns((1,1))
    yr_options = ['All Years'] + [year for year in set(temp_df['user_date'])]
    yr_slctbox = columns[0].selectbox(label='User Year', options=yr_options, key='time_select')
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
        cols = st.beta_columns((1.5,3))
        cols[0].subheader('Parameters')
        cols[0].write('Similar filtering capabilities to previous graph.')
        cols[1].subheader('Interpretation')
        cols[1].write('''
            Assuming each artist obtained the same value for the specified parameter, this is how their attribute distributions
            would compare to one another.
            
            Although there are not labels on the x-axis denoting what the colors mean, the labels
            and their corresponding values can be found in the dataframe box just above the graph.
        ''')
    attributes = ['popularity', 'danceability', 'energy', 'loudness', 'instrumentalness', 'acousticness', 'liveness', 'valence']

    temp_df = df[attributes + ['title', 'artist', 'user_date', 'duration', 'album']].copy()
    temp_df['user_date']  = temp_df['user_date'].astype(str).str[:4].astype(int)
    columns = st.beta_columns((1,1))
    yr_options = ['All Years'] + [year for year in set(temp_df['user_date'])]
    yr_slctbox = columns[0].selectbox(label='User Year', options=yr_options, key='keytime')
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

    with st.beta_expander('DataFrame'):
        st.dataframe(wk_df)

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
        st.write('''
            At its core, music is a form of art. However, one medium of the art that often goes overlooked is the album
            cover that artists use as a symbol of their music.

            This neat feature allows you to not only explore the art that artists attach to their music but also alter
            various features to derive a piece of art that the artist may have considered otherwise.
            
            At the end of the day, it's just a little fun to have while learning more about your taste of music.
        ''')
    
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

    wksp = st.beta_columns((1,1))
    if option == 'RGB Inverse':
        image = Image.open(requests.get(img_list[0], stream=True).raw)
        wksp[0].subheader('Before Operation')
        wksp[0].image(image)
        r, g, b = image.split()
        image = Image.merge("RGB", (b, g, r))
        wksp[1].subheader('After Operation')
        wksp[1].image(image)
    if option == 'Blur':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(BLUR))
    if option == 'Contour':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(CONTOUR))
    if option == 'Detail':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(DETAIL))
    if option == 'Edges':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(FIND_EDGES))
    if option == 'Enhance':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(EDGE_ENHANCE))
    if option == 'Enhance+':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(EDGE_ENHANCE_MORE))
    if option == 'Emboss':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(EMBOSS))
    if option == 'Smooth':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(SMOOTH))
    if option == 'Smooth+':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(SMOOTH_MORE))
    if option == 'Sharpen':
        image = Image.open(requests.get(img_url, stream=True).raw)
        wksp[0].subheader('Before Operation'); wksp[0].image(image)
        wksp[1].subheader('After Operation'); wksp[1].image(image.filter(SHARPEN))
def project_trends_page(df):
    ##############################################
    st.title('Attribute Trends Over Time')
    with st.beta_expander('Description...'):
        st.write('Here is a description of the grpah you are looking at.')
    
    px_df = df.copy()
    px_df['user_date'] = px_df['user_date'].astype(str).str[:4]
    px_df = px_df.groupby('user_date').agg('mean').drop(columns=['duration', 'explicit', 'tempo', 'signature'])
    for col in px_df.columns:
        if col not in ['popularity', 'loudness']:
            px_df[col] = px_df[col].multiply(100)
        if col == 'loudness':
            px_df[col] = px_df[col].multiply(-100/60)
    pct_df = px_df.pct_change().fillna(0).round(2).multiply(100)

    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        # vertical_spacing=0.02,
                        subplot_titles=("Attribute Score", "Percentage Change"))

    colors = n_colors('rgb(0, 102, 102)', 'rgb(229, 255, 204)', 8, colortype='rgb')
    for i, ncolor, px_col, pct_col in zip(range(px_df.shape[1]), colors, px_df, pct_df):
        fig.add_trace(go.Scatter(x=list(px_df.index), y=px_df[px_col],
                                name=px_col.title(),
                                legendgroup='group'+f'{i}',
                                line=dict(color=ncolor)),
                    row=1, col=1)

        fig.add_trace(go.Bar(x=list(pct_df.index), y=pct_df[pct_col],
                                name=pct_col.title(),
                                legendgroup='group'+f'{i}',
                                marker_color=ncolor,
                                showlegend=False),
                    row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)
    ##############################################
    st.title('Attribute Distributions Over Time')
    with st.beta_expander('Description...'):
        st.write('description goes here boss...')
    attributes = ['popularity','danceability','energy','loudness','acousticness',
            'instrumentalness','liveness','valence']
    cols_group = st.beta_columns((1,1,1,1))
    year = cols_group[0].selectbox(label='Year', options=['All Years'] + sorted(df['user_date'].astype(str).str[:4].astype(int).unique()))
    if year != 'All Years':
        genre = cols_group[1].selectbox(label='Genre', options=['All Genres'] + sorted(df.fillna('NA')[(df['genre'] != 'NA') & (df['user_date'].astype(str).str[:4].astype(int) == year)]['genre'].unique()))
    else:
        genre = cols_group[1].selectbox(label='Genre', options=['All Genres'] + sorted(df[df['genre'] != 'NA']['genre'].unique()))
    attr = cols_group[2].selectbox('Fixed Attribute', options=['None'] + [atbt.title() for atbt in attributes])
    if attr != 'None':
        attr_slid = cols_group[3].slider('Fixed Range', 0, 100, (0,100))
    if attr == 'None':
        attr_slid = cols_group[3].info('No fixed attribute')
    
    px_df = df[df['genre'] != 'NA'][attributes].copy()
    for col in px_df:
        if col not in ['popularity', 'loudness']:
            px_df[col] = px_df[col].multiply(100)
        if col == 'loudness':
            px_df[col] = px_df[col].multiply(-(100/60))
    
    if (year != 'All Years') & (genre != 'All Genres'):
        px_df = px_df[(px_df['user_date'].astype(str).str[:4].astype(int) == year) & (px_df['genre'] == genre)][attributes]
        if attr != 'None':
            px_df = px_df[(px_df[attr.lower()] >= int(attr_slid[0])) & (px_df[attr.lower()] <= int(attr_slid[1]))]
    elif (year != 'All Years') & (genre == 'All Genres'):
        px_df = px_df[px_df['user_date'].astype(str).str[:4].astype(int) == year][attributes]
        if attr != 'None':
            px_df = px_df[(px_df[attr.lower()] >= int(attr_slid[0])) & (px_df[attr.lower()] <= int(attr_slid[1]))]
    elif (year == 'All Years') & (genre != 'All Genres'):
        px_df = px_df[px_df['genre'] == genre][attributes]
        if attr != 'None':
            px_df = px_df[(px_df[attr.lower()] >= int(attr_slid[0])) & (px_df[attr.lower()] <= int(attr_slid[1]))]
    elif (year == 'All Years') & (genre == 'All Genres'):
        px_df = px_df[attributes]
        if attr != 'None':
            px_df = px_df[(px_df[attr.lower()] >= int(attr_slid[0])) & (px_df[attr.lower()] <= int(attr_slid[1]))]
    else:
        st.error('Combination does not exist')

    colors = n_colors('rgb(0, 102, 51)', 'rgb(5, 255, 164)', 8, colortype='rgb')

    fig = go.Figure()
    for col, color in zip(list(px_df.columns)[::-1], colors):
        fig.add_trace(go.Violin(x=px_df[col], line_color=color, name=col.title()))

    fig.update_traces(orientation='h', side='positive', width=3, points=False)
    fig.update_layout(xaxis_showgrid=True, showlegend=False, xaxis_title='Attribute Score')
    st.plotly_chart(fig, use_container_width=True)
    ##############################################
    st.title('Attribute Correlations Over Time')
    with st.beta_expander('Description...'):
        st.write('Here is a description of the grpah you are looking at.')
    cols_group = st.beta_columns((2.4,1.2,1.8,1.8))
    group = cols_group[0].radio(label='Group', options=['Genre', 'Time', 'Pairplot'], key='20:49_0803')
    top_ten_genre = list(df[df['genre'] != 'NA'].groupby('genre').size().sort_values(ascending=False)[:10].index)
    if 'Pairplot' in group:
        scat_df = df[df['genre'].isin(top_ten_genre)]
        scat_cols = ['popularity', 'danceability', 'energy', 'loudness', 'acousticness']
        for col in scat_cols:
            if col not in ['popularity', 'loudness']:
                scat_df[col] = scat_df[col].multiply(100)
            if col == 'loudness':
                scat_df[col] = scat_df[col].multiply(-(100/60))
        
        fig = px.scatter_matrix(scat_df, dimensions=scat_cols,
                        color='genre', color_discrete_sequence=px.colors.sequential.RdBu)
        
        st.plotly_chart(fig, use_container_width=True)
    if 'Genre' in group:
        dimension = cols_group[1].radio(label='Dimensions', options=['2D', '3D'], key='tomato1')
        if '2D' in dimension:
            attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                    'Acousticness', 'Liveness', 'Valence']
            x = cols_group[2].selectbox(label='Attribute 01',
                                        options = attributes,
                                        key='tomato2')
            y = cols_group[3].selectbox(label='Attribute 02',
                                        options = attributes,
                                        key='tomato3')
            px_df = df[(df['genre'] != 'NA') & (df['genre'].isin(top_ten_genre))].copy()
            px_df['loudness'] = px_df['loudness'].multiply(-100/60)
            fig = px.scatter(px_df, x=x.lower(), y=y.lower(), color='genre')
            st.plotly_chart(fig, use_container_width=True)
    
        if '3D' in dimension:
            attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                    'Acousticness', 'Liveness', 'Valence']
            x = cols_group[2].selectbox(label='Attribute 01',
                                        options = attributes,
                                        key='tomato4')
            y = cols_group[3].selectbox(label='Attribute 02',
                                        options = attributes,
                                        key='tomato5')
            px_df = df[(df['genre'] != 'NA') & (df['genre'].isin(top_ten_genre))].copy()
            px_df['loudness'] = px_df['loudness'].multiply(-100/60)
            px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
            px_df['user_month'] = px_df['user_date'].astype(str).str[5:7].astype(int)
            px_df['user_day'] = px_df['user_date'].astype(str).str[-2:].astype(int)
            px_df['user_ym'] = px_df['user_year'] + (px_df['user_month'] / 12) + (px_df['user_day'] / 365)
            fig = px.scatter_3d(px_df, x=x.lower(), y=y.lower(), z='user_ym', color='genre')
            st.plotly_chart(fig, use_container_width=True)
    if 'Time' in group:
        dimension = cols_group[1].radio(label='Dimensions', options=['2D', '3D'], key='tomato1')
        if '2D' in dimension:
            attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                    'Acousticness', 'Liveness', 'Valence']
            x = cols_group[2].selectbox(label='Attribute 01',
                                        options = attributes,
                                        key='tomato7')
            y = cols_group[3].selectbox(label='Attribute 02',
                                        options = attributes,
                                        key='tomato8')
            px_df = df.copy()
            px_df['loudness'] = px_df['loudness'].multiply(-100/60)
            px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
            fig = px.scatter(px_df, x=x.lower(), y=y.lower(), color='user_year')
            st.plotly_chart(fig, use_container_width=True)
        
        if '3D' in dimension:
            attributes = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Instrumentalness',
                                                    'Acousticness', 'Liveness', 'Valence']
            x = cols_group[2].selectbox(label='Attribute 01',
                                        options = attributes,
                                        key='tomato9')
            y = cols_group[3].selectbox(label='Attribute 02',
                                        options = attributes,
                                        key='tomato10')
            px_df = df[(df['genre'] != 'NA') & (df['genre'].isin(top_ten_genre))].copy()
            px_df['loudness'] = px_df['loudness'].multiply(-100/60)
            px_df['user_year'] = px_df['user_date'].astype(str).str[:4].astype(int)
            px_df['user_month'] = px_df['user_date'].astype(str).str[5:7].astype(int)
            px_df['user_day'] = px_df['user_date'].astype(str).str[-2:].astype(int)
            px_df['user_ym'] = px_df['user_year'] + (px_df['user_month'] / 12) + (px_df['user_day'] / 365)
            fig = px.scatter_3d(px_df, x=x.lower(), y=y.lower(), z='user_ym', color='user_ym')
            st.plotly_chart(fig, use_container_width=True)
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

    
    rand_group = st.beta_columns((2.3,7,2.3))
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
    rand_group[2].button('Rerun Randomization')

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
            rand_group[i % 4].write('Count: {}'.format(df[df[attr] == idx_attr].shape[0]))
            rank_df = df[attr].value_counts().sort_values(ascending=False).rank(method='max', ascending=False)
            rand_group[i % 4].write('Rank #{}'.format(int(rank_df.loc[rank_df.index == idx_attr].item())))
        # sort ascending = True
        elif attr in ['liveness', 'loudness', 'artist_date', 'user_date', 'user_time']:
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
def project_recomm_page(df, client_id, client_secret):
    
    st.title('Randomly Generated Recommendations')
    rec_cols = st.beta_columns((1,1,1,1))

    auth_manager = SpotifyClientCredentials(client_id = client_id,
                                                    client_secret = client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    with rec_cols[0].beta_expander('Song'):
        rand_idx = np.random.randint(df.shape[0])
        rec = sp.recommendations(seed_tracks=[df.iloc[rand_idx]['track_url']],
                                    limit=1)
        st.image(rec['tracks'][0]['album']['images'][0]['url'], use_column_width=True)
        st.subheader(rec['tracks'][0]['name'])
        st.write(rec['tracks'][0]['artists'][0]['name'])
    with rec_cols[1].beta_expander('Artist'):
        rand_idx = np.random.randint(df.shape[0])
        rec = sp.recommendations(seed_tracks=[df.iloc[rand_idx]['track_url']],
                                    limit=1)
        st.image(rec['tracks'][0]['album']['images'][0]['url'], use_column_width=True)
        st.subheader(rec['tracks'][0]['artists'][0]['name'])
    with rec_cols[2].beta_expander('Album'):
        rand_idx = np.random.randint(df.shape[0])
        rec = sp.recommendations(seed_tracks=[df.iloc[rand_idx]['track_url']],
                                    limit=1)
        st.image(rec['tracks'][0]['album']['images'][0]['url'], use_column_width=True)
        st.subheader(rec['tracks'][0]['album']['name'])
        st.write(rec['tracks'][0]['artists'][0]['name'])
    with rec_cols[3].beta_expander('Spotify Membership Code'):
        st.image('https://s.yimg.com/ny/api/res/1.2/hJL990zXx8DAOm_ao155kw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTIwMDA7aD0xNTAw/https://s.yimg.com/uu/api/res/1.2/bCY1rmzVTO5bG8aTkWUmkw--~B/aD0xNzcyO3c9MjM2MzthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/insider_articles_922/bb5661ee1b1b1323855be3a0f95eb119')
    
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

        rec_df = df.copy()
        rec_df['danceability'] = (rec_df['danceability']* 100).round(2)
        rec_df['energy'] = (rec_df['energy']* 100).round(2)
        rec_df['acousticness'] = (rec_df['acousticness']* 100).round(2)
        rec_df['instrumentalness'] = (rec_df['instrumentalness']* 100).round(2)
        rec_df['liveness'] = (rec_df['liveness']* 100).round(2)
        rec_df['valence'] = (rec_df['valence']* 100).round(2)
        rec_df['loudness'] = (rec_df['loudness'] * (-100/60)).round(2)
        
        slid_group = st.beta_columns((1,0.05,1))
        slid_group[0].subheader('Attribute Selection')
        slid_group[0].write('Control specific variables that define your music.')
        option = slid_group[0].selectbox('Attribute', options=['Popularity', 'Danceability', 'Energy', 'Instrumentalness', 'Loudness', 'Acousticness', 'Liveness', 'Valence', 'Tempo'])
        if option == 'Tempo':
            slid = slid_group[0].slider(label='', min_value=0, max_value=300, value=(int(rec_df[option.lower()].mean() - 10), int(rec_df[option.lower()].mean() + 10)))
        else:
            slid = slid_group[0].slider(label='', min_value=0, max_value=100, value=(max(0, int(rec_df[option.lower()].mean() - 10)), min(100, int(rec_df[option.lower()].mean() + 10))))

        slid_group[2].subheader('User Input')
        user_input = slid_group[2].radio(label='', options=['Track URL', 'Artist URL'])
        track_url, artist_url = None, None
        if user_input == 'Track URL':
            track_url = slid_group[2].text_input('Track URL', key='track')
        if user_input == 'Artist URL':
            artist_url = slid_group[2].text_input('Artist URL', key='artist')
        slid_group[2].subheader('Customize Results')
        limit = slid_group[2].slider(label='Maximum Number of Results', min_value=1, max_value=100, step=1, value=20)
        gather = slid_group[2].button('Gather Results')

    if gather:
        
        st.subheader('Because you listened to...')
        
        if track_url != None:
            if track_url != '':
                image = sp.track(track_url)['album']['images'][0]['url']
                track_name = sp.track(track_url)['name']
                artist_name = sp.track(track_url)['artists'][0]['name']
                genre_name = ''

                recs = sp.recommendations(seed_tracks=[track_url],
                                        limit=limit)
                
                rec_cols = st.beta_columns((2,8))
                rec_cols[0].image(image)
                rec_cols[1].markdown(f'''
                    Track: {track_name}

                    Artist: {artist_name}

                    Genre: {genre_name}
                    ''')
            else:
                rand_idx = np.random.randint(df.shape[0])
                image = df.iloc[rand_idx]['img_url']
                track_url = df.iloc[rand_idx]['track_url']
                track_name = df.iloc[rand_idx]['title']
                artist_name = df.iloc[rand_idx]['artist']
                genre_name = df.iloc[rand_idx]['genre'].title()
                recs = sp.recommendations(seed_tracks=[track_url],
                                            limit=limit)
            
                rec_cols = st.beta_columns((2,8))
                rec_cols[0].image(image)
                rec_cols[1].markdown(f'''
                    Track: {track_name}

                    Artist: {artist_name}

                    Genre: {genre_name}
                    ''')
        elif artist_url != None:
            if artist_url != '':
                image = sp.artist(artist_url)['images'][0]['url']
                track_name = ''
                artist_name = sp.artist(artist_url)['name']
                genre_name = sp.artist(artist_url)['genres'][0]

                recs = sp.recommendations(seed_artists=[artist_url],
                                        limit=limit)
                rec_cols = st.beta_columns((2,8))
                rec_cols[0].image(image)
                rec_cols[1].markdown(f'''
                    Artist: {artist_name}

                    Genre: {genre_name}
                    ''')
            else:
                rand_idx = np.random.randint(df.shape[0])
                image = df.iloc[rand_idx]['img_url']
                track_url = df.iloc[rand_idx]['track_url']
                track_name = df.iloc[rand_idx]['title']
                artist_name = df.iloc[rand_idx]['artist']
                genre_name = df.iloc[rand_idx]['genre'].title()
                recs = sp.recommendations(seed_tracks=[track_url],
                                            limit=limit)
            
                rec_cols = st.beta_columns((2,8))
                rec_cols[0].image(image)
                rec_cols[1].markdown(f'''
                    Track: {track_name}

                    Artist: {artist_name}

                    Genre: {genre_name}
                    ''')

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
            finaler_cols[i % 4].subheader(rec_data[0])
            finaler_cols[i % 4].write(rec_data[1])
def project_search_page():
    st.title('IDK WHAT I\'M DOING')

# PAGE MEAT
if ready_button:

    try:
        
        data = retrieve_dataframe()
        f_data = alter_dataframe(data)
        
        if not f_data.empty:
            
            try:
                
                if len(radio_page) == 0: st.error('Please select analysis dashboard(s) in "Select Data" sidebar')
                if radio_page == 'Search': project_search_page()
                if 'Brief History' in radio_page:
                    st.title('Brief History Page')
                    st.markdown('''
                    Welcome to the `Brief History Page` -- the page for observing your unique music trends and statistics
                    over the years.

                    As the first dashboard view, take time becoming familiar with the layout and functionality of the page,
                    as it is mirrored throughout the other dashboard views. Graph details can be found in `Description`
                    boxes and each graph hosts interactive features for you to utilize to develop a greater understanding
                    of the music you listen to.
                    ''')
                    project_histry_page(f_data)
                if 'Tracks' in radio_page: 
                    st.title('Tracks Page')
                    st.markdown('''
                        Welcome to the `Tracks Page` -- the page for discovering the highs and lows of your individual
                        tracks. The metrics on this page are gathered by Spotify, and a more detailed description of how the
                        data is gathered for this project can be found in the `GitHub Documentation`.
                    ''')
                    project_tracks_page(f_data)
                if 'Artists + Albums' in radio_page:
                    st.title('Artists + Albums Page')
                    st.markdown('''
                        Welcome to the `Artists + Albums Page` -- the page for discovering which artists have soared
                        to the top of your listening charts and by how much they stand out compared to the others.
                    ''')
                    project_artist_page(f_data)
                if 'Listening Trends' in radio_page:
                    st.title('Listening Trends Page')
                    st.markdown('''
                        Welcome to the `Listening Trends Page` -- the page for diving deeper into when exactly
                        and by how much your taste of music has changed over time.

                        This page offers the most customization of all, so take time exploring the many unique
                        relations between all possible attributes across every genre and every year. To learn
                        more about any of the attributes, please visit the `GitHub Documentation` in the sidebar.
                    ''')
                    project_trends_page(f_data)
                if 'Random Statistics' in radio_page: project_randm_page(f_data)
                if 'Recommendations [Beta]' in radio_page: project_recomm_page(f_data, client_id, client_secret)
                            
                    # except:
                    #     st.error('Cannot generate dashboard for requested view.')

            except:
                st.error('INTERACTIVE PAGE')
    except:
        project_dataq_page(raw_dataframe())
else:
    project_welcm_page()

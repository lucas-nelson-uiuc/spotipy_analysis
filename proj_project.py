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
st.set_option('deprecation.showPyplotGlobalUse', False)

# BODY page layout
st.title('Spotify Analysis Dashboard')
st.write("""
    Welcome to `spotipy_analysis`, a dashboard that presents detailed insights into your Spotify listening habits. By
    providing links to public Spotify playlists (either created by you, someone else, or both), you can learn
    more about what makes your taste in music unique to you and how it has possibly changed over time. 

    If you haven't already, please visit the `Resources` tab in the sidebar to consult how to properly interact
    with this application. Thanks again for checking out this project, and feel free to contact the author
    if you feel inclined to provide any feedback!
""")

# SIDEBAR page layout
with st.beta_container():

    with st.sidebar.beta_expander('Enter Spotify Data', True):
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

    with st.sidebar.beta_expander('Resources', False):
        st.write("[Getting Started](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")
        st.write("[Interaction Guide](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")

    with st.sidebar.beta_expander('Feedback', False):
        if st.slider("How much did you enjoy using this dashboard?", min_value=0, max_value=10, value=0, step=1) != 0:
            if st.selectbox("Did you experience any bugs?", options=['<select>', 'Yes', 'No']) != '<select>':
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

def alter_dataframe(df):
    
    if ready_button:
        
        with st.beta_expander("Interact with Data Frame", True):
            
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

def plot_histogram(df, col):
    return proj_plot.proj_plot_hist(df, col)

# plotting containers
if ready_button:

    data = retrieve_dataframe()
    f_data = alter_dataframe(data)

    # quick statistics
    with st.beta_container():

        st.header('DataFrame at a Glance')
        
        row1 = st.beta_columns((1, 0.8,0.8,0.8,0.8,0.8))

        row1_col0 = row1[0].header(proj_analysis.analysis_convert_raw(f_data))
        row1_col1 = row1[1].header(f_data['title'].unique().shape[0])
        row1_col2 = row1[2].header(f_data['artist'].unique().shape[0])
        row1_col3 = row1[3].header(f_data['album'].unique().shape[0])
        row1_col4 = row1[4].header(f_data[f_data['genre'] != 'NA']['genre'].unique().shape[0])
        row1_col5 = row1[5].header("{}%".format(round(f_data['popularity'].mean())))

        row1_col0 = row1[0].write('duration')
        row1_col1 = row1[1].write('tracks')
        row1_col2 = row1[2].write('artists')
        row1_col3 = row1[3].write('albums')
        row1_col4 = row1[4].write('genres')
        row1_col5 = row1[5].write('popularity')

    # description et plots
    with st.beta_container():

            cols0 = st.beta_columns((4,6))
            titl0 = cols0[0].header('Over the Decades: Release Date')
            desc0 = cols0[0].markdown(
                """
                The music we listen to tends to span across various decades, blending the style from previous decades and introducing unique flair
                for decades to come. Whether it's a specific summer's hit or an all-time classic, knowing when your music was released could
                provide insight into the prevailing taste of music at the time and how involved you were (or would have been) during that era.

                This visualization displays simply that, the periods of music history that grabbed and held onto your ear. Maybe you were born a few
                decades late according to your music taste, or maybe you're right on time. Only you (and your music) will know.
                """)
            data0 = cols0[0].dataframe(proj_analysis.analysis_decade_statistics(f_data))
            plot0 = cols0[1].pyplot(proj_plot.proj_plot_hist(f_data, 'artist_date'))

            cols1 = st.beta_columns((4,6))
            titl1 = cols1[0].header('Over the Decades: Song Duration')
            dsec1 = cols1[0].markdown(
                """
                Are you more likely to listen to many shorter songs or listen to few longer songs? Whether you prefer the upbeat tempo
                of shorter songs or the swelling storyline of longer songs, understanding the distribution of the length of your music could explain
                the specific attributes of the music you listen to as well as your attention span.

                This visualization displays how the length of the music you listen to has changed per decade. Given enough data points, most trends
                follow a positive skew, meaning there is a disproportionate amount of outliers on the right tail compared to the rest of the distribution.
                """)
            data1 = cols1[0].dataframe(proj_analysis.analysis_song_decades(f_data))
            plot1 = cols1[1].pyplot(proj_plot.proj_plot_hist(f_data, 'duration'))

            cols2 = st.beta_columns((4,6))
            titl2 = cols2[0].header('User Input: Annual Additions')
            desc2 = cols2[0].markdown(
                """
                Ever wondered when you were most active on Spotify? Or how active you are now compared to previous years? Nothing says you've explored new
                music more than adding album after album from various artists to your go-to playlists, and on the contrast, how resistant you were to change
                when you added considerably fewer songs in one year compared to the rest.
                
                This graph displays your activity over time, but a deeper look and you can understand how many unique artists and albums you discovered as
                you created and maintained your playlists.
                """)
            data2 = cols2[0].dataframe(proj_analysis.analysis_cat_df(f_data))
            plot2 = cols2[1].pyplot(proj_plot.proj_plot_factor(f_data))
            
            cols3 = st.beta_columns((4,6))
            titl3 = cols3[0].header('User Input: Daily Distractions')
            desc3 = cols3[0].markdown(
                """
                DESCRIPTION HERE.
                """)
            data3 = cols3[0].dataframe(proj_analysis.analysis_user_trends2(f_data))
            plot3 = cols3[1].pyplot(proj_plot.plot_user_datetime(f_data))

            cols4 = st.beta_columns((4,6))
            titl4 = cols4[0].header('Statistics Breakdown: Attribute Trends')
            desc4 = cols4[0].markdown(
                """
                Have you ever realized that you no longer listen to music you once used to listen to? Or maybe you stick to the same old tunes.
                It's one thing to know that your taste in music has or has not changed, but it's another thing to explain how exactly 
                and by how much your taste in music has or has not changed.

                This visualization details the year-to-year change in specific attributes that describe your music. (For a more detailed explanation,
                please refer to the `Resources` sidebar tab.) Drastic changes could imply a change in your preferences whereas stagnant lines could
                display a lack of change.
                """)
            data4 = cols4[0].dataframe(proj_analysis.analysis_attribute_trends(f_data))
            plot4 = cols4[1].pyplot(proj_plot.proj_plot_attribute(f_data))

            cols5 = st.beta_columns((4,6))
            titl5 = cols5[0].header('Statistics Breakdown: Genre Trends')
            desc5 = cols5[0].markdown(
                """
                We've all gone through phases of certain music, playing songs of a certain genre on repeat for days on end, until another trend
                emerged and the process repeats itself. Using the date you added specific songs to your playlists, you can better understand not
                only when these trends occurred but also to what magnitude these trends impacted your listening habits and possibly when they lost momentum.
                """)
            data5 = cols5[0].dataframe(proj_analysis.analysis_genre_trends(f_data))
            plot5 = cols5[1].pyplot(proj_plot.proj_plot_hist(f_data, 'user_date'))
            
            cols6 = st.beta_columns((4,6))
            titl6 = cols6[0].header('Statistics Breakdown: Genre Composition')
            desc6 = cols6[0].markdown(
                """
                Each genre utilizes the same array of musical attributes when producing music, yet when you listen to music from different genres,
                the sounds it produces and the emotions you feel are unique to that genre. Why?
                
                It's because different genres utilize these attributes to varying extents, focusing on some more than others. Rock is energetic,
                classical is not. Classical is acoustic, rock is not. Yet someone can listen to and enjoy/detest both.
                
                Which of those attributes contribute to how much time you spend listening to each genre, and by how much
                or how little? (For a more detailed explanation, please refer to the `Resources` sidebar tab.)
                """)
            data6 = cols6[0].dataframe(proj_analysis.analysis_genre_pd(f_data))
            plot6 = cols6[1].pyplot(proj_plot.proj_plot_nestpie(f_data, 'genre'))
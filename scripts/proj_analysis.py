import streamlit as st
import numpy as np
import pandas as pd
import calendar

import proj_pipeline

def analysis_search_dataframe(df, client_id, client_secret, song_str='', artist_str='', album_str=''):
    if (song_str == '') & (artist_str == '') & (album_str == ''):
        return st.error('Please search for song/artist/album in data')
    elif (song_str != '') and (artist_str != ''):
        return df[(df['title'] == song_str) & (df['artist'] == artist_str)]
    elif (song_str != '') and (album_str != ''):
        return df[(df['title'] == song_str) & (df['album'] == album_str)]
    elif (album_str != '') and (artist_str != ''):
        return df[(df['album'] == album_str) & (df['artist'] == artist_str)]
    elif song_str != '':
        return df[df['title'] == song_str]
    elif artist_str != '':
        return df[df['artist'] == artist_str]
    elif album_str != '':
        return df[df['album'] == album_str]
    else:
        return df
def analysis_filter_dataframe(df, playlist_list, year_range):
    # R0C1: all empty fields
    if (playlist_list == []) & (year_range == (df['artist_date'].min().year, df['artist_date'].max().year)):
        return df
    
    # R3C1: filter playlists, filter artists, filter date
    elif (playlist_list != []) & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        return df[(df['playlist'].isin(playlist_list)) & (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
    
    # R1C1: filter playlists
    elif playlist_list != []:
        return df[df['playlist'].isin(playlist_list)].reset_index(drop=True)
    
    # R1C3: filter date
    elif year_range != (df['artist_date'].min().year, df['artist_date'].max().year):
        return df[df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1))].reset_index(drop=True)

    # DO NOT FORGET ELSE SCENARIO IN PROJ_PROJECT.PY
    else:
        return "INPUT ERROR: Cannot return desired intersection of input fields."

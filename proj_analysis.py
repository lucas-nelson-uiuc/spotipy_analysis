import streamlit as st
import proj_pipeline
import numpy as np
import pandas as pd

def analysis_search_dataframe(df, client_id, client_secret, song_str, artist_str, album_str, year_range):
    # ROC1: all empty fields
    if (song_str == '') & (artist_str == '') & (album_str == '') & (year_range == (df['artist_date'].min().year, df['artist_date'].max().year)):
        return proj_pipeline.pipeline_rick_roll(proj_pipeline.SpotifyUser(client_id, client_secret))

    # R1C1: no empty fields
    elif (song_str != '') & (artist_str != '') & (album_str != '') & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        if (song_str.strip() in df['title'].unique()) & (artist_str.strip() in df['artist'].unique()) & (album_str.strip() in df['album'].unique()):
            return df[(df['title'] == song_str.strip()) | (df['artist'] == artist_str.strip()) | (df['album'] == album_str.strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.upper().strip() in df['title'].unique()) & (artist_str.upper().strip() in df['artist'].unique()) & (album_str.upper().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.upper().strip()) | (df['artist'] == artist_str.upper().strip()) | (df['album'] == album_str.upper().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.lower().strip() in df['title'].unique()) & (artist_str.lower().strip() in df['artist'].unique()) & (album_str.lower().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.lower().strip()) | (df['artist'] == artist_str.lower().strip()) | (df['album'] == album_str.lower().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.title().strip() in df['title'].unique()) & (artist_str.title().strip() in df['artist'].unique()) & (album_str.title().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.title().strip()) | (df['artist'] == artist_str.title().strip()) | (df['album'] == album_str.title().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{song_str}" or "{artist_str} or "{album_str}" or "{year_range}"')
    
    # R2C1: no song field
    elif (artist_str != '') & (album_str != ''):
        if (artist_str.strip() in df['artist'].unique()) & (album_str.strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.strip()) | (df['album'] == album_str.strip())].reset_index(drop=True)
        elif (artist_str.upper().strip() in df['artist'].unique()) & (album_str.upper().strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.upper().strip()) | (df['album'] == album_str.upper().strip())].reset_index(drop=True)
        elif (artist_str.lower().strip() in df['artist'].unique()) & (album_str.lower().strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.lower().strip()) | (df['album'] == album_str.lower().strip())].reset_index(drop=True)
        elif (artist_str.title().strip() in df['artist'].unique()) & (album_str.title().strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.title().strip()) | (df['album'] == album_str.title().strip())].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{artist_str}" or "{album_str} or "{year_range}"')

    # R2C2: no year field
    elif (song_str != '') & (artist_str != '') & (album_str != ''):
        if (song_str.strip() in df['title'].unique()) & (artist_str.strip() in df['artist'].unique()) & (album_str.strip() in df['album'].unique()):
            return df[(df['title'] == song_str.strip()) | (df['artist'] == artist_str.strip()) | (df['album'] == album_str.strip())].reset_index(drop=True)
        elif (song_str.upper().strip() in df['title'].unique()) & (artist_str.upper().strip() in df['artist'].unique()) & (album_str.upper().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.upper().strip()) | (df['artist'] == artist_str.upper().strip()) | (df['album'] == album_str.upper().strip())].reset_index(drop=True)
        elif (song_str.lower().strip() in df['title'].unique()) & (artist_str.lower().strip() in df['artist'].unique()) & (album_str.lower().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.lower().strip()) | (df['artist'] == artist_str.lower().strip()) | (df['album'] == album_str.lower().strip())].reset_index(drop=True)
        elif (song_str.title().strip() in df['title'].unique()) & (artist_str.title().strip() in df['artist'].unique()) & (album_str.title().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.title().strip()) | (df['artist'] == artist_str.title().strip()) | (df['album'] == album_str.title().strip())].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{song_str}" or "{artist_str} or "{album_str}"')

    # R2C3: no album field
    elif (song_str != '') & (artist_str != '') & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        if (song_str.strip() in df['title'].unique()) & (artist_str.strip() in df['artist'].unique()):
            return df[(df['title'] == song_str.strip()) | (df['artist'] == artist_str.strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.upper().strip() in df['title'].unique()) & (artist_str.upper().strip() in df['artist'].unique()):
            return df[(df['title'] == song_str.upper().strip()) | (df['artist'] == artist_str.upper().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.lower().strip() in df['title'].unique()) & (artist_str.lower().strip() in df['artist'].unique()) & (album_str.lower().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.lower().strip()) | (df['artist'] == artist_str.lower().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.title().strip() in df['title'].unique()) & (artist_str.title().strip() in df['artist'].unique()):
            return df[(df['title'] == song_str.title().strip()) | (df['artist'] == artist_str.title().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{song_str}" or "{artist_str} or "{year_range}"')

    # R2C4" no artist field
    elif (song_str != '') & (album_str != '') & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        if (song_str.strip() in df['title'].unique()) & (album_str.strip() in df['album'].unique()):
            return df[(df['title'] == song_str.strip()) | (df['album'] == album_str.strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.upper().strip() in df['title'].unique()) & (album_str.upper().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.upper().strip()) | (df['album'] == album_str.upper().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.lower().strip() in df['title'].unique()) & (album_str.lower().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.lower().strip()) | (df['album'] == album_str.lower().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.title().strip() in df['title'].unique()) & (album_str.title().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.title().strip()) | (df['album'] == album_str.title().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{song_str}" or "{album_str}" or "{year_range}"')

    # R3C1: no album field, no year field
    elif (song_str != '') & (artist_str != ''):
        if (song_str.strip() in df['title'].unique()) & (artist_str.strip() in df['artist'].unique()):
            return df[(df['title'] == song_str.strip()) | (df['artist'] == artist_str.strip())].reset_index(drop=True)
        elif (song_str.upper().strip() in df['title'].unique()) & (artist_str.upper().strip() in df['artist'].unique()):
            return df[(df['title'] == song_str.upper().strip()) | (df['artist'] == artist_str.upper().strip())].reset_index(drop=True)
        elif (song_str.lower().strip() in df['title'].unique()) & (artist_str.lower().strip() in df['artist'].unique()):
            return df[(df['title'] == song_str.lower().strip()) | (df['artist'] == artist_str.lower().strip())].reset_index(drop=True)
        elif (song_str.title().strip() in df['title'].unique()) & (artist_str.title().strip() in df['artist'].unique()):
            return df[(df['title'] == song_str.title().strip()) | (df['artist'] == artist_str.title().strip())].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{song_str}" or "{artist_str}')

    # R3C2: no artist field, no year field
    elif (song_str != '') & (album_str != ''):
        if (song_str.strip() in df['title'].unique()) & (album_str.strip() in df['album'].unique()):
            return df[(df['title'] == song_str.strip()) | (df['album'] == album_str.strip())].reset_index(drop=True)
        elif (song_str.upper().strip() in df['title'].unique()) & (album_str.upper().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.upper().strip()) | (df['album'] == album_str.upper().strip())].reset_index(drop=True)
        elif (song_str.lower().strip() in df['title'].unique()) & (album_str.lower().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.lower().strip()) | (df['album'] == album_str.lower().strip())].reset_index(drop=True)
        elif (song_str.title().strip() in df['title'].unique()) & (album_str.title().strip() in df['album'].unique()):
            return df[(df['title'] == song_str.title().strip()) | (df['album'] == album_str.title().strip())].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{song_str}" or "{album_str}')
    
    # R3C3: no artist field, no album field
    elif (song_str != '') & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        if (song_str.strip() in df['title'].unique()):
            return df[(df['title'] == song_str.strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.upper().strip() in df['title'].unique()):
            return df[(df['title'] == song_str.upper().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.lower().strip() in df['title'].unique()):
            return df[(df['title'] == song_str.lower().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (song_str.title().strip() in df['title'].unique()):
            return df[(df['title'] == song_str.title().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{song_str}" or "{year_range}')

    # R3C4: no song field, no year field
    elif (artist_str != '') & (album_str != ''):
        if (artist_str.strip() in df['artist'].unique()) & (album_str.strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.strip()) | (df['album'] == album_str.strip())].reset_index(drop=True)
        elif (artist_str.upper().strip() in df['artist'].unique()) & (album_str.upper().strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.upper().strip()) | (df['album'] == album_str.upper().strip())].reset_index(drop=True)
        elif (artist_str.lower().strip() in df['artist'].unique()) & (album_str.lower().strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.lower().strip()) | (df['album'] == album_str.lower().strip())].reset_index(drop=True)
        elif (artist_str.title().strip() in df['artist'].unique()) & (album_str.title().strip() in df['album'].unique()):
            return df[(df['artist'] == artist_str.title().strip()) | (df['album'] == album_str.title().strip())].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{artist_str}" or "{album_str}')

    # R3C5: no song field, no album field
    elif (artist_str != '') & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        if (artist_str.strip() in df['artist'].unique()):
            return df[(df['artist'] == artist_str.strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (artist_str.upper().strip() in df['artist'].unique()):
            return df[(df['artist'] == artist_str.upper().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (artist_str.lower().strip() in df['artist'].unique()):
            return df[(df['artist'] == artist_str.lower().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (artist_str.title().strip() in df['artist'].unique()):
            return df[(df['artist'] == artist_str.title().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{artist_str}" or "{year_range}')
    
    # R3C6: no song field, no artist field
    elif (album_str != '') & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        if (album_str.strip() in df['album'].unique()):
            return df[(df['album'] == album_str.strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (album_str.upper().strip() in df['album'].unique()):
            return df[(df['album'] == album_str.upper().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (album_str.lower().strip() in df['album'].unique()):
            return df[(df['album'] == album_str.lower().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        elif (album_str.title().strip() in df['album'].unique()):
            return df[(df['album'] == album_str.title().strip()) | (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
        else:
            st.error(f'Cannot find one of "{album_str}" or "{year_range}')
    
    # R4C1: no aritst field, no album field, no year field
    elif song_str != '':
        if song_str.strip() in df['title'].unique():
            return df[df['title'] == song_str.strip()].reset_index(drop=True)
        elif song_str.upper().strip() in df['title'].unique():
            return df[df['title'] == song_str.upper().strip()].reset_index(drop=True)
        elif song_str.lower().strip() in df['title'].unique():
            return df[df['title'] == song_str.title().lower()].reset_index(drop=True)
        elif song_str.title().strip() in df['title'].unique():
            return df[df['title'] == song_str.title().strip()].reset_index(drop=True)
        else:
            st.error(f'Cannot find song "{song_str}"')
    
    # R4C2: no song field, no album field, no year field
    elif artist_str != '':
        if artist_str.strip() in df['artist'].unique():
            return df[df['artist'] == artist_str.strip()].reset_index(drop=True)
        elif artist_str.upper().strip() in df['artist'].unique():
            return df[df['artist'] == artist_str.upper().strip()].reset_index(drop=True)
        elif artist_str.lower().strip() in df['artist'].unique():
            return df[df['artist'] == artist_str.lower().strip()].reset_index(drop=True)
        elif artist_str.title().strip() in df['artist'].unique():
            return df[df['artist'] == artist_str.title().strip()].reset_index(drop=True)
        else:
            st.error(f'Cannot find artist "{artist_str}"')

    # R4C2: no song field, no artist field, no year field
    elif album_str != '':
        if album_str.strip() in df['album'].unique():
            return df[df['album'] == album_str.strip()].reset_index(drop=True)
        elif album_str.upper().strip() in df['album'].unique():
            return df[df['album'] == album_str.upper().strip()].reset_index(drop=True)
        elif album_str.lower().strip() in df['album'].unique():
            return df[df['album'] == album_str.lower().strip()].reset_index(drop=True)
        elif album_str.title().strip() in df['album'].unique():
            return df[df['album'] == album_str.title().strip()].reset_index(drop=True)
        else:
            st.error(f'Cannot find album "{album_str}"')
    
    # R4C3: no song field, no artist field, no album field
    elif year_range != (df['artist_date'].min().year, df['artist_date'].max().year):
        return df[df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1))].reset_index(drop=True)
    
    # R5C0: super weird exception; should never execute
    else:
        return "CODE ERROR: Please contact author to report bug."

def analysis_filter_dataframe(df, playlist_list, artist_list, year_range):
    # R0C1: all empty fields
    if (playlist_list == []) & (artist_list == []) & (year_range == (df['artist_date'].min().year, df['artist_date'].max().year)):
        return df
    
    # R3C1: filter playlists, filter artists, filter date
    elif (playlist_list != []) & (artist_list != []) & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        return df[(df['playlist'].isin(playlist_list)) & (df['artist'].isin(artist_list)) & (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
    
    # R2C1: filter playlists, filter artists
    elif (playlist_list != []) & (artist_list != []):
        return df[(df['playlist'].isin(playlist_list)) & (df['artist'].isin(artist_list))].reset_index(drop=True)
    
    # R2C2: filter playlists, filter date
    elif (playlist_list != []) & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        return df[(df['playlist'].isin(playlist_list)) & (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
    
    # R2C3: filter artists, filter date
    elif (artist_list != []) & (year_range != (df['artist_date'].min().year, df['artist_date'].max().year)):
        return df[(df['artist'].isin(artist_list)) & (df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1)))].reset_index(drop=True)
    
    # R1C1: filter playlists
    elif playlist_list != []:
        return df[df['playlist'].isin(playlist_list)].reset_index(drop=True)
    
    # R1C2: filter artists
    elif artist_list != []:
        return df[df['artist'].isin(artist_list)].reset_index(drop=True)
    
    # R1C3: filter date
    elif year_range != (df['artist_date'].min().year, df['artist_date'].max().year):
        return df[df['artist_date'].astype(str).str[:4].astype(int).isin(range(year_range[0],year_range[1]+1))].reset_index(drop=True)

    # DO NOT FORGET ELSE SCENARIO IN PROJ_PROJECT.PY
    else:
        return "INPUT ERROR: Cannot return desired intersection of input fields."

def analysis_time_convert(df):
    duration_mins = df['duration'].sum() / 60000
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

def analysis_genre_convert(df, client_id, client_secret):
    
    total_genres = df['genre'].unique()
    sptfy_genres = proj_pipeline.pipeline_genres_spotify(proj_pipeline.SpotifyUser(client_id, client_secret))
    
    for genre in total_genres:
        if genre in sptfy_genres:
            return None
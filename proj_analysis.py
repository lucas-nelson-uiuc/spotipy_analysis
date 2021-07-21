import streamlit as st
import numpy as np
import pandas as pd
import calendar
from matplotlib import pyplot as plt, dates as mdates

import proj_pipeline



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

# APPLICATION DATAFRAMES: appear on app
# song duration container
def analysis_song_decades(df):
    test_df = df.copy()
    test_df = test_df[['duration', 'artist_date']]
    test_df['artist_date'] = test_df['artist_date'].astype(str).str[:4]
    test_df['artist_date'] = (test_df['artist_date'].astype(int) // 10) * 10
    test_df['duration'] = test_df['duration'] // 60000
    test_df = test_df.set_index('artist_date').sort_index()
    result = test_df.groupby('artist_date').describe().unstack(1).reset_index().pivot(index='artist_date', values=0, columns='level_1')
    result = result[['count', 'max', 'min', 'mean', 'std', '25%', '50%', '75%']]
    app = pd.DataFrame({
        'count':result['count'].sum(),
        'max':result['max'].max(),
        'min':result['min'].min(),
        'mean':result['mean'].mean(),
        'std':result['std'].mean(),
        '25%':result['25%'].mean(),
        '50%':result['50%'].mean(),
        '75%':result['75%'].mean()
        }, index=['Total'])
    concat = pd.concat([result, app])
    concat['count'] = concat['count'].astype(int)
    concat['max'] = concat['max'].astype(int)
    concat['min'] = concat['min'].astype(int)
    return concat

# production date container
def analysis_decade_statistics(df):
    test_df = df.copy()
    test_df = test_df.drop(columns=['user_date', 'user_time','url', 'tempo','signature','playlist'])
    test_df['artist_date'] = test_df['artist_date'].astype(str).str[:4]
    test_df['artist_date'] = (test_df['artist_date'].astype(int) // 10) * 10
    test_df = test_df.set_index('artist_date').sort_index()
    test_df = test_df.groupby('artist_date').aggregate({
        'title':'count',
        'artist': lambda x : x.nunique(),
        'album': lambda x : x.nunique(),
        'genre': lambda x : x.nunique(),
        'duration':'sum',
        'explicit':'sum',
        'popularity':'mean',
        'danceability':'mean',
        'energy':'mean',
        'loudness':'mean',
        'speechiness':'mean',
        'acousticness':'mean',
        'instrumentalness':'mean',
        'liveness':'mean',
        'valence':'mean'
    })
    test_df['popularity'] = test_df['popularity'].astype(int)
    test_df['duration'] = test_df['duration'].apply(analysis_convert_ms)
    for col in ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']:
        if col == 'loudness':
            test_df[col] = (test_df[col].round(2) * (100/60)).astype(int)
        else:
            test_df[col] = (test_df[col].round(2) * 100).astype(int)
    test_df.rename(columns={'title':'songs', 'artist':'artists', 'album':'albums','genre':'genres'}, inplace=True)
    return test_df

# genre ecdf container
def analysis_genre_trends(df):
    test_df = df[df['genre'] != 'NA']
    test_df = test_df[['user_date', 'genre']]
    test_df['user_date'] = test_df['user_date'].astype(str).str[:4]
    test_df = test_df.groupby(['user_date', 'genre']).size().reset_index().rename(columns={0:'count'})
    result = pd.pivot(test_df, index='genre', columns="user_date", values="count").fillna(0)
    return result.astype(int)

def analysis_attribute_trends(df):
    test_df = df.copy()
    test_df.drop(columns=['title', 'artist', 'album', 'genre', 'url', 'duration', 'explicit', 'artist_date', 'user_time', 'tempo', 'signature', 'playlist'], inplace=True)
    test_df['user_date'] = test_df['user_date'].astype(str).str[:4]
    test_df['loudness'] = abs(test_df['loudness'] * 100/60)
    for col in list(test_df.columns[2:]):
        if col != 'loudness':
            test_df[col] = test_df[col] * 100
    return test_df.groupby('user_date').agg('mean')

def analysis_attribute_pctchange(df):
    return analysis_attribute_trends(df).pct_change() * 100

def analysis_user_trends(df):
    test_df = df.copy()
    test_df = test_df[['user_date', 'user_time']]
    test_df['datetime'] = test_df['user_date'].astype(str) + ' ' + test_df['user_time'].astype(str)
    test_df.drop(columns=['user_date', 'user_time'], inplace=True)
    # Convert to datetime
    test_df['datetime'] = pd.to_datetime(test_df['datetime'])
    # Create Categorical Column
    cat_type = pd.CategoricalDtype(list(calendar.day_name), ordered=True)
    test_df['day_of_week'] = pd.Categorical.from_codes(
        test_df['datetime'].dt.day_of_week, dtype=cat_type
    )
    # Create Normalized Date Column
    test_df['time_of_day'] = pd.to_datetime('2000-01-01 ' +
                                    test_df['datetime'].dt.time.astype(str))
    return test_df

def analysis_user_trends2(df):
    test_df = df.copy()
    test_df = test_df[['user_date', 'user_time']]
    test_df['datetime'] = test_df['user_date'].astype(str) + ' ' + test_df['user_time'].astype(str)
    test_df.drop(columns=['user_date', 'user_time'], inplace=True)

    # df = pd.DataFrame({...})

    # Convert to datetime
    test_df['datetime'] = pd.to_datetime(test_df['datetime'])
    
    return test_df

# genre breakdown container
def analysis_genre_pd(df):
    test_df = df[df['genre'] != 'NA'].copy()
    test_df['adj_loud'] = abs(test_df['loudness']) / 60
    test_df['frac_pop'] = abs(test_df['popularity']) / 100
    test_df = test_df[['genre', 'duration', 'frac_pop', 'adj_loud', 'danceability', 'energy', 'speechiness',
                'acousticness', 'instrumentalness', 'liveness', 'valence']]
    
    agg_d = {
    'duration':'sum',
    'frac_pop':'mean',
    'adj_loud':'mean',
    'danceability':'mean',
    'energy':'mean',
    'speechiness':'mean',
    'acousticness':'mean',
    'instrumentalness':'mean',
    'liveness':'mean',
    'valence':'mean'
    }
    test_df = test_df.groupby('genre').agg(agg_d)
    test_df['adj_score'] = test_df.drop(columns='duration',axis=1).sum(axis=1)

    if len(test_df.reset_index()['genre'].unique()) < 5:
        test_df = test_df.sort_values('duration', ascending=False).iloc[:len(test_df.reset_index()['genre'].unique())]
    else:
        test_df = test_df.sort_values('duration', ascending=False).iloc[:5]
    for col in test_df.columns:
        if col not in ['genre', 'duration', 'adj_score']:
            test_df[col] = (test_df[col] / test_df['adj_score']) * test_df['duration']
    
    test_df.rename(columns={'adj_loud':'loudness', 'frac_pop':'popularity'}, inplace=True)

    retr_df= pd.DataFrame(test_df.reset_index().melt(id_vars=['genre'],
                                        value_vars=['popularity', 'loudness', 'danceability',
                                                    'energy', 'speechiness', 'acousticness',
                                                    'instrumentalness', 'liveness', 'valence']).groupby(['genre','variable'])['value'].sum())
    retr_df['percentage'] = retr_df.groupby(level='genre').apply(lambda x:100 * x / float(x.sum()))
    
    return retr_df.sort_values('value', ascending= False).sort_index(level='genre', sort_remaining=False)

# TRANSFER DATAFRAMES: solely used in other files
def analysis_cat_df(df):
    test_df = df[df['genre'] != 'NA'].copy()
    test_df = test_df[['title', 'artist', 'album', 'genre', 'duration', 'explicit', 'popularity', 'user_date']]
    test_df['user_date'] = test_df['user_date'].astype(str).str[:4]
    result = test_df.groupby('user_date').aggregate({
        'title' : lambda x : x.nunique(),
        'artist': lambda x : x.nunique(),
        'album' : lambda x : x.nunique(),
        'genre' : lambda x : x.nunique(),
        'duration': 'sum',
        'explicit': 'sum',
        'popularity': 'mean'
    })
    result['duration'] = result['duration'].apply(analysis_convert_min)
    result['popularity'] = result['popularity'].astype(int)
    result.rename(columns={'title':'songs','artist':'artists','album':'albums', 'genre':'genres'}, inplace=True)
    return result

# CONVERSION functions
def analysis_transform_year(year_col):
    bottom_five = (year_col // 10) * 10
    top_five = ((year_col // 10) + 1) * 10
    return f'{bottom_five}-{top_five}'

def analysis_convert_raw(df):
    test_df = df.copy()
    
    duration_mins = test_df['duration'].sum() / 60000
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

def analysis_convert_min(mins):
    hours = (mins // 60)
    minutes = mins - (hours * 60)
    seconds = (mins - int(mins)) * 60
    if int(hours) > 0:
        return "{}h{}m{}s".format(int(hours), int(minutes), int(seconds))
    elif int(minutes) > 0:
        return "{}m{}s".format(int(minutes), int(seconds))
    else:
        return "{}s".format(int(seconds))

def analysis_convert_ms(ms):
    seconds=(ms/1000)%60
    minutes=(ms/(1000*60))%60
    hours=(ms/(1000*60*60))%24
    
    if int(hours) > 0:
        return "{}h{}m{}s".format(int(hours), int(minutes), int(seconds))
    elif int(minutes) > 0:
        return "{}m{}s".format(int(minutes), int(seconds))
    else:
        return "{}s".format(int(seconds))

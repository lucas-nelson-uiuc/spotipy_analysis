import streamlit as st
import numpy as np
import pandas as pd
import calendar
from matplotlib import pyplot as plt, dates as mdates

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

# APPLICATION DATAFRAMES: appear on app
# song duration container
def analysis_song_decades(df):
    test_df = df.copy()
    test_df = test_df[['duration', 'artist_date']]
    test_df['artist_date'] = test_df['artist_date'].astype(str).str[:4]
    test_df['artist_date'] = (test_df['artist_date'].astype(int) // 10) * 10
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
        }, index=['Stats'])
    concat = pd.concat([result, app])
    for col in concat.columns:
        if col != 'count':
            concat[col] = pd.to_datetime(concat[col], unit='ms').dt.time.astype(str).str[3:-7]
    concat['count'] = concat['count'].astype(int)
    return concat
# production date container
def analysis_decade_statistics(df):
    test_df = df.copy()
    test_df = test_df.drop(columns=['user_date', 'user_time','track_url', 'img_url', 'tempo','signature','playlist'])
    test_df['artist_date'] = test_df['artist_date'].astype(str).str[:4]
    test_df['artist_date'] = (test_df['artist_date'].astype(int) // 10) * 10
    test_df = test_df.set_index('artist_date').sort_index()
    test_df = test_df.groupby('artist_date').aggregate({
        'title':'count',
        'artist': lambda x : x.nunique(),
        'album': lambda x : x.nunique(),
        'genre': lambda x : x.nunique(),
        'duration':'sum'
    })
    test_df['duration'] = pd.to_datetime(test_df['duration'], unit='ms').dt.time.astype(str).str[:-7]
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
# DESCRIPTION
def analysis_attribute_decades(df):
    test_df = df.copy()
    test_df.drop(columns=['title', 'artist', 'album', 'track_url', 'img_url', 'duration', 'explicit', 'user_date', 'user_time', 'signature', 'playlist'], inplace=True)
    test_df['decade'] = test_df['artist_date'].astype(str).str[:4].apply(analysis_transform_year)
    test_df.drop('artist_date', inplace=True)
    test_df['loudness'] = abs(test_df['loudness'] * 100/60)
    for col in list(test_df.columns[2:]):
        if col not in ['loudness', 'genre', 'artist_date']:
            test_df[col] = test_df[col] * 100
    return test_df.groupby(['decade', 'genre']).agg('mean')
# attribute trends over time
def analysis_attribute_trends(df, col):
    test_df = df.copy()
    test_df.drop(columns=['title', 'artist', 'album', 'genre', 'tempo', 'track_url', 'img_url', 'duration', 'explicit', 'artist_date', 'user_time', 'signature', 'playlist'], inplace=True)
    test_df['user_date'] = test_df['user_date'].astype(str).str[:4]
    test_df['loudness'] = abs(test_df['loudness'] * 100/60)
    for column in list(test_df):
        if column not in ['user_date', 'popularity', 'loudness']:
            test_df[column] = test_df[column] * 100
    if col == None:
        return test_df.groupby('user_date').agg('mean').transpose()
    if col != None:
        return test_df.groupby('user_date').agg('mean').transpose().loc[col, : ]
# song cumsum over time per genre
def analysis_attribute_genre(df, col):
    if col == 'artist_date':
        test_df = df.copy()
        test_df = test_df[test_df['genre'] != 'NA']
        test_df = test_df[['genre', col, 'title']]
        test_df.rename(columns={'title':'count'}, inplace=True)
        test_df[col] = test_df[col].astype(str).str[:4].astype(int).apply(lambda x : analysis_custom_round(x))
        test_df = test_df.groupby(['genre', col]).agg('count')
        return test_df.reset_index().pivot(index='genre', columns=col).fillna(0).astype(int)
    if col == 'user_date':
        test_df = df.copy()
        test_df = test_df[test_df['genre'] != 'NA']
        test_df = test_df[['genre', col, 'title']]
        test_df.rename(columns={'title':'count'}, inplace=True)
        test_df[col] = test_df[col].astype(str).str[:4].astype(int)
        test_df = test_df.groupby(['genre', col]).agg('count')
        return test_df.reset_index().pivot(index='genre', columns=col).fillna(0).astype(int).cumsum(axis=1)
# specific attribute over time per genre
def analysis_attribute_sums(df, col):
    test_df = df.copy()
    test_df = test_df[test_df['genre'] != 'NA']
    test_df.drop(columns=['title', 'artist', 'album', 'track_url', 'img_url', 'duration', 'explicit', 'artist_date', 'user_time', 'signature', 'playlist'], inplace=True)
    test_df['user_date'] = test_df['user_date'].astype(str).str[:4]
    test_df['loudness'] = abs(test_df['loudness'] * 100/60)
    for column in list(test_df.columns):
        if column not in ['user_date', 'genre', 'loudness', 'popularity']:
            test_df[column] = test_df[column] * 100
    test_df = test_df.groupby(['genre', 'user_date'])[col].agg('mean')
    test_df = test_df.reset_index(level='user_date')
    return test_df.reset_index().pivot(index='genre', columns='user_date').fillna(method='ffill', axis=1).replace({np.nan:0, np.inf:9999}).astype(int)
# attribute trends % change over time
def analysis_attribute_pctchange(df):
    return analysis_attribute_trends(df, col=None).pct_change().multiply(100)
# DESCRIPTION
def analysis_genre_pctchange(df, col):
    return analysis_attribute_sums(df, col).pct_change(axis=1).fillna(0).replace(np.inf, 99.99).multiply(100).astype(int)
# DESCRIPTION
def analysis_plot_genrechange(df, col):
    test_df = df[df['genre'] != 'NA'].groupby('genre').filter(lambda x : len(x) > 10).reset_index(drop=True).copy()
    test_df.drop(columns=['title', 'artist', 'album', 'url', 'duration', 'explicit', 'artist_date', 'user_time', 'signature', 'playlist'], inplace=True)
    test_df['user_date'] = test_df['user_date'].astype(str).str[:4].astype(int)
    test_df['loudness'] = abs(test_df['loudness'] * 100/60)
    for col in list(test_df.columns):
        if col not in ['user_date', 'genre', 'loudness', 'popularity']:
            test_df[col] = test_df[col] * 100
    return test_df.groupby(['genre', 'user_date']).agg('mean')
# DESCRIPTION
def analysis_plot_pctchange(df, col):
    test_df = df.copy()
    test_df.drop(columns=['title', 'artist', 'album', 'genre', 'track_url', 'img_url', 'duration', 'explicit', 'artist_date', 'user_time', 'signature', 'playlist'], inplace=True)
    test_df['user_date'] = test_df['user_date'].astype(str).str[:4].astype(int)
    test_df['loudness'] = abs(test_df['loudness'] * 100/60)
    for col in list(test_df.columns):
        if col not in ['user_date', 'loudness', 'popularity']:
            test_df[col] = test_df[col] * 100
    return test_df.groupby(['user_date']).agg('mean')
# DESCRIPTION
def analysis_user_trends(df):
    test_df = df.copy()
    test_df = test_df[['user_date', 'user_time']]
    test_df['datetime'] = test_df['user_date'].astype(str) + ' ' + test_df['user_time'].astype(str)
    test_df.drop(columns=['user_date', 'user_time'], inplace=True)
    
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
# DESCRIPTION
def analysis_user_trends2(df):
    test_df = df.copy()
    test_df = test_df[['user_date', 'user_time']]
    test_df['datetime'] = test_df['user_date'].astype(str) + ' ' + test_df['user_time'].astype(str)
    test_df.drop(columns=['user_date', 'user_time'], inplace=True)

    # df = pd.DataFrame({...})

    test_df['datetime'] = pd.to_datetime(test_df['datetime'])
    
    return test_df
# genre breakdown container
def analysis_genre_pd(df):
    test_df = df[df['genre'] != 'NA'].copy()
    test_df['adj_loud'] = abs(test_df['loudness']) / 60
    test_df['frac_pop'] = abs(test_df['popularity']) / 100
    test_df = test_df[['genre', 'duration', 'frac_pop', 'adj_loud', 'danceability', 'energy',
                'acousticness', 'instrumentalness', 'liveness', 'valence']]
    agg_d = {
    'duration':'sum',
    'frac_pop':'mean',
    'adj_loud':'mean',
    'danceability':'mean',
    'energy':'mean',
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
                                                    'energy', 'acousticness',
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
    result['duration'] = pd.to_datetime(result['duration'], unit='ms').dt.time
    result['popularity'] = result['popularity'].astype(int)
    result.rename(columns={'title':'songs','artist':'artists','album':'albums', 'genre':'genres'}, inplace=True)
    return result
# CONVERSION functions
def analysis_custom_round(x, base=5):
    return int(base * round(float(x)/base))
def analysis_transform_year(year_col, base=10):
    year_col = int(year_col)
    bot_bound = (year_col // base) * base
    top_bound = ((year_col // base) + 1) * base
    return f'{bot_bound}-{top_bound}'
def analysis_pretty_time(df):
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
import streamlit as st
import pandas as pd
import numpy as np
import calendar
import seaborn as sns
from matplotlib import pyplot as plt, dates as mdates
import math
import proj_analysis

# PLOT OBJECTS
def proj_plot_hist(df, col):
    if col == 'artist_date':
        df[col] = df[col].astype(str).str[:4].astype(int).sort_values()
        return sns.displot(data=df, x=col).set(xlabel='Year', ylabel='# of Songs').set_xticklabels(rotation=45)

    if col == 'duration':
        df[col] = df[col] / 60000
        df['decade'] = df['artist_date'].apply(proj_analysis.analysis_transform_year)
        hue_order = sort_hue_order(df['decade'])
        plt.style.use('seaborn-white')
        return sns.displot(df, x=col,
                            hue='decade',
                            hue_order=hue_order,
                            kind='hist',
                            multiple='stack',
                            palette='Paired').set(xlabel='Duration (min)',
                            ylabel='# of Songs')

    if col == 'artist':
        plt.style.use('seaborn-white')
        return sns.displot(df, x=col,
                            hue='decade',
                            hue_order=hue_order,
                            kind='hist',
                            multiple='stack',
                            palette='Paired').set(xlabel='Duration (min)',
                            ylabel='# of Songs')

    if col == 'user_date':
        test_df = df[df['genre'] != 'NA'].groupby('genre').filter(lambda x : len(x) > 10).reset_index()
        return sns.displot(data=test_df, x='user_date', kind='ecdf', hue='genre', palette='gist_ncar', stat='count'
                    ).set(xlabel='Year-Month', ylabel='# of Songs').set_xticklabels(rotation=45)

    if col == 'tempo':
        test_df = df[df['genre'] != 'NA'].groupby('genre').filter(lambda x : len(x) > 10).reset_index()
        plt.style.use('seaborn-white')
        return sns.displot(test_df, x=col,
                            hue='genre',
                            kind='hist',
                            multiple='stack',
                            palette='coolwarm').set(xlabel='Tempo (bpm)',
                            ylabel='# of Songs')

def proj_plot_factor(df):
    result = proj_analysis.analysis_cat_df(df)
    plot_df = result.reset_index().melt(id_vars='user_date', value_vars=['songs','artists','albums']).set_index('user_date').sort_index()
    plot_df.reset_index(inplace=True)
    return sns.catplot(data=plot_df, x='user_date', y='value', hue='variable', kind='bar', palette='Paired'
                    ).set(xlabel='Year', ylabel='# of Songs')
    
def proj_plot_attribute(df, method):
    if method == 'mean':
        test_df = proj_analysis.analysis_attribute_trends(df)
        plot_df = test_df.copy()
        plot_df = plot_df.reset_index().melt(id_vars=['user_date'],
                                value_vars=['popularity',
                                        'danceability',
                                        'energy',
                                        'loudness',
                                        'speechiness',
                                        'acousticness',
                                        'instrumentalness',
                                        'liveness',
                                        'valence']).set_index('user_date').sort_index().reset_index()
        return sns.catplot(data=plot_df, x='user_date', y='value', hue='variable', kind='point', palette='Paired'
                        ).set(xlabel='Year', ylabel='Attribute Score')

    if method == 'pct_change':
        test_df = proj_analysis.analysis_attribute_pctchange(df)
        plot_df = test_df.copy()
        plot_df = plot_df.reset_index().melt(id_vars=['user_date'],
                                value_vars=['popularity',
                                        'danceability',
                                        'energy',
                                        'loudness',
                                        'speechiness',
                                        'acousticness',
                                        'instrumentalness',
                                        'liveness',
                                        'valence']).set_index('user_date').sort_index().reset_index()
        return sns.catplot(data=plot_df, x='user_date', y='value', hue='variable', kind='bar', palette='Paired'
                        ).set(xlabel='Year', ylabel='Percent Change (%)')

def plot_user_datetime(df):
    plot_dfdf = proj_analysis.analysis_user_trends(df)
    
    return sns.displot(data=plot_dfdf, x='time_of_day', hue='day_of_week', kind='kde',  multiple='stack', palette='ocean')
    # g = sns.displot(data=plot_dfdf, x='time_of_day', hue='day_of_week', kind='kde', multiple='stack', palette='ocean')
    # g.set_xlim([pd.to_datetime('2000-01-01 00:00:00'),
    #             pd.to_datetime('2000-01-01 23:59:59')])
    # g.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    
def proj_plot_nestpie(df, col):
    pie_df = proj_analysis.analysis_genre_pd(df)
    copy_df = pie_df.reset_index()
    pie_labels = np.where(copy_df['variable'] == 'frac_pop', 'popularity',
                    np.where(copy_df['variable'] == 'adj_loud', 'loudness',
                        np.where(copy_df['variable'] == 'danceability', 'dance',
                                np.where(copy_df['variable'] == 'speechiness', 'speech',
                                        np.where(copy_df['variable'] == 'acousticness', 'acoustic',
                                                np.where(copy_df['variable'] == 'instrumentalness', 'instrumental',
                                                        np.where(copy_df['variable'] == 'liveness', 'live', copy_df['variable'])))))))
    
    facecolor = '#eaeaf2'
    font_color = '#525252'
    hfont = {'fontname':'Calibri'}
    if len(copy_df['genre'].unique()) < 5:
        labels = copy_df['genre'].unique()
    else:
        labels = copy_df['genre'].unique()[:5]
    size = 0.3
    vals = copy_df['value']
    # Major category values = sum of minor category values
    group_sum = pie_df.groupby('genre')['value'].sum()
    
    fig, ax = plt.subplots(figsize=(10,6), facecolor=facecolor)
    a,b,c,d,e = [plt.cm.Purples, plt.cm.Reds, plt.cm.Greens, plt.cm.Blues, plt.cm.RdPu]
    outer_colors = [a(.8), b(.8), c(.8), d(.8), e(.8)]
    inner_colors = [a(.75), a(.71), a(.67), a(.63), a(.59), a(.55), a(.51), a(.47), a(.43),
                    b(.75), b(.71), b(.67), b(.63), b(.59), b(.55), b(.51), b(.47), b(.43),
                    c(.75), c(.71), c(.67), c(.63), c(.59), c(.55), c(.51), c(.47), c(.43),
                    d(.75), d(.71), d(.67), d(.63), d(.59), d(.55), d(.51), d(.47), d(.43),
                    e(.75), e(.71), e(.67), e(.63), e(.59), e(.55), e(.51), e(.47), e(.43),
    ]
                
    plt.style.use('seaborn-white')
    ax.pie(group_sum, 
        radius=1, 
        colors=outer_colors, 
        labels=labels, 
        textprops={'color':font_color},
        wedgeprops=dict(width=size, edgecolor='w'),
        counterclock=False)

    ax.pie(vals, 
        radius=1-size, # size=0.3
        colors=inner_colors,
        wedgeprops=dict(width=size, edgecolor='w'),
        counterclock=False)

    return fig

# FIXING PLOTS
def sort_hue_order(five_year_col):
    five_year_set = list(five_year_col.unique())
    return sorted(five_year_set, reverse=True)
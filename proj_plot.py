import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math

def proj_plot_hist(df, col):
    if col == 'duration':
        df[col] = df[col] / 60000
    df['artist_five_year'] = df['artist_date'].apply(transform_year)
    hue_order = sort_hue_order(df['artist_five_year'])

    sns.set(style='white')
    
    figure = sns.displot(df, x=col,
                        hue='artist_five_year',
                        hue_order=hue_order,
                        discrete=True)
    figure.set(xlabel='Duration (min)',
                ylabel='# of songs')
    figure.legend.set_title('')
    # plt.legend(loc='upper right')
    return figure

def transform_year(year_col):
    year_col = year_col.year
    bottom_five = (year_col // 10) * 10
    top_five = ((year_col // 10) + 1) * 10
    return f'{bottom_five}-{top_five}'

def sort_hue_order(five_year_col):
    five_year_set = list(five_year_col.unique())
    return sorted(five_year_set, reverse=True)

# outer: genre%, inner: total time
def proj_plot_nestpie(df, col):
    fig, ax = plt.subplots(subplot_kw=dict(projection="polar"))

    size = 0.3
    # represent genre by song% and listen time
    vals = np.array([[60., 32.], [37., 40.], [29., 10.]])
    #normalize vals to 2 pi
    valsnorm = vals/np.sum(vals)*2*np.pi
    #obtain the ordinates of the bar edges
    valsleft = np.cumsum(np.append(0, valsnorm.flatten()[:-1])).reshape(vals.shape)

    cmap = plt.get_cmap("tab20c")
    outer_colors = cmap(np.arange(3)*4)
    inner_colors = cmap([1, 2, 5, 6, 9, 10])

    ax.bar(x=valsleft[:, 0],
        width=valsnorm.sum(axis=1), bottom=1-size, height=size,
        color=outer_colors, edgecolor='w', linewidth=1, align="edge")

    ax.bar(x=valsleft.flatten(),
        width=valsnorm.flatten(), bottom=1-2*size, height=size,
        color=inner_colors, edgecolor='w', linewidth=1, align="edge")

    ax.set(title="Pie plot with `ax.bar` and polar coordinates")
    ax.set_axis_off()
    plt.show()


# x-axis: col (year, genre, ), y-axis: song count
def proj_plot_bar(df, col):
    # df[col].value_counts()
    return None

def proj_plot_smth():
    return None
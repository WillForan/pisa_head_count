#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import sys      # args and exit
import re       # match and remove ♀
import io       # save plot to stream


def game_roster(match_date, ngames=10):
    """
    0. pull game roster from google sheets and clean it up a bit
     - remove junk rows (only take as many rows as there are games)
     - reformat date from m/d to mm/dd to match python's strftime
    1. select only the row that matches the game date we provide
    """
    gsheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQW4QdMnwot2ABQjt7HScESNRRbzTCvcGBJT7qRwymS28scPSBlL5aLixxVly8Gmjst0TDoCeIkdKXz/pub?gid=801787798&single=true&output=tsv'
    df = pd.read_csv(gsheet, sep='\t')[0:ngames]
    # make dates look like what python uses, so we can find game day
    # essentially just add 0 to 1 digit months
    df.loc[:, 'date'] = [x.strftime("%m/%d") for x in pd.to_datetime(df.date, format="%m/%d")]
    dayrow = df[df.date == match_date]

    return(dayrow)


def get_match_date(match_dow=3, week_offset=0):
    """
    game_roster parsed google sheet encodes day like mm/dd
    find the next game day in mm/dd format
    input is the day of the week we have a match
    """
    # when is our game (thursday=3)
    cur_dow = dt.datetime.now().weekday()
    days_to_match = match_dow-cur_dow if cur_dow <= match_dow else 7 - (cur_dow - match_dow)
    match_day_search_fmt = (dt.datetime.now() + dt.timedelta(days=days_to_match + 7*week_offset)).strftime("%m/%d")
    return(match_day_search_fmt)


def dayrow_extract(dayrow):
    """
    extract list of females (f), list of males (m), and total needed from dayrow
     - find the columns greater than 0, skip the first 6 columns
     - use that to get the number of players
    """
    ignr = 5  # zero-based count of non-yes/no player cols (to ignore)
    players = dayrow.columns[
                  [False]*ignr +
                  (dayrow.iloc[:, ignr:] > 0).values.tolist()[0]
              ]
    # gals match '♀' in name
    gals = [not re.search('♀', x) is None for x in players]
    m = players[[not x for x in gals]]
    f = [re.sub(' *♀', '', x) for x in players[gals]]

    # size like 8v8, extract the first char (8) and make an int
    need_n = int(dayrow['size'].values[0][0])
    return({'f': f, 'm': m, 'need_n': need_n})


def draw_names(v, offset=0, color='black', adj=0):
    text_offset = .1  # how far to shift text over
    x = 1  # all on the vert pos.
    for i, n in enumerate(v):
        plt.text(x-text_offset, i+.2+offset,
                 "%d. %s" % (i+1+offset-adj, n), color=color)


def plot_players(f, m, need_n):
    width = .3
    total = len(m) + len(f)  # == dayrow.TOTAL.values[0]
    # cut posible range into colors red (too few), yellow (enough), green (have subs)
    fcolor = pd.cut([len(f)], [-pd.np.Inf,1,2,pd.np.Inf],labels=['red','yellow','green'])[0]
    mcolor = pd.cut([len(m)], [-pd.np.Inf,need_n-max(2,len(f))-1,need_n,pd.np.Inf],labels=['red','yellow','green'])[0]
    fig = plt.figure()

    # gap between m and f
    f_offset = len(m) + 1

    # color histogram. give .2 extra so empty will show (as red)
    plt.bar(1, len(m)+.2, width, color=mcolor)
    plt.bar(1, len(f)+.2, width, f_offset, color=fcolor)
    # show 2 above how many we have
    plt.ylim([-.2, total+2])
    # only show one x position
    plt.xlim([.5, 1.5])
    plt.axis('off')
    # place enumerated names on the bar
    draw_names(m, 0, 'black', 0)
    draw_names(f, f_offset, 'black', 1)
    #
    title = "\n" +\
            r'$\frac{%d}{%d}$ = $\frac{%d}{2}$♀ + $\frac{%d}{%d}$♂ ' %\
            (total, need_n, len(f), len(m), need_n - max(2, len(f)))
    plt.title(title, fontsize=20)
    fig.suptitle("as of " + dt.datetime.now().strftime('%m/%d %H:%M'),
                 fontsize=10)
    return(fig)


def stream_plot(fig):
    fig.tight_layout()
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    return(imgdata.read())


def most_recent_image():
    """
    stdout buff wrie put it all together
    """
    match_date = get_match_date()
    dayrow = game_roster(match_date)
    fig = plot_players(**dayrow_extract(dayrow))
    return(stream_plot(fig))


if __name__ == "__main__":
    if(len(sys.argv) < 2):
        match_date = get_match_date()
    else:
        match_date = sys.argv[1]

    dayrow = game_roster(match_date)

    # error if we did not find exacltly one match
    if len(dayrow) != 1:
        print("did a bad job uniquely matching %s" % match_date)
        sys.exit(1)

    fig = plot_players(**dayrow_extract(dayrow))
    sys.stdout.buffer.write(stream_plot(fig))

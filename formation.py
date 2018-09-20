#!/usr/bin/env python3

# htps://pandas.pydata.org/pandas-docs/stable/comparison_with_r.html
#

import pandas as pd

from soccerimg import get_match_date, game_roster, dayrow_extract


# replace:
#  df.apply(lambda x:
#      x.assign(m=lambda e: max(e["col_to_max"]))).\
# with:
#  df.apply(mutate,'m',max,'col_to_max')
def mutate(x,new_col,fun,on_col):
    return(x.assign(**{new_col: lambda e: fun(e[on_col])}))

sheet="https://docs.google.com/spreadsheets/d/e/2PACX-1vS2gt8F7xEhaMt3kfMe6zRktkp9vn0A778zit3-jLXbr7TQudQxENjj1kvPvnZvt_A8NSbx0PVhByqc/pub?output=tsv"


# who is playing
players = dayrow_extract(game_roster(get_match_date()))
allplayers = players['f'] + players['m'].tolist()

# remove sub heading, remove empty rows (F==F if not NaN)
d=pd.read_table(sheet)[1:].\
  query("F==F") # remove nulls

# take dataframe from wide to long: row for each position prefnum combination
pos=d[["who","F","M","D","G","Rest/25"]].\
    melt(["who","Rest/25"],var_name="pos",value_name="prefnum").\
    assign(prefnum=lambda x: pd.to_numeric(x["prefnum"])).\
    assign(playing=lambda x: [w in allplayers for w in x.who]).\
    query("playing and prefnum>0").drop(columns=["playing"])


# formation specifies maxes:

# first past: who wants to be where the most
#  get everyone's max preference and pick that position 
#  break ties with sub time
wanted = \
    pos.groupby('who').\
    apply(mutate,'m',max,'prefnum').\
    query("m==prefnum").\
    sort_values(['prefnum','Rest/25'],ascending=False).\
    groupby('pos').\
    apply(mutate,'r',lambda x: pd.Series.rank(x,method='first'),'prefnum').\
    sort_values(['pos','r'],ascending=False).\
    assign(dup=lambda x: x.who.duplicated()).\
    query("not dup").\
    drop(columns=["dup"])
    # todo, add sex, keep min of 2 girls

# todo: make on-field and sub split

# remove all wanted from comparison 
# merge origial with most prefered, drop the most prefered rows
# (m!=m means m is NaN on that row -- row as not in wanted df)
second = pos.\
    merge(wanted[["who","pos","m"]],on=["who","pos"],how='outer').\
    query('m!=m').\
    drop(columns="m")
# todo: remove any positions already filled

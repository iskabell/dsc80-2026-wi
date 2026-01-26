# lab.py


import os
import io
from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def trick_me():
    tricky_1 = pd.DataFrame(
        [
            ['Alice', 'A', 20],
            ['Bob', 'B', 21],
            ['Cara', 'C', 22],
            ['Dan', 'D', 23],
            ['Eve', 'E', 24]
        ],
        columns=['Name', 'Name', 'Age']
    )

    tricky_1.to_csv('tricky_1.csv', index=False)
    tricky_2 = pd.read_csv('tricky_1.csv')

    return 3


def trick_bool():
    return [10, 10, 12]


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def population_stats(df):
    num_nonnull = df.count()
    prop_nonnull = df.count() / len(df)
    num_distinct = df.nunique()
    prop_distinct = df.nunique() / df.count()
    
    return pd.DataFrame({
        'num_nonnull': num_nonnull,
        'prop_nonnull': prop_nonnull,
        'num_distinct': num_distinct,
        'prop_distinct': prop_distinct
    })


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def most_common(df, N=10):
    result = pd.DataFrame(index=range(N))

    for col in df.columns:
        vc = df[col].value_counts()
        values = vc.index.to_series().iloc[:N].reset_index(drop=True)
        counts = vc.iloc[:N].reset_index(drop=True)
        values = values.reindex(range(N))
        counts = counts.reindex(range(N))
        result[f"{col}_values"] = values.values
        result[f"{col}_counts"] = counts.values

    return result


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def super_hero_powers(powers):
    powers = powers.set_index(powers.columns[0])
    most_powers_hero = powers.sum(axis=1).idxmax()
    flyers = powers[powers['Flight']]
    most_common_flyer_power = flyers.drop(columns='Flight').sum().idxmax()
    one_power_heroes = powers[powers.sum(axis=1) == 1]
    most_common_single_power = one_power_heroes.sum().idxmax()
    return [most_powers_hero, most_common_flyer_power, most_common_single_power]


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def clean_heroes(heroes):
    return heroes.replace(['-', -99], np.nan)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def super_hero_stats():
    return [
        'Onslaught',
        'George Lucas',
        'bad',
        'Marvel Comics',
        'NBC - Heroes',
        'Groot'
    ]

# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def clean_universities(df):
    out = df.copy()
    out['institution'] = out['institution'].str.replace('\n', ', ')
    out['broad_impact'] = out['broad_impact'].astype(int)
    split = out['national_rank'].str.split(',', expand=True)
    out['nation'] = split[0].str.strip().replace({
        'Czechia': 'Czech Republic',
        'UK': 'United Kingdom',
        'USA': 'United States'
    })
    out['national_rank_cleaned'] = split[1].astype(int)
    out = out.drop(columns='national_rank')
    out['is_public'] = out['control'].eq('Public').fillna(False)
    return out

def university_info(cleaned):
    s1 = (
        cleaned.groupby('state')
        .filter(lambda x: len(x) >= 3)
        .groupby('state')['score']
        .mean()
        .idxmin()
    )

    s2 = (
        cleaned[cleaned['world_rank'] <= 100]['quality_of_faculty']
        .le(100)
        .mean()
    )

    s3 = (
        cleaned.groupby('state')['is_public']
        .apply(lambda x: (~x).mean() >= 0.5)
        .sum()
    )

    s4 = (
        cleaned[cleaned['national_rank_cleaned'] == 1]
        .sort_values('world_rank', ascending=False)
        .iloc[0]['institution']
    )

    return [s1, s2, s3, s4]
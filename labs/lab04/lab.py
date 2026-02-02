# lab.py


import pandas as pd
import numpy as np
np.set_printoptions(legacy='1.21')
import io
from pathlib import Path
import os


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def prime_time_logins(login):
    times = pd.to_datetime(login['Time'])
    mask = (times.dt.hour >= 16) & (times.dt.hour < 20)
    counts = (
        login[mask]
        .groupby('Login Id')
        .size()
    )
    return (
        counts
        .reindex(login['Login Id'].unique(), fill_value=0)
        .to_frame(name='Time')
    )


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def logins_per_day(login):
    times = pd.to_datetime(login['Time'])
    now = pd.Timestamp('2026-01-31 23:59:00')
    return (
        login
        .assign(Time=times)
        .groupby('Login Id')
        .apply(lambda x: len(x) / max((now - x['Time'].min()).days, 1))
    )


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def cookies_null_hypothesis():
    return [1, 2]
                         
def cookies_p_value(N):
    sims = np.random.binomial(250, 0.04, size=N)
    return np.mean(sims >= 15)


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def car_null_hypothesis():
    return [1, 4]

def car_alt_hypothesis():
    return [2, 5]

def car_test_statistic():
    return [1, 4]

def car_p_value():
    return 4


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def superheroes_test_statistic():
    return [1]
    
def bhbe_col(heroes):
    return (
        heroes['Hair color'].str.contains('blond', case=False, na=False)
        & heroes['Eye color'].str.contains('blue', case=False, na=False)
    )

def superheroes_observed_statistic(heroes):
    bhbe = bhbe_col(heroes)
    return (heroes.loc[bhbe, 'Alignment'] == 'good').mean()

def simulate_bhbe_null(heroes, N):
    bhbe = bhbe_col(heroes).to_numpy()
    good = (heroes['Alignment'] == 'good').to_numpy()
    sims = np.random.permutation(np.tile(good, (N, 1)))
    return sims[:, bhbe].mean(axis=1)

def superheroes_p_value(heroes):
    sims = simulate_bhbe_null(heroes, 100000)
    obs = superheroes_observed_statistic(heroes)
    p = np.mean(sims >= obs)
    return [p, 'Reject' if p < 0.01 else 'Fail to reject']


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def diff_of_means(data, col='orange'):
    means = data.groupby('Factory')[col].mean()
    return abs(means['Yorkville'] - means['Waco'])


def simulate_null(data, col='orange'):
    shuffled = data.assign(
        Factory=np.random.permutation(data['Factory'])
    )
    return diff_of_means(shuffled, col)


def color_p_value(data, col='orange'):
    obs = diff_of_means(data, col)
    sims = np.array([simulate_null(data, col) for _ in range(1000)])
    return np.mean(sims >= obs)


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def ordered_colors():
    return [
        ('yellow', 0.000),
        ('orange', 0.042),
        ('red', 0.214),
        ('green', 0.467),
        ('purple', 0.965)
    ]


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def same_color_distribution():
    return (0.005, 'Reject')

# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def perm_vs_hyp():
    return ['P', 'H', 'H', 'H', 'P']
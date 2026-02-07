# lab.py


from pathlib import Path
import pandas as pd
import numpy as np
np.set_printoptions(legacy='1.21')
from scipy import stats


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def after_purchase():
    return ['MNAR', 'MD', 'MAR', 'MAR', 'MAR']


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def multiple_choice():
    return ['MAR', 'MNAR', 'MD', 'MNAR', 'MCAR']


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------



def first_round():
    return [0.158, 'NR']

def second_round():
    return [0.023, 'R', 'D']



# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def verify_child(heights):
    pvals = {}

    for col in heights.columns:
        if col.startswith('child_'):
            father_missing = heights.loc[heights[col].isna(), 'father'].dropna()
            father_present = heights.loc[heights[col].notna(), 'father'].dropna()
            _, pval = stats.ks_2samp(father_missing, father_present)
            pvals[col] = pval

    return pd.Series(pvals)


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def cond_single_imputation(new_heights):
    father_bins = pd.qcut(new_heights['father'], 4)

    imputed_child = new_heights['child'].fillna(
        new_heights.groupby(father_bins)['child'].transform('mean')
    )

    return imputed_child


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def quantitative_distribution(child, N):
    observed = child.dropna().values

    densities, bin_edges = np.histogram(observed, bins=10, density=True)

    bin_widths = np.diff(bin_edges)
    bin_probs = densities * bin_widths
    bin_probs = bin_probs / bin_probs.sum()

    imputed = []

    for _ in range(N):
        bin_idx = np.random.choice(len(bin_probs), p=bin_probs)

        low = bin_edges[bin_idx]
        high = bin_edges[bin_idx + 1]
        imputed.append(np.random.uniform(low, high))

    return np.array(imputed)


def impute_height_quant(child):
    num_missing = child.isna().sum()
    imputed_vals = quantitative_distribution(child, num_missing)
    filled = child.copy()
    filled.loc[filled.isna()] = imputed_vals
    return filled


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def answers():
    mc_answers = [1, 2, 2, 3]
    websites = [
        'https://www.wikipedia.org/robots.txt',
        'https://stackoverflow.com/robots.txt'
    ]
    return mc_answers, websites
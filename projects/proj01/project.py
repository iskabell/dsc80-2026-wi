# project.py


import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def get_assignment_names(grades):
    assignment_names = {}

    assignment_names['lab'] = sorted([
        col for col in grades.columns
        if col.startswith('lab') and ' - ' not in col
    ])

    assignment_names['project'] = sorted([
        col for col in grades.columns
        if col.startswith('project') and ' - ' not in col
    ])

    assignment_names['disc'] = sorted([
        col for col in grades.columns
        if col.startswith('disc') and ' - ' not in col
    ])

    assignment_names['checkpoint'] = sorted([
        col for col in grades.columns
        if col.startswith('checkpoint') and ' - ' not in col
    ])

    assignment_names['midterm'] = ['Midterm']
    assignment_names['final'] = ['Final']

    return assignment_names


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def projects_overall(grades):
    assignment_names = get_assignment_names(grades)
    projects = assignment_names['project']
    
    project_scores = []

    for project in projects:
        earned = grades[project].fillna(0)

        total_max = grades[f"{project} - Max Points"].iloc[0]

        fr_col = f"{project} - Free Response"
        fr_max_col = f"{project} - Free Response - Max Points"

        if fr_col in grades.columns:
            earned = earned + grades[fr_col].fillna(0)
            total_max = total_max + grades[fr_max_col].iloc[0]

        project_scores.append(earned / total_max)

    return sum(project_scores) / len(project_scores)


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def lateness_penalty(col):
    td = pd.to_timedelta(late_series)
    hours = td.dt.total_seconds() / 3600

    penalties = pd.Series(0.4, index=late_series.index)
    penalties[hours <= 336] = 0.7
    penalties[hours <= 168] = 0.9
    penalties[hours <= 2] = 1.0

    return penalties

# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def process_labs(grades):
    labs = get_assignment_names(grades)['lab']
    out = pd.DataFrame(index=grades.index)

    for lab in labs:
        score = grades[lab].fillna(0)
        max_pts = grades[f"{lab} - Max Points"].iloc[0]
        penalty = lateness_penalty(grades[f"{lab} - Lateness (H:M:S)"])

        out[lab] = (score / max_pts) * penalty

    return out


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def labs_overall(processed):
    sorted_labs = processed.apply(np.sort, axis=1, result_type='expand')
    return sorted_labs.iloc[:, 1:].mean(axis=1)

# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def total_points(grades):
    names = get_assignment_names(grades)

    labs_processed = process_labs(grades)
    lab_score = labs_overall(labs_processed)

    project_score = projects_overall(grades)

    checkpoints = names['checkpoint']
    if len(checkpoints) > 0:
        cp_scores = []
        for cp in checkpoints:
            earned = grades[cp].fillna(0)
            max_pts = grades[f"{cp} - Max Points"].iloc[0]
            cp_scores.append(earned / max_pts)
        checkpoint_score = sum(cp_scores) / len(cp_scores)
    else:
        checkpoint_score = 0

    discussions = names['disc']
    if len(discussions) > 0:
        disc_scores = []
        for disc in discussions:
            earned = grades[disc].fillna(0)
            max_pts = grades[f"{disc} - Max Points"].iloc[0]
            disc_scores.append(earned / max_pts)
        discussion_score = sum(disc_scores) / len(disc_scores)
    else:
        discussion_score = 0

    midterm = grades['Midterm'].fillna(0)
    midterm_max = grades['Midterm - Max Points'].iloc[0]
    midterm_score = midterm / midterm_max

    final = grades['Final'].fillna(0)
    final_max = grades['Final - Max Points'].iloc[0]
    final_score = final / final_max
\
    total = (
        0.20 * lab_score +
        0.30 * project_score +
        0.025 * checkpoint_score +
        0.025 * discussion_score +
        0.15 * midterm_score +
        0.30 * final_score
    )

    return total


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def final_grades(total):
    return pd.cut(
        scores,
        bins=[-np.inf, 0.6, 0.7, 0.8, 0.9, np.inf],
        labels=['F', 'D', 'C', 'B', 'A'],
        right=False
    )
def letter_proportions(total):
    letters = final_grades(final_scores)
    proportions = letters.value_counts(normalize=True)
    order = ['B', 'C', 'A', 'D', 'F']
    
    return proportions.reindex(order).dropna()


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def raw_redemption(final_breakdown, question_numbers):
    ...
    
def combine_grades(grades, raw_redemption_scores):
    ...


# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def z_score(ser):
    ...
    
def add_post_redemption(grades_combined):
    ...


# ---------------------------------------------------------------------
# QUESTION 10
# ---------------------------------------------------------------------


def total_points_post_redemption(grades_combined):
    ...
        
def proportion_improved(grades_combined):
    ...


# ---------------------------------------------------------------------
# QUESTION 11
# ---------------------------------------------------------------------


def section_most_improved(grades_analysis):
    ...
    
def top_sections(grades_analysis, t, n):
    ...


# ---------------------------------------------------------------------
# QUESTION 12
# ---------------------------------------------------------------------


def rank_by_section(grades_analysis):
    ...


# ---------------------------------------------------------------------
# QUESTION 13
# ---------------------------------------------------------------------


def letter_grade_heat_map(grades_analysis):
    ...

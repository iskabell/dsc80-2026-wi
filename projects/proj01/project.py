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
    td = pd.to_timedelta(col)
    hours = td.dt.total_seconds() / 3600

    penalties = pd.Series(0.4, index=col.index)
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
        total,
        bins=[-np.inf, 0.6, 0.7, 0.8, 0.9, np.inf],
        labels=['F', 'D', 'C', 'B', 'A'],
        right=False
    )
def letter_proportions(total):
    letters = final_grades(total)
    proportions = letters.value_counts(normalize=True)
    order = ['B', 'C', 'A', 'D', 'F']
    return proportions.reindex(order).fillna(0)


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def raw_redemption(final_breakdown, question_numbers):
    scores = final_breakdown.iloc[:, question_numbers]
    max_scores = scores.max()
    earned = scores.sum(axis=1)
    possible = max_scores.sum()
    raw = earned / possible
    raw = raw.fillna(0)
    return pd.DataFrame({
        'PID': final_breakdown['PID'],
        'Raw Redemption Score': raw
    })
    
def combine_grades(grades, raw_redemption_scores):
    return grades.merge(raw_redemption_scores, on='PID', how='left').fillna({'Raw Redemption Score': 0})

# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def z_score(ser):
    return (ser - ser.mean()) / ser.std(ddof=0)
    
def add_post_redemption(grades_combined):
    out = grades_combined.copy()

    mid_col = out.filter(like='Midterm').columns[0]
    mid = out[mid_col].fillna(0)

    mid_z = z_score(mid)
    red_z = z_score(out['Raw Redemption Score'])

    mean_mid = mid.mean()
    std_mid = mid.std(ddof=0)

    redeemed = red_z * std_mid + mean_mid

    post = mid.where(red_z <= mid_z, redeemed)
    post = post.clip(0, 1)

    out['Midterm Score Pre-Redemption'] = mid
    out['Midterm Score Post-Redemption'] = post

    return out


# ---------------------------------------------------------------------
# QUESTION 10
# ---------------------------------------------------------------------


def total_points_post_redemption(grades_combined):
    df = add_post_redemption(grades_combined)
    base = total_points(df)
    return base - 0.15 * df['Midterm Score Pre-Redemption'] + 0.15 * df['Midterm Score Post-Redemption']
        
def proportion_improved(grades_combined):
    pre = final_grades(total_points(grades_combined))
    post = final_grades(total_points_post_redemption(grades_combined))

    improved = post.cat.codes > pre.cat.codes
    return improved.mean()


# ---------------------------------------------------------------------
# QUESTION 11
# ---------------------------------------------------------------------


def section_most_improved(grades_analysis):
    order = {'F': 0, 'D': 1, 'C': 2, 'B': 3, 'A': 4}

    pre = grades_analysis['Letter Grade Pre-Redemption'].astype(str).map(order)
    post = grades_analysis['Letter Grade Post-Redemption'].astype(str).map(order)

    improved = post > pre

    proportions = (
        grades_analysis
        .assign(Improved=improved)
        .groupby('Section')['Improved']
        .mean()
    )

    return proportions.idxmax()
    
def top_sections(grades_analysis, t, n):
    final_prop = (
        grades_analysis['Final'] /
        grades_analysis['Final - Max Points']
    )

    qualifying = grades_analysis.assign(FinalProp=final_prop)

    counts = (
        qualifying[qualifying['FinalProp'] >= t]
        .groupby('Section')
        .size()
    )

    return np.array(sorted(counts[counts >= n].index))


# ---------------------------------------------------------------------
# QUESTION 12
# ---------------------------------------------------------------------


def rank_by_section(grades_analysis):
    sorted_df = grades_analysis.sort_values(
        by=['Section', 'Total Points Post-Redemption', 'PID'],
        ascending=[True, False, True]
    )

    sorted_df['Rank'] = sorted_df.groupby('Section').cumcount() + 1

    result = sorted_df.pivot(
        index='Rank',
        columns='Section',
        values='PID'
    )

    max_n = grades_analysis['Section'].value_counts().max()
    result = result.reindex(range(1, max_n + 1))

    sections = sorted(grades_analysis['Section'].unique())
    result = result.reindex(columns=sections)

    return result.fillna('')


# ---------------------------------------------------------------------
# QUESTION 13
# ---------------------------------------------------------------------


def letter_grade_heat_map(grades_analysis):
    order_grades = ['A', 'B', 'C', 'D', 'F']
    sections = sorted(grades_analysis['Section'].unique())

    counts = (
        grades_analysis
        .groupby(['Section', 'Letter Grade Post-Redemption'])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=order_grades, fill_value=0)
    )

    proportions = counts.div(counts.sum(axis=1), axis=0)
    heat_df = proportions.T.reindex(index=order_grades, columns=sections)

    fig = px.imshow(
        heat_df,
        color_continuous_scale='Viridis',
        title='Distribution of Letter Grades by Section'
    )

    fig.update_layout(
        font=dict(
            family='Impact',
            size=14
        )
    )

    return fig
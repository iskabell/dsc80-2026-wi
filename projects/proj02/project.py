# project.py


import pandas as pd
import numpy as np
np.set_printoptions(threshold=20, suppress=True, legacy='1.21')

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pd.options.plotting.backend = 'plotly'

from IPython.display import display

# DSC 80 preferred styles
pio.templates["dsc80"] = go.layout.Template(
    layout=dict(
        margin=dict(l=30, r=30, t=30, b=30),
        autosize=True,
        width=600,
        height=400,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        title=dict(x=0.5, xanchor="center"),
    )
)
pio.templates.default = "simple_white+dsc80"
import warnings
warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def clean_loans(loans):
    loans = loans.copy()
    loans['emp_title'] = loans['emp_title'].str.lower().str.strip()
    loans.loc[loans['emp_title'] == 'rn', 'emp_title'] = 'registered nurse'
    loans['issue_d'] = pd.to_datetime(loans['issue_d'])
    loans['term'] = loans['term'].str.extract(r'(\d+)').astype(int)
    loans['term_end'] = loans.apply(
        lambda row: row['issue_d'] + pd.DateOffset(months=row['term']),
        axis=1
    )
    return loans


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def correlations(df, pairs):
    values = []
    index = []
    for col1, col2 in pairs:
        values.append(df[col1].corr(df[col2]))
        index.append(f"r_{col1}_{col2}")
    return pd.Series(values, index=index)


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def create_boxplot(loans):
    df = loans.copy()
    bins = [580, 670, 740, 800, 850]
    labels = ["[580, 670)", "[670, 740)", "[740, 800)", "[800, 850)"]
    
    df['credit_bin'] = pd.cut(
        df['fico_range_low'],
        bins=bins,
        right=False,
        labels=labels
    ).astype(str)

    fig = px.box(
        df,
        x='credit_bin',
        y='int_rate',
        color='term',
        labels={
            'credit_bin': 'Credit Score Range',
            'int_rate': 'Interest Rate (%)',
            'term': 'Loan Length (Months)'
        },
        title='Interest Rate vs. Credit Score',
        color_discrete_map={
            36: 'purple',
            60: 'gold'
        }
    )
    return fig


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def ps_test(loans, N):
    df = loans.copy()
    has_ps = df['desc'].notna()
    observed = (
        df.loc[has_ps, 'int_rate'].mean()
        - df.loc[~has_ps, 'int_rate'].mean()
    )

    diffs = []
    rates = df['int_rate'].values
    labels = has_ps.values

    for _ in range(N):
        shuffled = np.random.permutation(labels)
        diffs.append(
            rates[shuffled].mean() - rates[~shuffled].mean()
        )
    diffs = np.array(diffs)
    return (diffs >= observed).mean()
    
def missingness_mechanism():
    return 2
    
def other_missingness():
    return 1


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def tax_owed(income, brackets):
    tax = 0
    for i in range(len(brackets)):
        rate, lower = brackets[i]
        if i + 1 < len(brackets):
            upper = brackets[i + 1][1]
            taxable = min(max(income - lower, 0), upper - lower)
        else:
            taxable = max(income - lower, 0)
        tax += rate * taxable
    return tax


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def clean_state_taxes(state_taxes_raw): 
    df = state_taxes_raw.copy()
    df = df.dropna(how='all')

    df['State'] = df['State'].where(~df['State'].astype(str).str.startswith('('))
    df['State'] = df['State'].ffill()

    df['Rate'] = (
        pd.to_numeric(
            df['Rate'].astype(str).str.replace('%', '', regex=False),
            errors='coerce'
        )
        .div(100)
        .apply(lambda x: round(x, 2) if pd.notna(x) else x)
        .fillna(0)
    )

    df['Lower Limit'] = (
        pd.to_numeric(
            df['Lower Limit'].astype(str).str.replace(',', '', regex=False),
            errors='coerce'
        )
        .fillna(0)
        .astype(int)
    )
    return df[['State', 'Rate', 'Lower Limit']]



# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def state_brackets(state_taxes):
    return (
        state_taxes
        .sort_values('Lower Limit')
        .groupby('State')
        .apply(lambda df: list(zip(df['Rate'], df['Lower Limit'])))
        .to_frame(name='bracket_list')
    )
    
def combine_loans_and_state_taxes(loans, state_taxes):
    # Start by loading in the JSON file.
    # state_mapping is a dictionary; use it!
    import json
    state_mapping_path = Path('data') / 'state_mapping.json'
    with open(state_mapping_path, 'r') as f:
        state_mapping = json.load(f)
        
    # Now it's your turn:
    brackets = state_brackets(state_taxes)
    mapping_df = (
        pd.Series(state_mapping)
        .rename_axis('abbr')
        .reset_index(name='full_name')
    )
    brackets = (
        brackets
        .reset_index()
        .merge(mapping_df, left_on='State', right_on='full_name')
        .drop(columns=['State', 'full_name'])
        .rename(columns={'abbr': 'State'})
        .set_index('State')
    )
    return (
        loans
        .rename(columns={'addr_state': 'State'})
        .merge(brackets, left_on='State', right_index=True, how='left')
    )


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def find_disposable_income(loans_with_state_taxes):
    FEDERAL_BRACKETS = [
     (0.1, 0), 
     (0.12, 11000), 
     (0.22, 44725), 
     (0.24, 95375), 
     (0.32, 182100),
     (0.35, 231251),
     (0.37, 578125)
    ]
    df = loans_with_state_taxes.copy()
    df['federal_tax_owed'] = df['annual_inc'].apply(
        lambda x: tax_owed(x, FEDERAL_BRACKETS)
    )
    df['state_tax_owed'] = df.apply(
        lambda row: tax_owed(
            row['annual_inc'],
            row['bracket_list'] if isinstance(row['bracket_list'], list) else [(0, 0)]
        ),
        axis=1
    )
    df['disposable_income'] = (
        df['annual_inc']
        - df['federal_tax_owed']
        - df['state_tax_owed']
    )
    return df


# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def aggregate_and_combine(loans, keywords, quantitative_column, categorical_column):
    dfs = []
    for keyword in keywords:
        mask = loans['emp_title'].str.contains(keyword, na=False)
        by_group = (
            loans[mask]
            .groupby(categorical_column)[quantitative_column]
            .mean()
            .to_frame(name=f'{keyword}_mean_{quantitative_column}')
        )
        overall = (
            loans.loc[mask, quantitative_column]
            .mean()
        )
        by_group.loc['Overall'] = overall
        dfs.append(by_group)

    result = pd.concat(dfs, axis=1)
    if 'Overall' in result.index:
        idx = [i for i in result.index if i != 'Overall'] + ['Overall']
        result = result.loc[idx]
    return result


# ---------------------------------------------------------------------
# QUESTION 10
# ---------------------------------------------------------------------


def exists_paradox(loans, keywords, quantitative_column, categorical_column):
    df = aggregate_and_combine(loans, keywords, quantitative_column, categorical_column)
    a, b = df.columns

    grouped = df.iloc[:-1].dropna()
    overall = df.iloc[-1]

    return bool(
        ((grouped[a] > grouped[b]).all() and overall[a] < overall[b]) or
        ((grouped[a] < grouped[b]).all() and overall[a] > overall[b])
    )
    
def paradox_example(loans):
    return {
        'loans': loans,
        'keywords': ['engineer', 'nurse'],
        'quantitative_column': 'loan_amnt',
        'categorical_column': 'home_ownership'
    }
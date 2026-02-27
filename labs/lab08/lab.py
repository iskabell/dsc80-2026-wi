# lab.py


import pandas as pd
import numpy as np
np.set_printoptions(legacy='1.21')
import itertools
import plotly.express as px
import statsmodels.api as sm
from pathlib import Path
from sklearn.preprocessing import Binarizer, QuantileTransformer, FunctionTransformer

import warnings
warnings.filterwarnings('ignore')


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def best_transformation():
    homeruns_fp = Path('data')/'homeruns.csv'
    homeruns = pd.read_csv(homeruns_fp)
    df = homeruns
    
    y = df['Home Runs']
    X = sm.add_constant(df['Year'])
    
    r2_1 = sm.OLS(np.sqrt(y), X).fit().rsquared
    r2_2 = sm.OLS(1 / y, X).fit().rsquared
    r2_3 = sm.OLS(np.log(y), X).fit().rsquared
    r2_4 = sm.OLS(y ** 2, X).fit().rsquared
    
    r2_values = [r2_1, r2_2, r2_3, r2_4]
    
    return np.argmax(r2_values) + 1


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------



def create_ordinal(df):
    cut_order = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
    color_order = ['J', 'I', 'H', 'G', 'F', 'E', 'D']
    clarity_order = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']
    
    cut_map = {v: i for i, v in enumerate(cut_order)}
    color_map = {v: i for i, v in enumerate(color_order)}
    clarity_map = {v: i for i, v in enumerate(clarity_order)}
    
    return pd.DataFrame({
        'ordinal_cut': df['cut'].map(cut_map),
        'ordinal_color': df['color'].map(color_map),
        'ordinal_clarity': df['clarity'].map(clarity_map)
    })


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------



def create_one_hot(df):
    categorical_cols = ['cut', 'color', 'clarity']
    result = pd.DataFrame(index=df.index)
    
    for col in categorical_cols:
        for val in df[col].unique():
            result[f'one_hot_{col}_{val}'] = (df[col] == val).astype(int)
    
    return result


def create_proportions(df):
    categorical_cols = ['cut', 'color', 'clarity']
    result = pd.DataFrame(index=df.index)
    
    for col in categorical_cols:
        proportions = df[col].value_counts(normalize=True)
        result[f'proportion_{col}'] = df[col].map(proportions)
    
    return result


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def create_quadratics(df):
    quantitative_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    quantitative_cols.remove('price')
    
    result = pd.DataFrame(index=df.index)
    
    for col1, col2 in itertools.combinations(quantitative_cols, 2):
        result[f'{col1} * {col2}'] = df[col1] * df[col2]
    
    return result


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------



def comparing_performance():
    return [
        0.8493305264354858,
        1548.5331930613174,
        'x',
        'carat * x',
        'ordinal_color',
        1434.8400089047332
    ]


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


class TransformDiamonds(object):
    
    def __init__(self, diamonds):
        self.data = diamonds
        
    # Question 6.1
    def transform_carat(self, data):
        b = Binarizer(threshold=1)
        return b.fit_transform(data[['carat']])
    
    # Question 6.2
    def transform_to_quantile(self, data):
        qt = QuantileTransformer(n_quantiles=100)
        qt.fit(self.data[['carat']])
        return qt.transform(data[['carat']])
    
    # Question 6.3
    def transform_to_depth_pct(self, data):
        def depth_pct(arr):
            x = arr[:, 0]
            y = arr[:, 1]
            z = arr[:, 2]
            return 100 * (2 * z / (x + y))
        ft = FunctionTransformer(depth_pct)
        return ft.transform(data[['x', 'y', 'z']].values)
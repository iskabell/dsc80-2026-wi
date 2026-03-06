# lab.py


import pandas as pd
import numpy as np
np.set_printoptions(legacy='1.21')
from pathlib import Path
import plotly.express as px

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def simple_pipeline(data):
    def simple_pipeline(data):
    X = data[['c2']]
    y = data['y']
    
    pipe = Pipeline([
        ('log', FunctionTransformer(np.log)),
        ('lr', LinearRegression())
    ])
    
    pipe.fit(X, y)
    preds = pipe.predict(X)
    
    return pipe, preds


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def multi_type_pipeline(data):
    X = data[['group', 'c1', 'c2']]
    y = data['y']

    preprocessor = ColumnTransformer([
        ('c1_pass', 'passthrough', ['c1']),
        ('c2_log', FunctionTransformer(np.log), ['c2']),
        ('group_ohe', OneHotEncoder(sparse_output=False), ['group'])
    ])

    pipe = Pipeline([
        ('preprocess', preprocessor),
        ('model', LinearRegression())
    ])

    pipe.fit(X, y)
    preds = pipe.predict(X)

    return pipe, preds


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


# Imports
from sklearn.base import BaseEstimator, TransformerMixin

class StdScalerByGroup(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        # X might not be a pandas DataFrame (e.g. a numpy array)
        df = pd.DataFrame(X)
        grp_col = df.columns[0]
        num_cols = df.columns[1:]
        
        stats = df.groupby(grp_col)[num_cols].agg(['mean', 'std'])

        # Store the means and SDs for each column (e.g. 'c1' and 'c2'), 
        # for each group (e.g. 'A', 'B', 'C').  
        self.grps_ = {}
        for g in stats.index:
            self.grps_[g] = {}
            for col in num_cols:
                self.grps_[g][col] = {
                    'mean': stats.loc[g, (col, 'mean')],
                    'std': stats.loc[g, (col, 'std')]
                }

        return self

    def transform(self, X, y=None):
        # X might not be a pandas DataFrame (e.g. a numpy array)
        df = pd.DataFrame(X)

        try:
            getattr(self, "grps_")
        except AttributeError:
            raise RuntimeError("You must fit the transformer before transforming the data!")
        
        # Hint: Define a helper function here!
        grp_col = df.columns[0]
        num_cols = df.columns[1:]

        result = pd.DataFrame()

        for col in num_cols:
            result[col] = df.apply(
                lambda row: (
                    row[col] - self.grps_[row[grp_col]][col]['mean']
                ) / self.grps_[row[grp_col]][col]['std'],
                axis=1
            )
            
        return result


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------

from sklearn.metrics import mean_squared_error, r2_score

def eval_toy_model():
    data = pd.read_csv(Path("data") / "toy.csv")

    y = data['y']
    results = []

    pl1, preds1 = simple_pipeline(data)
    rmse1 = mean_squared_error(y, preds1, squared=False)
    r21 = r2_score(y, preds1)
    results.append((rmse1, r21))

    pl2, preds2 = multi_type_pipeline(data)
    rmse2 = mean_squared_error(y, preds2, squared=False)
    r22 = r2_score(y, preds2)
    results.append((rmse2, r22))

    X = data[['group','c1','c2']]

    pre = ColumnTransformer([
        ('grp_std', StdScalerByGroup(), ['group','c1','c2']),
        ('log_c2', FunctionTransformer(np.log), ['c2']),
        ('group_ohe', OneHotEncoder(sparse_output=False), ['group'])
    ])

    pipe3 = Pipeline([
        ('preprocess', pre),
        ('model', LinearRegression())
    ])

    pipe3.fit(X, y)
    preds3 = pipe3.predict(X)

    rmse3 = mean_squared_error(y, preds3, squared=False)
    r23 = r2_score(y, preds3)

    results.append((rmse3, r23))

    return results


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------



def tree_reg_perf(galton):
    # Add your imports here
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.metrics import mean_squared_error

    X = galton.drop(columns=['childHeight'])
    y = galton['childHeight']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0
    )

    train_err = []
    test_err = []

    for depth in range(1, 21):

        model = DecisionTreeRegressor(max_depth=depth, random_state=0)
        model.fit(X_train, y_train)

        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        train_err.append(mean_squared_error(y_train, train_pred))
        test_err.append(mean_squared_error(y_test, test_pred))

    return pd.DataFrame(
        {'train_err': train_err, 'test_err': test_err},
        index=range(1, 21)
    )

def knn_reg_perf(galton):
    # Add your imports here
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.metrics import mean_squared_error

    X = galton.drop(columns=['childHeight'])
    y = galton['childHeight']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0
    )

    train_err = []
    test_err = []

    for k in range(1, 21):

        model = KNeighborsRegressor(n_neighbors=k)
        model.fit(X_train, y_train)

        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        train_err.append(mean_squared_error(y_train, train_pred))
        test_err.append(mean_squared_error(y_test, test_pred))

    return pd.DataFrame(
        {'train_err': train_err, 'test_err': test_err},
        index=range(1, 21)
    )
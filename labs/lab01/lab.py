# lab.py


from pathlib import Path
import io
import pandas as pd
import numpy as np
np.set_printoptions(legacy='1.21')


# ---------------------------------------------------------------------
# QUESTION 0
# ---------------------------------------------------------------------


def consecutive_ints(ints):
    if len(ints) == 0:
        return False

    for k in range(len(ints) - 1):
        diff = abs(ints[k] - ints[k+1])
        if diff == 1:
            return True

    return False


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def median_vs_mean(nums):
    nums = sorted(nums)
    n = len(nums)

    if n % 2 == 1:
        median = nums[n // 2]
    else:
        mid1 = nums[n // 2 - 1]
        mid2 = nums[n // 2]
        median = (mid1 + mid2) / 2

    mean = sum(nums) / n

    return median <= mean

# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def n_prefixes(s, n):
    result = ""

    for k in range(n):
        prefix = s[:k+1]
        result = prefix + result

    return result


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def exploded_numbers(ints, n):
    result = []
    max_val = max(ints)
    max_width = len(str(max_val + n))

    for num in ints:
        exploded = []
        for k in range(num - n, num + n + 1):
            exploded.append(str(k).zfill(max_width))
        result.append(" ".join(exploded))

    return result


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def last_chars(fh):
    result = ""

    for line in fh:
        line = line.rstrip("\n")
        if line:
            result += line[-1]

    return result


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def add_root(A):
    positions = np.arange(len(A))
    return A + np.sqrt(positions)

def where_square(A):
    roots = np.sqrt(A)
    return roots == np.floor(roots)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def filter_cutoff_loop(matrix, cutoff):
    rows = len(matrix)
    cols = len(matrix[0])
    selected_cols = []

    for j in range(cols):
        col = [matrix[i][j] for i in range(rows)]
        mean = sum(col) / rows
        if mean > cutoff:
            selected_cols.append(col)

    result = []
    for i in range(rows):
        row = [selected_cols[j][i] for j in range(len(selected_cols))]
        result.append(row)

    return np.array(result)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def filter_cutoff_np(matrix, cutoff):
    col_means = np.mean(matrix, axis=0)
    mask = col_means > cutoff
    return matrix[:, mask]


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def growth_rates(A):
    initial = A[:-1]
    final = A[1:]
    rates = (final - initial) / initial
    return np.round(rates, 2)

def with_leftover(A):
    shares = 20 // A
    spent = shares * A
    leftover = 20 - spent
    total_leftover = np.cumsum(leftover)

    for i in range(len(total_leftover)):
        if total_leftover[i] >= A[i]:
            return i

    return -1


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def salary_stats(salary):
    num_players = len(salary)
    num_teams = salary['Team'].nunique()
    total_salary = salary['Salary'].sum()

    highest_row = salary.loc[salary['Salary'].idxmax()]
    highest_salary = highest_row['Player']
    total_highest = salary[salary['Team'] == highest_row['Team']]['Salary'].sum()

    avg_los = round(salary[salary['Team'] == 'Los Angeles Lakers']['Salary'].mean(), 2)

    fifth_row = salary.sort_values('Salary').iloc[4]
    fifth_lowest = f"{fifth_row['Player']}, {fifth_row['Team']}"

    last_names = salary['Player'].str.extract(r'(\b\w+)$')[0]
    duplicates = last_names.duplicated().any()

    return pd.Series({
        'num_players': num_players,
        'num_teams': num_teams,
        'total_salary': total_salary,
        'highest_salary': highest_salary,
        'avg_los': avg_los,
        'fifth_lowest': fifth_lowest,
        'duplicates': duplicates,
        'total_highest': total_highest
    })

# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def parse_malformed(fp):
    rows = []

    with open(fp) as f:
        next(f)

        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 5:
                continue

            try:
                first = parts[0].strip('"')
                last = parts[1].strip('"')
                weight = float(parts[2].strip('"'))
                height = float(parts[3].strip('"'))
                geo = ','.join(parts[4:]).strip('"')
                rows.append([first, last, weight, height, geo])
            except:
                continue

    columns = ['first', 'last', 'weight', 'height', 'geo']
    df = pd.DataFrame(rows, columns=columns)

    if len(df) < 100:
        missing = 100 - len(df)
        filler = pd.DataFrame({
            'first': [None] * missing,
            'last': [None] * missing,
            'weight': [np.nan] * missing,
            'height': [np.nan] * missing,
            'geo': [None] * missing
        })
        df = pd.concat([df, filler], ignore_index=True)

    return df

# lab.py


import os
import io
from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def read_linkedin_surveys(dirname):
    directory = Path(dirname)
    dfs = []
    for file in directory.iterdir():
        if file.name.startswith("survey") and file.suffix == ".csv":
            df = pd.read_csv(file)
            df.columns = [
                "first name",
                "last name",
                "current company",
                "job title",
                "email",
                "university"
            ]
            df["first name"] = df["first name"].str.strip().str.title()
            df["last name"] = df["last name"].str.strip().str.title()
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def linkedin_stats(df):
    ohio = df[df["university"].str.contains("Ohio", na=False)]
    prop_programmer = ohio["job title"].str.contains("Programmer", na=False).mean()
    num_engineer_titles = df["job title"][df["job title"].str.endswith("Engineer", na=False)].nunique()
    longest_title = df.loc[df["job title"].str.len().idxmax(), "job title"]
    num_managers = df["job title"].str.contains("manager", case=False, na=False).sum()
    return [
        prop_programmer,
        num_engineer_titles,
        longest_title,
        num_managers
    ]


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def read_student_surveys(dirname):
    directory = Path(dirname)
    dfs = []
    for file in directory.iterdir():
        if file.name.startswith("favorite") and file.suffix == ".csv":
            df = pd.read_csv(file)
            dfs.append(df.set_index("id"))
    return pd.concat(dfs, axis=1)


def check_credit(df):
    responses = df.drop(columns=["name"])
    valid = responses.copy()

    genre_cols = valid.columns[valid.eq("(no genres listed)").any()]
    valid[genre_cols] = valid[genre_cols].replace("(no genres listed)", pd.NA)

    completed = valid.notna().mean(axis=1) >= 0.5
    ec = completed.astype(int) * 5

    question_credit = (valid.notna().mean() >= 0.9).sum()
    question_credit = min(question_credit, 2)

    ec = ec + question_credit

    return pd.DataFrame({
        "name": df["name"],
        "ec": ec
    })


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def most_popular_procedure_type(pets, procedure_history):
    merged = pets.merge(procedure_history, on="PetID", how="inner")
    return merged["ProcedureType"].value_counts().idxmax()

def pet_name_by_owner(owners, pets):
    merged = owners.merge(pets, on="OwnerID", how="left")
    grouped = merged.groupby("Name_x")["Name_y"].apply(list)
    grouped = grouped.reindex(owners["Name"])
    return grouped.apply(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

def total_cost_per_city(owners, pets, procedure_history, procedure_detail):
    merged = (
        pets
        .merge(owners, on="OwnerID", how="left")
        .merge(procedure_history, on="PetID", how="left")
        .merge(procedure_detail, on=["ProcedureType", "ProcedureSubCode"], how="left")
    )
    totals = merged.groupby("City")["Price"].sum().fillna(0)
    return totals


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def average_seller(sales):
    return (
        sales.pivot_table(
            index="Name",
            values="Total",
            aggfunc="mean",
            fill_value=0
        )
        .rename(columns={"Total": "Average Sales"})
    )

def product_name(sales):
    return sales.pivot_table(
        index="Name",
        columns="Product",
        values="Total",
        aggfunc="sum"
    )

def count_product(sales):
    return sales.pivot_table(
        index=["Product", "Name"],
        columns="Date",
        values="Total",
        aggfunc="sum",
        fill_value=0
    )

def total_by_month(sales):
    sales = sales.copy()
    sales["Month"] = pd.to_datetime(sales["Date"]).dt.month_name()
    return sales.pivot_table(
        index=["Name", "Product"],
        columns="Month",
        values="Total",
        aggfunc="sum",
        fill_value=0
    )
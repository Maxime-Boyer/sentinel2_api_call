"""Collection of functions to convert JSON files to dataframes.

Each json format must be worked out here.

Created by agarc the 4/23/2024.
"""
import json

import pandas as pd


def _load_json(filename: str) -> dict:
    """Open a JSON file and return its content as a dictionary"""
    # Opening JSON file
    f = open(filename)  # noqa: SIM115

    # returns JSON object as a dictionary
    data = json.load(f)

    # Closing file
    f.close()

    return data


def _explode_rows(
    df: pd.DataFrame, row_name: str, attribute_name: str = None
) -> pd.DataFrame:
    """Explode rows in a dataframe"""
    rows = df[df["index"] == row_name]
    exploded = rows.explode("data")

    if attribute_name:
        exploded["data"] = exploded["data"].apply(lambda x: x[attribute_name])

    dg = df.drop(df[df["index"] == row_name].index)
    dg = pd.concat([dg, exploded], ignore_index=True)

    return dg


def cdc_json_to_df(filename: str) -> pd.DataFrame:
    """Reads the CDC JSON output and returns a dataframe"""
    data = _load_json(filename)
    cdc_df = pd.json_normalize(data).T.reset_index()
    cdc_df.columns = ["index", "data"]

    cdc_df = _explode_rows(cdc_df, row_name="types_de_profils", attribute_name="type")
    cdc_df = _explode_rows(
        cdc_df,
        row_name="taches_et_responsabilites",
        attribute_name="tache_et_responsabilite",
    )
    cdc_df = _explode_rows(
        cdc_df, row_name="competences_du_profils", attribute_name="competence"
    )

    cdc_df["categorie"] = "CDC"
    cdc_df = cdc_df[["categorie", "index", "data"]]

    return cdc_df


def rec_json_to_df(filename: str) -> pd.DataFrame:
    """Reads the REC JSON output and returns a dataframe"""
    data = _load_json(filename)
    rec_df = pd.json_normalize(data).T.reset_index()
    rec_df.columns = ["index", "data"]

    rec_df = _explode_rows(rec_df, row_name="types_de_profils", attribute_name="type")
    rec_df = _explode_rows(
        rec_df, row_name="types_de_profils_variante", attribute_name="type"
    )
    rec_df = _explode_rows(rec_df, row_name="offre_technique", attribute_name="element")
    rec_df = _explode_rows(
        rec_df,
        row_name="sous_criteres_techniques_et_ponderation",
        attribute_name="critere",
    )
    rec_df["categorie"] = "REC"
    rec_df = rec_df[["categorie", "index", "data"]]

    return rec_df


def cv_json_single_file_to_df(
    filename: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reads the CV JSON output and returns a dataframe"""
    data = _load_json(filename)

    # experience
    cv_exp_df = pd.DataFrame(columns=["categorie", "index", "data"])
    for xp in data["experiences_entreprise"]:
        tmp_df = pd.json_normalize(xp).T.reset_index()
        tmp_df.columns = ["index", "data"]

        categorie_name = tmp_df[tmp_df["index"] == "nom_entreprise"]["data"][0][0]
        tmp_df["categorie"] = categorie_name

        cv_exp_df = pd.concat([cv_exp_df, tmp_df], ignore_index=True)

    # tasks
    cv_taches_df = pd.DataFrame(columns=["categorie", "index", "data"])
    for xp in data["experiences_entreprise"]:
        tmp_df = pd.json_normalize(xp).T.reset_index()
        tmp_df.columns = ["index", "data"]

        tmp_dg = tmp_df[tmp_df["index"] == "role"].explode(column="data")
        tmp_df = tmp_df.drop(tmp_df[tmp_df["index"] == "role"].index)
        tmp_df = pd.concat([tmp_df, tmp_dg], ignore_index=True)

        categorie_name = tmp_df[tmp_df["index"] == "nom_entreprise"]["data"][0][0]
        tmp_df["categorie"] = categorie_name

        cv_taches_df = pd.concat([cv_taches_df, tmp_df], ignore_index=True)

    # degrees
    cv_diplomes_df = pd.json_normalize(data).T.reset_index()
    cv_diplomes_df.columns = ["index", "data"]

    cv_diplomes_df = cv_diplomes_df.explode(column="data")
    cv_diplomes_df["categorie"] = "Divers (diplomes, ...)"
    cv_diplomes_df = cv_diplomes_df[["categorie", "index", "data"]]
    cv_diplomes_df = cv_diplomes_df[cv_diplomes_df["index"] != "experiences_entreprise"]

    return cv_exp_df, cv_taches_df, cv_diplomes_df

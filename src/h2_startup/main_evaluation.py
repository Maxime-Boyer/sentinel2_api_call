import json
import os
import time
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from h2_startup.modules.technical_notation.single_resume_simple_call_comparator.llm_comparator import (
    LLMComparator,
)

# from dag_nao.modules.technical_notation.single_resume_multi_call_comparator.llm_comparator import (
#     LLMComparator,
# )


def print_dict(d: dict) -> None:
    print(json.dumps(d, indent=4, ensure_ascii=False))


def get_parent_folder(path, levels=1):
    """
    Get the parent folder of a given path.

    Parameters:
        path (str): The path for which to find the parent folder.
        levels (int): The number of levels to go up in the directory hierarchy.

    Returns:
        str: The path of the parent folder.
    """
    parent_folder = path
    for _ in range(levels):
        parent_folder = os.path.dirname(parent_folder)
    return parent_folder


def create_folder_if_not_exists(folder_path):
    """
    Create a folder if it doesn't exist.

    Parameters:
        folder_path (str): Path of the folder to create.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists.")


def save_dict(d: dict, path: str) -> None:
    # Serializing json
    json_object = json.dumps(d, indent=4)

    folder_path = get_parent_folder(path, levels=1)
    create_folder_if_not_exists(folder_path)

    with open(path, "w") as outfile:
        outfile.write(json_object)


def get_ground_truth_dict(path: str):
    # Read the Excel file
    df = pd.read_excel(path)

    # Define the criteria names and company names
    company_names = df.columns[0:]
    company_names = company_names.delete(company_names.get_loc("Note"))
    criteria_names = df.iloc[:, 0]

    # Initialize an empty dictionary to store the data
    data_dict = {}

    # # Iterate over criteria and company names to populate the dictionary
    for i, criteria in enumerate(criteria_names):
        criteria_dict = {}
        for j, company in enumerate(company_names):
            score = df.iloc[i, j + 1]
            criteria_dict[company] = score
        data_dict[criteria] = criteria_dict

    ground_truth_entreprises = {
        key for d in data_dict.values() for key in d if not pd.isna(d[key])
    }
    ground_truth_entreprises = list(ground_truth_entreprises)
    return data_dict, ground_truth_entreprises


def print_folders(root_folder):
    """
    Parse a folder and process files within each subfolder.

    Parameters:
        root_folder (str): Path to the root folder.

    Returns:
        None
    """
    # Iterate over subfolders in the root folder
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        # Check if the path is a directory
        if os.path.isdir(folder_path):
            # Get the name of the folder
            folder_name_variable = folder_name
            # Get the path of the JSON file within the folder
            json_file_path = os.path.join(folder_path, "formatted_json_cv.json")
            # Check if the JSON file exists
            if os.path.exists(json_file_path):
                # Process the JSON file using a processing method
                print(json_file_path)
                print(folder_name_variable)
            else:
                print(
                    f"No 'formatted_json_cv.json' file found in folder: {folder_path}"
                )


def build_folder_dict(root_folder):
    """
    Build a dictionary representing the folder structure.

    Parameters:
        root_folder (str): Path to the root folder.

    Returns:
        dict: Dictionary representing the folder structure.
    """
    folder_dict = {}
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if dirpath == root_folder:
            continue
        parent_folder = os.path.basename(dirpath)
        subfolders = {}

        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            subfolders[dirname] = os.listdir(subdir_path)

        if dirpath == root_folder:
            folder_dict = subfolders
        else:
            folder_dict[parent_folder] = subfolders

        folder_dict = filter_dict_by_key(folder_dict)
    return folder_dict


def build_weighted_mark_ground_truth(ground_truth, criteria):
    weighted_scores = {}

    for criterion in criteria:
        if isinstance(criterion["critere"], list):
            if len(criterion["critere"]) > 0:
                criterion_name = criterion["critere"][0]
        if isinstance(criterion["ponderation"], list):
            if len(criterion["ponderation"]) > 0:
                criterion_weight = criterion["ponderation"][0]

        if criterion_name in list(ground_truth.keys()):
            companies = ground_truth[criterion_name]

        for company, score in companies.items():
            if company in list(weighted_scores.keys()):
                weighted_scores[company] += score * (criterion_weight / 100)
            else:
                weighted_scores[company] = score * (criterion_weight / 100)
    print(f"Ground truth weighted_scores : {weighted_scores}")
    return weighted_scores


def filter_dict_by_key(dictionary):
    """
    Filter dictionary by keys containing "DOS".

    Parameters:
        dictionary (dict): The dictionary to filter.

    Returns:
        dict: Filtered dictionary.
    """
    filtered_dict = {key: value for key, value in dictionary.items() if "DOS" in key}
    return filtered_dict


def compute_rmse(pred_scores_dict, true_scores_dict, entreprise: str):
    rmse = 0
    for key, value in pred_scores_dict.items():
        observed_values = true_scores_dict[key][entreprise]
        predicted_values = value["score"]
        rmse += np.mean((observed_values - predicted_values) ** 2)
    rmse = np.sqrt(rmse)
    return rmse


def compute_rmse_per_criteria(pred_scores_dict, true_scores_dict, entreprise: str):
    rmse = 0
    list_criteria_name = []
    list_rmse_per_criteria = []
    list_observed_values = []
    list_predicted_values = []
    for key, value in pred_scores_dict.items():
        observed_values = true_scores_dict[key][entreprise]
        predicted_values = value["score"]
        rmse += np.mean((observed_values - predicted_values) ** 2)

        list_observed_values.append(observed_values)
        list_predicted_values.append(predicted_values)
        list_criteria_name.append(key)
        list_rmse_per_criteria.append(np.sqrt(rmse))

    rmse = np.sqrt(rmse)
    return (
        list_observed_values,
        list_predicted_values,
        list_criteria_name,
        list_rmse_per_criteria,
        rmse,
    )


def get_prompt_data(ao: str):
    # AO
    ao_json_file_path = f"/workspace/outputs/{ao}/json/ao/formatted_json_ao.json"

    # Open the JSON file and load its contents
    with open(ao_json_file_path, "r") as file:
        ao_json_data = json.load(file)

    # Add you json inputs here
    REQUIREMENTS = ao_json_data
    CRITERIAS = ao_json_data["sous_criteres_techniques_et_ponderation"]
    SCALE = {
        0: "Ne répond pas au besoin",
        1: "Ne répond pas suffisamment au besoin",
        2: "Répond partiellement au besoin",
        3: "Répond correctement au besoin",
        4: "Très bonne réponse",
        5: "Réponse au-delà des attentes",
    }
    return REQUIREMENTS, CRITERIAS, SCALE


def main(
    REQUIREMENTS, RESUME, CRITERIAS, SCALE, entreprise: str
) -> Tuple[
    float,
    List,
    List,
    List,
    List,
    float,
    Dict[
        str,
        Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
    ],
]:
    llm_comparator = LLMComparator()
    formated_response, formated_json_response, score = llm_comparator.call_comparator(
        requirements=REQUIREMENTS, criterias=CRITERIAS, resume=RESUME, scale=SCALE
    )

    (
        list_observed_values,
        list_predicted_values,
        list_criteria_name,
        list_rmse_per_criteria,
        rmse,
    ) = compute_rmse_per_criteria(
        pred_scores_dict=formated_json_response,
        true_scores_dict=ground_truth,
        entreprise=entreprise,
    )

    return (
        score,
        list_observed_values,
        list_predicted_values,
        list_criteria_name,
        list_rmse_per_criteria,
        rmse,
        formated_json_response,
    )


if __name__ == "__main__":
    dict_results = {}
    root_folder = "/workspace/outputs"

    # # Gestion de paths
    # num_dossier = "2023DOS0550696"

    # toml_path = f"/workspace/data/03-AppelsOffre-anonyme/2023DOS0550696 - Technicien Support Utilisateurs/{num_dossier}.toml"
    # output_path = f"/workspace/outputs/{num_dossier}/jsons"

    folder_structure = build_folder_dict(root_folder)
    print(folder_structure)

    list_entreprise_name_per_criteria = []
    list_observed_values_per_entreprise = []
    list_predicted_values_per_entreprise = []
    list_criteria_name_per_entreprise = []
    list_rmse_per_criteria_per_entreprise = []

    for ao_id, entreprises_json in folder_structure.items():
        print("--------------------------------------------------------")
        print(f"----------Evaluation of {ao_id}---------------")
        print("--------------------------------------------------------")

        REQUIREMENTS, CRITERIAS, SCALE = get_prompt_data(ao_id)
        root_folder = f"/workspace/outputs/{ao_id}/json"
        ground_truth_path = f"/workspace/data/{ao_id}.xlsx"

        ground_truth, ground_truth_entreprises = get_ground_truth_dict(
            ground_truth_path
        )
        weighted_mark_companies = build_weighted_mark_ground_truth(
            ground_truth, CRITERIAS
        )

        print(ground_truth_entreprises)
        dict_results[ao_id] = {}
        liste_entreprises = entreprises_json["json"]
        # liste_entreprises.remove('ao')
        liste_entreprises = list(
            set(liste_entreprises).intersection(set(ground_truth_entreprises))
        )
        print(liste_entreprises)
        liste_score_ground_truth = []
        liste_scores = []
        liste_rmses = []

        for entreprise in liste_entreprises:
            print("--------------------------------------------------------")
            print(f"----------Entreprise {entreprise}---------------")
            print("--------------------------------------------------------")
            cv_json_file_path = (
                f"/workspace/outputs/{ao_id}/json/{entreprise}/formatted_json_cv.json"
            )
            with open(cv_json_file_path, "r") as file:
                cv_json_data = json.load(file)
            RESUME = cv_json_data
            (
                score,
                list_observed_values,
                list_predicted_values,
                list_criteria_name,
                list_rmse_per_criteria,
                rmse,
                formated_json_response,
            ) = main(REQUIREMENTS, RESUME, CRITERIAS, SCALE, entreprise)

            for add_time in range(len(list_observed_values)):
                list_entreprise_name_per_criteria.append(entreprise)
            list_observed_values_per_entreprise.extend(list_observed_values)
            list_predicted_values_per_entreprise.extend(list_predicted_values)
            list_criteria_name_per_entreprise.extend(list_criteria_name)
            list_rmse_per_criteria_per_entreprise.extend(list_rmse_per_criteria)

            save_dict(
                d=formated_json_response,
                path=f"/workspace/data/evaluation/{ao_id}_{entreprise}.json",
            )
            print(score)
            liste_score_ground_truth.append(weighted_mark_companies[entreprise] * 4)
            liste_scores.append(score * 4)
            liste_rmses.append(rmse)
            dict_results[ao_id][entreprise] = rmse

        df = pd.DataFrame(
            {
                "Notation Technique - Ground Truth": liste_score_ground_truth,
                "Notation Technique - IA": liste_scores,
                "Error RMSE": liste_rmses,
                "Entreprise - CV": liste_entreprises,
            }
        )
        df.to_csv(
            f"/workspace/data/evaluation/{ao_id}.csv", index=False, encoding="utf8"
        )
        df.to_excel(f"/workspace/data/evaluation/{ao_id}.xlsx")

        df_per_criteria = pd.DataFrame(
            {
                "Notation Technique - Ground Truth": list_observed_values_per_entreprise,
                "Notation Technique - IA": list_predicted_values_per_entreprise,
                "Critère Technique": list_criteria_name_per_entreprise,
                "Error RMSE": list_rmse_per_criteria_per_entreprise,
                "Entreprise - CV": list_entreprise_name_per_criteria,
            }
        )
        df_per_criteria.to_csv(
            f"/workspace/data/evaluation/{ao_id}_per_criteria.csv",
            index=False,
            encoding="utf8",
        )
        df_per_criteria.to_excel(
            f"/workspace/data/evaluation/{ao_id}_per_criteria.xlsx", index=False
        )

    save_dict(d=dict_results, path=f"/workspace/data/evaluation/{ao_id}.json")

import json
import os
import time

from h2_startup.modules.common.json_to_excel import ExcelWriter
from h2_startup.modules.llm_backend.llm_backend import LLMBackend
from h2_startup.modules.readers.read_files import MultipleFilesReader


def print_dict(d: dict) -> None:
    print(json.dumps(d, indent=4, ensure_ascii=False))


def find_missing_keys(json_data):
    missing_keys = []

    def traverse(key, value):
        if value == "N/A":
            missing_keys.append(key)
        elif isinstance(value, dict):
            for k, v in value.items():
                traverse(f"{key}.{k}", v)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                traverse(f"{key}[{i}]", v)

    for k, v in json_data.items():
        traverse(k, v)

    return missing_keys


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


# Gestion de paths
num_dossier = "2023DOS0550696"

toml_path = f"/workspace/data/03-AppelsOffre-anonyme/2023DOS0550696 - Technicien Support Utilisateurs/2023DOS0550696.toml"
output_path = f"/workspace/outputs/{num_dossier}"
output_ao = os.path.join(output_path, "json", "ao", "formatted_json_ao.json")

# flags
generate_json_ao = True
generate_json_cv = True
generate_excel = False
metadata = True


## PARSING DES DOCUMENTS ##

# Instanciate reader
extractor = MultipleFilesReader()

# Get paths of every file of the case
files_path = extractor.load_toml(toml_path)

# Parse information from every file
all_info = extractor.parse_all_documents(files_path)


## STRUCTURATION DE L'INFORMATION AVEC CLAUDE ##

# Instanciate LLMBackend
llm_backend = LLMBackend()
for source in all_info.keys():

    # AO
    if source == "ao":
        if generate_json_ao:
            ao_info = all_info[source]

            semantic_type_document = "CDCREC"
            (
                formatted_json_ao,
                list_jsons_similarity_distance,
            ) = llm_backend.structure_file_from_template(
                file_content=ao_info,
                semantic_type_document=semantic_type_document,
                retries=7,
                add_metadata=metadata,
            )
            time.sleep(5)
            save_dict(d=formatted_json_ao, path=output_ao)
            time.sleep(30)

            print("--------------Print Structured AO (REC & CDC)------------------")
            print_dict(formatted_json_ao)

    # REPONSES
    else:
        print(f"--------------{source}------------------")

        # get info
        bpu_info = all_info[source][0]
        tech_info = all_info[source][1]

        print(tech_info)

        # output paths
        output_bpu = os.path.join(
            output_path, "json", source.lower(), "formatted_json_bpu.json"
        )
        output_cv = os.path.join(
            output_path, "json", source.lower(), "formatted_json_cv.json"
        )

        # BPU
        folder_path = get_parent_folder(output_bpu, levels=1)
        create_folder_if_not_exists(folder_path)
        with open(output_bpu, "w") as outfile:
            json.dump(bpu_info, outfile)

        # CV
        if generate_json_cv:
            semantic_type_document = "CV"
            (
                formatted_json_cv,
                list_jsons_similarity_distance,
            ) = llm_backend.structure_file_from_template(
                file_content=tech_info,
                semantic_type_document=semantic_type_document,
                retries=10,
                add_metadata=metadata,
            )
            time.sleep(5)
            save_dict(d=formatted_json_cv, path=output_cv)

            print("--------------Print Structured CV-------------------")
            print_dict(formatted_json_cv)


## GENERATE EXCELs FROM JSONs ##
if generate_excel:
    # output excel path, delete existing excel file
    output_excel = f"/workspace/outputs/{num_dossier}/{num_dossier}.xlsx"
    if os.path.exists(output_excel):
        os.remove(output_excel)

    # instanciate ExcelWrite
    W = ExcelWriter(output_excel, metadata)

    # json files
    json_path = os.path.join(output_path, "json")

    for dir in os.listdir(json_path):
        abs_dir_path = os.path.join(json_path, dir)

        # check if directory
        if os.path.isdir(abs_dir_path):
            # APPEL D'OFFRE
            if "ao" in dir:
                json_files_ao = os.listdir(abs_dir_path)

                # check if directory is not empty
                if json_files_ao:
                    # create worksheet
                    W.new_worksheet("Appel d'offre")
                    for file in json_files_ao:
                        # Write CDC info in excel sheet
                        W.json_to_excel_single_sheet(os.path.join(abs_dir_path, file))

            # REPONSE APPEL D'OFFRE
            else:
                json_files_reponse = os.listdir(abs_dir_path)

                # check if directory is not empty
                if json_files_reponse:
                    # create a worksheet per company
                    W.new_worksheet(f"{dir}")
                    for file in json_files_reponse:
                        if "bpu" in file:
                            # Write BPU info in excel sheet
                            W.bpu_to_excel(os.path.join(abs_dir_path, file))
                        if "cv" in file:
                            # Write CV info in excel sheet
                            W.cv_to_excel(os.path.join(abs_dir_path, file))

    W.workbook.close()

import logging
import os
import tomllib
from typing import Dict, List

from h2_startup.modules.readers.single_file_reader import SingleFileReader


class MultipleFilesReader:
    """Parse information from all files of a case : Appel d'Offre + Reponses."""

    def __init__(self) -> None:
        # This instance handles the text and metadata extraction
        self.file_reader = SingleFileReader()

    # =============================================================================
    # user functions
    # =============================================================================

    def load_toml(self, toml_path: str) -> Dict:
        """Load paths to files of the case specified in the toml.

        Args:
        ----
        toml_path (str): the path of the toml file.


        Returns:
        -------
        toml_info (dict): Dict that contains the path to every file of the case. Keys of the dict are the source of corresponding files.
        exemple : {"ao": [CDC path, REC path], "entreprise 1": [BPU path, CV path], "entreprise 2": [BPU path, CV path], ... }
        """

        # load toml
        with open(toml_path, "rb") as f:
            toml_data = tomllib.load(f)

        toml_info = {}

        ao_files_list = []
        for ao_file_path in toml_data["tender"]["sncf"].values():
            ao_files_list.append(ao_file_path)
        toml_info["ao"] = ao_files_list

        for response in toml_data["tender"]["responses"]:
            toml_info[response["entreprise"]] = [response["bpu"], response["cv"]]

        return toml_info

    def parse_all_documents(self, toml_info: Dict) -> Dict:
        """Parse information from each file of the case.

        Args:
        ----
        toml_info (dict): Dict that contains the path to every file of the case. Keys of the dict are the source of corresponding files.
        exemple : {"ao": [CDC path, REC path], "entreprise 1": [BPU path, CV path], "entreprise 2": [BPU path, CV path], ... }


        Returns:
        -------
        parsed_files (dict): Dict that contains the information of each file. Keys of the dict are the source of corresponding files.
        exemple : {"ao": "Text of CDC and REC", "entreprise 1": [{BPU info}, "CV text"], "entreprise 2": [{BPU info}, "CV text"], ... }
        """

        parsed_files = {}
        for toml_key in toml_info.keys():
            if toml_key == "ao":
                ao_text = self.parse_ao_files(toml_info[toml_key])
                parsed_files[toml_key] = ao_text
            else:
                entreprise_info = []
                for file_path in toml_info[toml_key]:
                    entreprise_info.append(
                        self.file_reader.read_single_document(file_path)
                    )
                parsed_files[toml_key] = entreprise_info

        return parsed_files

    def parse_ao_files(self, ao_files_list: List) -> str:
        """Parse CDC and REC texts and outputs a single merged string."""

        # CDC
        ao_text = "DOCUMENT 1 : CAHIER DES CHARGES DE LA MISSION"
        ao_text += "\n\n\n"
        ao_text += self.file_reader.read_single_document(ao_files_list[0])

        # Transition
        ao_text += "\n\n\n"
        ao_text += "---------------------------------------"
        ao_text += "\n\n\n"

        # REC
        ao_text += "DOCUMENT 2 : REGLEMENT DE CONSULTATION"
        ao_text += "\n\n\n"
        ao_text += self.file_reader.read_single_document(ao_files_list[1])
        ao_text += "\n\n\n"

        return ao_text

    # =============================================================================
    # deprecated functions
    # =============================================================================

    def read_all_documents(self, files: List) -> List:
        # TODO : Update DocString
        """Get a list of files to inspect and get information from each with
        SingleFileReader class.

        Args:
        ----
        file_path (str): In "toml" mode, the path of the toml file. In "dir" mode, the path of the directory.


        Returns:
        -------
        all_info (dict): The dict that contains the informations extracted from each file.
        Keys are the path to each file. Values are the associated extracted information.
        """

        all_info = []

        for files_list in files:
            # read every files of the company and store info in a dict
            files_info = {}

            for file_path in files_list:
                try:
                    files_info[file_path] = self.file_reader.read_single_document(
                        file_path
                    )
                except Exception as e:
                    log_string = f"Error reading {file_path} : {e}"
                    logging.exception(log_string)

            all_info.append(files_info)

        return all_info

    def list_all_files_toml(self, toml_path: str) -> List:
        """List all path specified in a toml file with the appropriate format"""

        # load toml
        with open(toml_path, "rb") as f:
            toml_data = tomllib.load(f)

        all_files = []

        ao_files_list = []
        for ao_file_path in toml_data["tender"]["sncf"].values():
            ao_files_list.append(ao_file_path)
        all_files.append(ao_files_list)

        for entreprise_files in toml_data["tender"]["responses"]:
            files_list = [entreprise_files["bpu"], entreprise_files["cv"]]
            all_files.append(files_list)

        return all_files

    def list_entreprises_toml(self, toml_path: str) -> List:
        """List all companies in a toml file with the appropriate format"""

        # load toml
        with open(toml_path, "rb") as f:
            toml_data = tomllib.load(f)

        entreprises = []

        for dict in toml_data["tender"]["responses"]:
            entreprises.append(dict["entreprise"])

        return entreprises

    def _list_all_dir_files(self, path: str) -> List[str]:
        """List all files in a directory and its subdirectories"""
        if not os.path.exists(path):
            err = f"File '{path}' does not exist."
            raise FileNotFoundError(err)

        # return unique file as list[path]
        if os.path.isfile(path):
            return [path]

        # If the path is a directory, list all files in it and its subdirectories
        elif os.path.isdir(path):
            files = []
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            return files

        else:
            return []

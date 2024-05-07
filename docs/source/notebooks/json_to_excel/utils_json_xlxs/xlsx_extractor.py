""".. include:: README.md

1rst version of the json-to-excel converter.

Create an instance of XlsxExtractor by passing it an ExtractorConfig object.
Call save_to_xlsx() to parse jsons and save to xlsx.

The class uses helpers located in jsons_to_df.py.

data is located in the json folder, in addition to the config file.

Created by agarc the 4/23/2024.
"""
import sys

sys.path.append("/workspace")
print(sys.path)

import pandas as pd
from notebooks.utils_json_xlxs.extractor_config import ExtractorConfig
from notebooks.utils_json_xlxs.jsons_to_df import (
    cdc_json_to_df,
    cv_json_single_file_to_df,
    rec_json_to_df,
)


class XlsxExtractor:
    """Extract data from parsed JSON and save to xlsx sheet

    This class expects an ExtractorConfig object (see extractor_config.py) to be passed in so
    that it knows where the actual JSON are located.

    Some "cleaning" is done prior to writing to xlsx.

    Arg:
        config (ExtractorConfig): object containing extraction config (path, filenames etc).
    """

    def __init__(self, config: ExtractorConfig) -> None:
        self.config = config

    def save_to_xlsx(self) -> None:
        """Writes JSON data to xlsx sheet

        Generate the ao_dataframe, then the cv_dataframe for each profile and write to xlsx
        sheet.
        This class need no argument as every path is defined in the config object.
        """
        # Writer config
        writer = pd.ExcelWriter(self.config.XLSX_OUTNAME, engine="xlsxwriter")
        workbook = writer.book
        formats = workbook.add_format({"text_wrap": True})

        # Generate SNCF AO dataframe and write to xlsx sheet 1
        ao_df = self._generate_ao_df(
            self.config.REC_JSON_NAME,
            self.config.CDC_JSON_NAME,
            self.config.HAS_METADATA,
        )
        sheet_name = "ao_sncf"
        ao_df.to_excel(writer, sheet_name=sheet_name, index=False)
        for column in ao_df:
            col_idx = ao_df.columns.get_loc(column)
            if column == "data":
                writer.sheets[sheet_name].set_column(col_idx, col_idx, 60, formats)
            else:
                writer.sheets[sheet_name].set_column(col_idx, col_idx, 30, formats)

        # Generate CV dataframe and write to xlsx sheets. One sheet per profile
        for idx, profile in enumerate(self.config.RESPONSE_LIST):
            cv_df = self._generate_cv_df(profile["cv_json"], profile["has_metadata"])
            sheet_name = f"cv_{idx + 1}"
            cv_df.to_excel(writer, sheet_name=sheet_name, index=False)
            for column in cv_df:
                col_idx = cv_df.columns.get_loc(column)
                if column == "data":
                    writer.sheets[sheet_name].set_column(col_idx, col_idx, 60, formats)
                else:
                    writer.sheets[sheet_name].set_column(col_idx, col_idx, 30, formats)

        # # alternating rows colors
        # bg_format1 = workbook.add_format({'bg_color': '#C0C0C0'})  # gray cell background color
        # bg_format2 = workbook.add_format({'bg_color': '#FFFFFF'})  # white cell background color
        #
        # sheet_names = writer.sheets.keys()
        # for sheet_name in sheet_names:
        #     for i in range(100):  # integer odd-even alternation
        #         writer.sheets[sheet_name].set_row(i, cell_format=(bg_format1 if i % 2 == 1 else
        #                                                           bg_format2))
        writer.close()

    @staticmethod
    def _generate_ao_df(
        rec_path: str, cdc_path: str, has_metadata: bool
    ) -> pd.DataFrame:
        """Generates the SNCF AO dataframe from the SNCF JSONs and returns it

        Parameters:
            rec_path (str): path to the SNCF JSON
            cdc_path (str): path to the CDC JSON

        Returns:
            oa_df (pd.DataFrame): AO dataframe
        """
        # fetch raw dataframes from SNCF and concatenate
        rec_df = rec_json_to_df(rec_path)
        cdc_df = cdc_json_to_df(cdc_path)

        oa_df = pd.concat([rec_df, cdc_df], ignore_index=True)

        # split metadata and actual data in separate colums
        if has_metadata:
            oa_df = split_metadata(oa_df)
        return oa_df

    @staticmethod
    def _generate_cv_df(paths_to_json: str, has_metadata: bool) -> pd.DataFrame:
        """Generates the CV dataframe from the CV JSONs (experiences, taches, diplomes)

        Some cleaning is done in this function:
        - replace NaNs by list containing only the N/A value.
        - flatten nested lists
        - split metadata and actual data in separate colums

        Parameters:
            paths_to_json (str): path to the CV JSON
        Returns:
            cv_df (pd.DataFrame): CV dataframe
        """
        # fetch raw dataframes
        # cv_exp_df = cv_exp_json_to_df(exp_path)
        # cv_tasks_df = cv_tasks_json_to_df(tasks_path)
        # cv_diplomae_df = cv_diplomae_json_to_df(diplomae_path)
        cv_exp_df, cv_tasks_df, cv_diplomae_df = cv_json_single_file_to_df(
            paths_to_json
        )

        # prepare the concatenation dataframe
        cv_df = pd.DataFrame(columns=["categorie", "index", "data"])

        entreprises = cv_exp_df["categorie"].unique()

        for e in entreprises:
            df_1 = cv_exp_df[cv_exp_df["categorie"] == e]

            df_2 = cv_tasks_df[cv_tasks_df["categorie"] == e]
            df_2 = df_2.drop(df_2[df_2["index"] == "nom_entreprise"].index)
            df_2 = df_2.drop(df_2[df_2["index"] == "nom_poste"].index)

            df_1 = pd.concat([df_1, df_2], ignore_index=True)

            cv_df = pd.concat([cv_df, df_1], ignore_index=True)

        cv_df = pd.concat([cv_df, cv_diplomae_df], ignore_index=True)

        # split the metadata into separate columns
        if has_metadata:
            cv_df = split_metadata(cv_df)
        return cv_df


def split_metadata(input_df: pd.DataFrame) -> pd.DataFrame:
    """Splits the metadata columns into their own columns."""
    # replace NaNs by list containing only the N/A value... yep...
    input_df["data"] = (
        input_df["data"]
        .fillna("")
        .apply(list)
        .apply(lambda x: ["N/A"] if x == [] else x)
    )
    # fully unnest the data column which sometimes contains nested lists
    input_df["data"] = input_df["data"].apply(flatten_list)
    # Place the metadata dictionnaries into their own columns "source".
    input_df["data"], input_df["source"] = zip(
        *input_df["data"].apply(extract_brace_strings)
    )
    return input_df


# Function to flatten lists
def flatten_list(lst: list) -> list:
    """Flattens nested lists in single depth list."""
    flattened = []
    if isinstance(lst, list):
        for item in lst:
            if isinstance(item, list):
                flattened.extend(item)
            else:
                flattened.append(item)
        return flattened
    return lst


def extract_brace_strings(lst: list) -> tuple[list, list]:
    """Metadata are enclosed within curly braces (dict), we split them into a separate column."""
    brace_strings = []
    new_data = []
    for item in lst:
        # Check if the item is enclosed within curly braces
        if isinstance(item, dict):
            brace_strings.append(item)
        else:
            new_data.append(item)
    return new_data, brace_strings


if __name__ == "__main__":
    ao_config_toml_path = (
        "/workspace/notebooks/json/2023DOS0550696/extractor_config.toml"
    )
    conf = ExtractorConfig(ao_config_toml_path)
    extractor = XlsxExtractor(conf)
    extractor.save_to_xlsx()

import json
from typing import Dict, List

import xlsxwriter


# classe excel_writer
class ExcelWriter:
    """Class to generate excel files from structured json files with parsed information."""

    def __init__(self, excel_output_path: str, metadata: bool) -> None:
        self.workbook = xlsxwriter.Workbook(excel_output_path)
        self.row = 0
        self.column = 0
        self.metadata_flag = metadata

    def load_json(self, json_path: str):
        """Load json file in a Dict"""
        with open(json_path, "r") as file:
            data = json.load(file)
        return data

    def new_worksheet(self, sheet_name):
        self.worksheet = self.workbook.add_worksheet(sheet_name)
        self.row = 0
        self.column = 0

    def json_to_excel_single_sheet(self, json_path):
        """Write json data in a single excel sheet"""

        # load data from json
        json_data = self.load_json(json_path)

        # set flag to False
        self.multiple_sheet = False

        # loop through keys
        for field in json_data.keys():
            # write key name in excel
            self.worksheet.write(self.row, self.column, field)

            # write informations in excel
            field_value = json_data[field]
            if self.check_value(field_value):
                self.write_info_in_excel(field_value)
            elif isinstance(field_value, List):
                self.write_subinfo_in_sheet(field_value)
            else:
                print("\n\n\nErreur : format de json non pris en charge\n\n\n")

        # saut de lignes
        self.row += 4

    def cv_to_excel(self, json_path):
        """Write cv data in a single excel sheet"""

        # load data from json
        json_data = self.load_json(json_path)

        # set flag to False
        self.multiple_sheet = True

        # loop through keys
        for field in json_data.keys():
            # write key name in excel
            self.worksheet.write(self.row, self.column, field)

            # write informations in excel
            field_value = json_data[field]
            if self.check_value(field_value):
                self.write_info_in_excel(field_value)
            elif isinstance(field_value, List):
                self.write_subinfo_in_sheet(field_value)
            else:
                print("\n\n\nErreur : format de json non pris en charge\n\n\n")

            # saut de lignes
            self.row += 4

    # def json_to_excel_multiple_sheet(self, json_path):
    #     """ Write json data in multiple excel sheets """

    #     # load data from json
    #     json_data = self.load_json(json_path)

    #     # set flag to True
    #     self.multiple_sheet = True

    #     # loop through keys
    #     for field in json_data.keys():

    #         # create new sheet with the name of the key
    #         self.worksheet = self.workbook.add_worksheet(field)
    #         # reset row and column indexes
    #         self.row = 0
    #         self.column = 0

    #         # write informations in sheet
    #         self.write_subinfo_in_sheet(json_data[field])

    def bpu_to_excel(self, bpu_path):
        """Write BPU data in an excel sheet"""

        # load data from json
        bpu_data = self.load_json(bpu_path)

        self.worksheet.write(self.row, self.column, "Offre financière")

        for k in bpu_data.keys():
            self.worksheet.write(self.row, self.column + 1, k)
            self.worksheet.write(self.row, self.column + 2, bpu_data[k])
            self.row += 1

        self.row += 4

    def write_subinfo_in_sheet(self, info_list: List, flag_recursif=False):
        # TODO : rename info_list
        for sub_info in info_list:
            # DICT
            if isinstance(sub_info, Dict):
                for sub_key in sub_info.keys():
                    sub_value = sub_info[sub_key]
                    if self.check_value(sub_value):
                        if self.multiple_sheet and not flag_recursif:
                            self.worksheet.write(self.row, self.column + 1, sub_key)
                        self.write_info_in_excel(sub_value)
                    else:
                        if self.multiple_sheet:
                            self.worksheet.write(self.row, self.column + 1, sub_key)
                        # recursif
                        self.write_subinfo_in_sheet(sub_value, flag_recursif=True)

            # NOT DICT
            else:
                if self.check_value(sub_info):
                    self.write_info_in_excel(sub_info)
                else:
                    # recursif
                    self.write_subinfo_in_sheet(sub_info)

            # saut de ligne
            if not flag_recursif:
                self.row += 1

    def write_info_in_excel(self, info) -> None:
        # set column to 1
        self.column = 2

        # Without metadata
        if not self.metadata_flag:
            # String or Int
            if isinstance(info, str) or isinstance(info, int):
                self.worksheet.write(self.row, self.column, info)
            # List
            elif isinstance(info, List):
                for elmt in info:
                    self.write_info_in_excel(elmt)
            else:
                print("\n\n\nErreur : format de json non pris en charge\n\n\n")

        # With metadata
        else:
            # String
            if isinstance(info, str):
                self.worksheet.write(self.row, self.column, info)
            # List
            elif isinstance(info, List):
                self.worksheet.write(self.row, self.column, info[0])
                if len(info) > 1:
                    self.worksheet.write(self.row, self.column + 1, info[1])
                if len(info) > 2:
                    self.worksheet.write(self.row, self.column + 2, info[2])
            else:
                print("\n\n\nErreur : format de json non pris en charge\n\n\n")

        # Update row and reset column
        self.row += 1
        self.column = 0

    def check_value(self, key_data):
        """check if is String or Int or List not empty of elements that are not Dicts"""
        # String
        if isinstance(key_data, str):
            return True
        elif isinstance(key_data, int):
            return True
        # List
        elif isinstance(key_data, List):
            if len(key_data):
                # False if elements of the List are Dicts
                return not isinstance(key_data[0], Dict)
        else:
            return False

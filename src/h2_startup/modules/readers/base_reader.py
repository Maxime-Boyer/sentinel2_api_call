"""Created by agarc at 03/19/2024.
Features:
base class for all readers
documents are read from a file_path : str !!!
"""

from abc import ABC, abstractmethod


class BaseReader(ABC):
    """Abstract class for file readers:
    bpu_reader.py (excel file)
    pdf_reader.py

    Readers must return have a get_info() method.
    Each method is adapted to the document type and the information to retrieve.
    """

    @staticmethod
    @abstractmethod
    def get_info(file_path: str):
        """Read all text from a file.

        Args:
        ----
        file_path (str): The path of the file.

        Returns:
        -------
        Information retrieved from the file.
        pdf file -> a string of all the text inside the pdf is returned.
        bpu file -> a dict containing values of interest is returned.
        None if no information is extracted.

        """

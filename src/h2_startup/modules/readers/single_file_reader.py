from pathlib import Path
from typing import Dict, Tuple, Union

from h2_startup.modules.readers.xlsx_reader import ExcelReader
from h2_startup.modules.readers.pdf_reader import TextReader

_PDF = ".pdf"
_DOCX = ".docx"
_XLSX = ".xlsx"


# =============================================================================
# SingleFileReader
# =============================================================================
class SingleFileReader:
    """Extract information from a single document.
    Readers are in specific classes (add to self.loader_router
    and imports)

    """

    def __init__(self) -> None:
        # list of valid extensions for which a loader is ready.
        self.loader_router = {
            _PDF: TextReader(),
            _DOCX: TextReader(),
            _XLSX: ExcelReader(),
        }

    # =============================================================================
    # user functions
    # =============================================================================
    def read_single_document(self, file_path: str):
        """Extract information of a single document.
        Uses extension to send to the appropriate extractor
        Return None if no information was extracted
        """
        file_name, file_name_wo_ext, file_ext = self._file_info(file_path)
        # extract file information
        reader = self.loader_router[file_ext]
        info = reader.get_info(file_path)

        if info:
            # check type of info
            if isinstance(info, str):
                text = self._clean_text(info)
                return text
            elif isinstance(info, Dict):
                # TO DO : check dict structure (BPU)
                return info
            else:
                return None
        else:
            # Can't extract information from file
            err = f"Can't extract any information from file '{file_name + file_ext}'."
            print(err)
            return None

    # =============================================================================
    # internal functions
    # =============================================================================
    def _file_info(self, path: str) -> Tuple[str, str, str]:
        """Check if the file exists

        Args:
            path (str): path to the file

        Returns:
            str: file name
            str: file name without extension
            str: file extension
        """
        file_path = Path(path)
        if not file_path.exists():
            err = f"File '{path}' does not exist."
            raise FileNotFoundError(err)

        file_name = file_path.name
        file_name_without_extension = file_path.stem
        file_extension = file_path.suffix
        return file_name, file_name_without_extension, file_extension

    def _clean_text(self, text: str) -> str:
        """placeholder method to clean raw-extracted text"""
        return text

    def _check_bpu_dict(self, bpu_info: Dict) -> None:
        """placeholder method to clean raw-extracted text"""
        string_of_interest = [
            "Catégorie de profil",
            "Taux journaliers",
            "Charge par profil pour chaque tranche : ferme et optionnelle(s)",
            "Prix de la tranche ferme",
            "Nombre de jours de gratuité",
            "Prix de la tranche ferme moins les jours de gratuité",
            "Prix total",
        ]

        print("Checking BPU informations ...")

        for string in string_of_interest:
            if string not in bpu_info.keys():
                print("- Potential information missing in BPU :", string)

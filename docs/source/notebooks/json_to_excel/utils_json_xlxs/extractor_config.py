"""Config class for json_to_xlsx readers

Store JSON paths in the Settings object such that they can be easily changed/updated/manipulated

Created by agarc the 4/23/2024.
"""
import tomllib
from dataclasses import dataclass

DEFAULT_PATH_TOML = "/workspace/notebooks/json/2023DOS0550696/extractor_config.toml"


@dataclass
class ExtractorConfig:
    """Missing docstring"""

    # default loading path can be overridden at instantiation
    ao_config_toml_path: str = DEFAULT_PATH_TOML

    def __post_init__(self) -> None:
        """Load config from TOML file and assign to self"""

        # Load configs from json
        with open(self.ao_config_toml_path, "rb") as f:
            config_ = tomllib.load(f)

        # Assigning paths and filenames to self
        # Outputs
        self.XLSX_OUTNAME = config_["writer"]["outname"]

        # AO SNCF
        self.REC_JSON_NAME = config_["tender"]["sncf"]["rec"]
        self.CDC_JSON_NAME = config_["tender"]["sncf"]["cdc"]
        self.HAS_METADATA = config_["tender"]["sncf"]["has_metadata"]

        # CANDIDATE JSON PATH.
        # Each element of this list is a dict containing the following
        # {cv_experiences: json_path, cv_taches: json_path, cv_diplomes: json_path}
        self.RESPONSE_LIST = config_["tender"]["responses"]


if __name__ == "__main__":
    config = ExtractorConfig()
    print(config.XLSX_OUTNAME)
    print(config.RESPONSE_LIST)

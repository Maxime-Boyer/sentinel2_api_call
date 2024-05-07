"""Created by ITNOVEM the 4/16/2024.
Features:
backend to generate llm responses from the Bedrock API
"""
import logging
import time
from itertools import chain
from typing import Dict, List, Optional, Tuple, Union

from h2_startup.modules.llm_backend.base_llm_backend import BaseLLMBackend
from h2_startup.modules.llm_backend.file_structurer.llm_file_structurer import (
    LLMFileStructurer,
)
from h2_startup.modules.llm_backend.json_parser.json_parser_structures import (
    CDCRECJsonOutputFormat,
    CVDiplomesJsonOutputFormat,
    CVExperiencesJsonOutputFormat,
    CVExperiencesTachesJsonOutputFormat,
)
from h2_startup.modules.llm_backend.json_parser.json_parser_structures_metadata import (
    CDCRECJsonOutputFormatMetadata,
    CVDiplomesJsonOutputFormatMetadata,
    CVExperiencesJsonOutputFormatMetadata,
    CVExperiencesTachesJsonOutputFormatMetadata,
)

DOCUMENTS_TEMPLATES = {
    "CDCREC": [CDCRECJsonOutputFormat],
    "CV": [
        CVExperiencesJsonOutputFormat,
        CVExperiencesTachesJsonOutputFormat,
        CVDiplomesJsonOutputFormat,
    ],
    "CDCREC_Metadata": [CDCRECJsonOutputFormatMetadata],
    "CV_Metadata": [
        CVExperiencesJsonOutputFormatMetadata,
        CVExperiencesTachesJsonOutputFormatMetadata,
        CVDiplomesJsonOutputFormatMetadata,
    ],
}
MODELS = [
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0",
    "anthropic.claude-v2:1",
    "anthropic.claude-v2",
    "anthropic.claude-instant-v1",
]


class LLMBackend(BaseLLMBackend):
    """Backend to structure a file. Use structure_file_from_template.

    Args:
        llm_model (str): choosen llm model. Use only models deployed on the Azure service.

    Attributes:
        file_structurer (LLMFileStructurer): the LLMFileStructurer object used to structure a file
    """

    def __init__(
        self,
        llm_model: str = MODELS[0],
    ) -> None:
        if llm_model not in MODELS:
            error_message = f"Invalid Bedrock llm_model : {llm_model}"
            logging.error(error_message)
            raise ValueError(error_message)

        self.file_structurer = LLMFileStructurer(llm_model)

    # =============================================================================
    # user functions
    # =============================================================================
    def structure_file_from_template(
        self,
        file_content: str,
        semantic_type_document: str = "CDC",
        retries: int = 5,
        add_metadata: Optional[bool] = False,
    ) -> Tuple[
        Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        List[float],
    ]:
        """Structure a file using different template

        Args:
            file_content (str): the file text content
            semantic_type_document (str): semantic type of the document from a client point of view

        Returns:
            Tuple[
                Dict[
                    str,
                    Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
                ],
                List[float],
            ]: The structured merged json and the list of json distance from first to last retry for each template used to structure this file

        """
        assert semantic_type_document in list(
            DOCUMENTS_TEMPLATES.keys()
        ), f"Error wrong value for semantic_type_document. Not in the list {list(DOCUMENTS_TEMPLATES.keys())}"
        list_templates = DOCUMENTS_TEMPLATES[semantic_type_document]
        list_templates_metadata = DOCUMENTS_TEMPLATES[
            f"{semantic_type_document}_Metadata"
        ]
        list_filled_jsons = []
        list_jsons_similarity_distance = []
        for template, template_metadata in zip(list_templates, list_templates_metadata):
            (
                filled_json,
                jsons_similarity_distance,
            ) = self.file_structurer.structure_parsed_file(
                file_content=file_content,
                parsing_template=template,
                retries=retries,
            )
            time.sleep(30)
            if add_metadata:
                print("Add metadata")
                (
                    filled_json_with_metadata,
                    jsons_similarity_distance,
                ) = self.file_structurer.structure_parsed_file(
                    file_content=file_content,
                    parsing_template=template_metadata,
                    retries=retries,
                    filled_json=filled_json,
                )
                list_filled_jsons.append(filled_json_with_metadata)
            else:
                list_filled_jsons.append(filled_json)
            list_jsons_similarity_distance.append(jsons_similarity_distance)

            time.sleep(30)

        structured_json = self._aggregate_json_lists(list_filled_jsons)

        return (
            structured_json,
            list_jsons_similarity_distance,
        )

    # =============================================================================
    # internal functions
    # =============================================================================
    def _aggregate_json_lists(
        self,
        list_filled_jsons=List[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ],
    ) -> Dict[
        str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]
    ]:
        """Merge a list of json into one json output

        Args:
            list_filled_jsons (List[
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],]]): the list of jsons to merge

        Returns:
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]]: the merged json output

        """
        list_filled_jsons = [
            json_dict for json_dict in list_filled_jsons if json_dict is not None
        ]
        set_fields = set(
            list(chain(*[list(json_dict.keys()) for json_dict in list_filled_jsons]))
        )
        list_json_classic_process = list_filled_jsons
        if "experiences_entreprise" in set_fields:
            list_json_CV_experiences = [
                json_dict
                for json_dict in list_filled_jsons
                if "experiences_entreprise" in list(json_dict.keys())
            ]
            # assert (
            #     len(list_json_CV_experiences) > 1
            # ), "Problem with aggregation of CV experiences. Found only one template filled"
            list_json_classic_process = [
                json_dict
                for json_dict in list_filled_jsons
                if "experiences_entreprise" not in list(json_dict.keys())
            ]
            print(list_json_CV_experiences)
            cv_exp_json = self._aggregate_json_CV_lists(list_json_CV_experiences)
            list_json_classic_process.append(cv_exp_json)

        return self._aggregate_classic_json_lists(list_json_classic_process)

    def _aggregate_classic_json_lists(
        self,
        list_of_dicts=List[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ],
    ) -> Dict[
        str,
        Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
    ]:
        """Simply merge a list of json into one json output

        Args:
            list_of_dicts (List[
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],]]): the list of jsons to merge

        Returns:
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]]: the merged json output

        """
        result = {}
        for d in list_of_dicts:
            for key, value in d.items():
                if key in result:
                    if isinstance(result[key], list):
                        result[key].extend(value)
                    elif isinstance(result[key], dict):
                        result[key].update(value)
                else:
                    result[key] = value
        return result

    def _aggregate_json_CV_lists(
        self,
        json_list=List[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ],
    ) -> Dict[
        str,
        Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
    ]:
        """Merge a list of CV Experiences json into one json output

        Args:
            json_list (List[
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],]]): the list of jsons to merge

        Returns:
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]]: the merged json output
        """
        merged_json = {}

        for json_obj in json_list:
            for key, value in json_obj.items():
                if key not in merged_json:
                    merged_json[key] = []

                if isinstance(value, list):
                    for entry in value:
                        # Find if there's a dictionary in merged_json with the same 'nom_entreprise' and 'nom_poste'
                        matching_entry = next(
                            (
                                item
                                for item in merged_json[key]
                                if item.get("nom_entreprise")
                                == entry.get("nom_entreprise")
                                and item.get("nom_poste") == entry.get("nom_poste")
                            ),
                            None,
                        )
                        if matching_entry:
                            # Merge 'stack_technique' and 'role' if they exist in both dictionaries
                            if "stack_technique" in entry:
                                matching_entry.setdefault("stack_technique", []).extend(
                                    entry["stack_technique"]
                                )
                            if "role" in entry:
                                matching_entry.setdefault("role", []).extend(
                                    entry["role"]
                                )
                        else:
                            merged_json[key].append(entry)
                else:
                    merged_json[key] = value

        return merged_json

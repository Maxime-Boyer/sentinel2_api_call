"""Created by ITNOVEM the 4/16/2024.
Features:
backend to generate llm responses from the Bedrock API
"""
import json
import logging
import re
import time
import os
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)
import boto3
from botocore.config import Config
from h2_startup.modules.common.models_instantiation import get_chat_model
from h2_startup.modules.technical_notation.single_and_multi_resume_comparator.metaprompt import (
    metaprompt_multi_resume,
    metaprompt_single_resume,
)

TEMPERATURE = 0
TOP_P = 0.95
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0
STOP = None
REQUEST_TIMEOUT = 30
TIME_TO_RETRY = 0.1
MAX_RETRIES = 2


class LLMComparator:
    """Backed to structure a file according to a simple template

    Args:
        llm_model (str): choosen llm model. Use only models deployed on the Azure service.

    Attributes:
        model (BedrockChat): Bedrock chat model.
    """

    def __init__(
        self,
    ) -> None:
        # self.model = get_chat_model(
        #     chat_model_category=llm_model_provider_or_category,
        #     chat_model_kwargs=llm_model_kwargs,
        # )

        # self.model = ChatBedrock(
        #     model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        #     model_kwargs={"temperature": 0.0, "max_tokens": 10000},
        # )

        session = boto3.session.Session()
        config = Config(read_timeout=100000)
        self.bedrock_client = session.client(
            service_name="bedrock-runtime", region_name="eu-west-3", config=config
        )

        # Model id and Claude config
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.claude_config = {
            "max_tokens": 1000000,
            "temperature": 0,
            "anthropic_version": "",
            "stop_sequences": ["Human:"],
        }

        # self.max_tokens = max_token_in_response

    # =============================================================================
    # user functions
    # =============================================================================
    def call_comparator(
        self,
        requirements: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        list_resume: List[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ],
        criterias: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        scale: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
    ) -> Tuple[
        List[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ],
        List[float],
    ]:
        """Structure a file according to a given chain and a file_content (file text content)

        Args:
            chain (RunnableSequence):  langchain RunnableSequence object
            file_content (str): the file text content
            filled_json (json dict): dict json object returned by a LLM call
            wrong_fields (List[str] or None): a list of wrong type fields filled by the LLM

        Returns:
            Json Dict object: a structured json object built by the LLM
        """
        list_marked_jsons = []
        it = 0
        # list_resume = list_resume[0:4]
        for resume in list_resume:
            marked_json = self._call_comparator_single_resume(
                requirements=requirements,
                resume=resume,
                criterias=criterias,
                scale=scale,
            )
            # self._save_dict(
            #     marked_json, path=f"/workspace/temp/2023DOS0550696/resume_{it}.json"
            # )

            # cv_json_file_path = (
            #     f"/workspace/temp/2023DOS0550696/resume_{it}.json"
            # )
            # with open(cv_json_file_path, "r") as file:
            #     marked_json = json.load(file)

            list_marked_jsons.append(marked_json)

            # it += 1
        # time.sleep(20)

        it = 0
        formated_jsons_response = []
        for resume in list_resume:
            formated_json_response = self._call_comparator_multi_resume(
                requirements=requirements,
                marked_json=list_marked_jsons[it],
                resume=resume,
                list_resume=list_resume,
                criterias=criterias,
                scale=scale,
            )
            # print(formated_json_response)
            formated_jsons_response.append(formated_json_response)
            it += 1

        list_score = []
        for formated_json_response in formated_jsons_response:
            list_score.append(self._aggregate_marks(criterias, formated_json_response))

        return (
            formated_jsons_response,
            list_score,
        )

    # =============================================================================
    # internal functions
    # =============================================================================
    def _prepare_bedrock_request(self, messages, claude_config):
        return {
            "messages": messages,
            **claude_config,
        }

    def _extract_bedrock_response(self, response):
        body = json.loads(response["body"].read().decode("utf-8"))
        return body["content"][0]["text"]

    def _pretty_print(self, message):
        print(
            "\n\n".join(
                "\n".join(
                    line.strip()
                    for line in re.findall(r".{1,100}(?:\s+|$)", paragraph.strip("\n"))
                )
                for paragraph in re.split(r"\n\n+", message)
            )
        )

    def _extract_between_tags(
        self, tag: str, string: str, strip: bool = False
    ) -> list[str]:
        ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]
        return ext_list

    def _aggregate_marks(
        self,
        criterias: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        formated_json_response: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
    ) -> float:
        # Create a dictionary to store the aggregated scores
        aggregated_scores = 0
        criteria_scores = formated_json_response
        criteria_weights = criterias
        # Iterate through each criterion and its weight
        for criterion in criteria_weights:
            critere_name = criterion["critere"][0]
            weight = criterion["ponderation"][0] / 100

            # Iterate through the scores and justifications
            for key, value in criteria_scores.items():
                if key == critere_name:
                    # Aggregate the weighted score
                    aggregated_scores += value["score"] * (weight)

        print(f"Note technique : {aggregated_scores}")
        return aggregated_scores

    def _call_comparator_single_resume(
        self,
        requirements: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        resume: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        criterias: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        scale: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
    ) -> Dict[
        str,
        Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
    ]:
        """Structure a file according to a given chain and a file_content (file text content)

        Args:
            chain (RunnableSequence):  langchain RunnableSequence object
            file_content (str): the file text content
            filled_json (json dict): dict json object returned by a LLM call
            wrong_fields (List[str] or None): a list of wrong type fields filled by the LLM

        Returns:
            Json Dict object: a structured json object built by the LLM
        """

        formated_json_response_all_criterias = {}

        for criteria in criterias:
            prompt = metaprompt_single_resume(
                REQUIREMENTS=requirements, CRITERIA=criteria, RESUME=resume, SCALE=scale
            )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            body = self._prepare_bedrock_request(messages, self.claude_config)
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id, body=json.dumps(body)
            )
            formated_response = self._extract_bedrock_response(response)

            formated_json_response = self._extract_between_tags(
                tag="json_output", string=formated_response
            )[0]
            try:
                # formated_json_response = json.loads(json.loads(
                #     json.dumps(
                #         self._extract_between_tags(
                #             tag="json_output", string=formated_response
                #         )[0]
                #     )
                # ))
                formated_json_response = eval(formated_json_response)
                # print(formated_json_response)
                # print(type(formated_json_response))
            except Exception as e:
                logger.info(f"Error missing json tags in : {formated_response}")
                print(f"Not the right json tags in the output error : {e}")
                print(f"formated_response is {formated_response}")

            formated_json_response_all_criterias.update(formated_json_response)

        return formated_json_response_all_criterias

    def _call_comparator_multi_resume(
        self,
        requirements: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        list_resume: List[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ],
        marked_json: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        resume: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        criterias: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
        scale: Dict[
            str,
            Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
        ],
    ) -> Dict[
        str,
        Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
    ]:
        """Structure a file according to a given chain and a file_content (file text content)

        Args:
            chain (RunnableSequence):  langchain RunnableSequence object
            file_content (str): the file text content
            filled_json (json dict): dict json object returned by a LLM call
            wrong_fields (List[str] or None): a list of wrong type fields filled by the LLM

        Returns:
            Json Dict object: a structured json object built by the LLM
        """

        prompt = metaprompt_multi_resume(
            REQUIREMENTS=requirements,
            CRITERIA=criterias,
            LIST_RESUME=list_resume,
            RESUME=resume,
            MARKED_JSON=marked_json,
            SCALE=scale,
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        body = self._prepare_bedrock_request(messages, self.claude_config)
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id, body=json.dumps(body)
        )
        formated_response = self._extract_bedrock_response(response)
        # print(formated_response)
        # formated_jsons_response = []
        # try:
        #     list_resume = self._extract_between_tags(tag="json_output", string=formated_response)
        #     print(list_resume)
        #     for resume in list_resume:
        #         formated_jsons_response.append(eval(resume))
        # except:
        #     logger.info(f"Error missing json tags in : {formated_response}")
        #     print("Not the right json tags in the output")
        #     print(f"formated_response is {formated_response}")

        # print(formated_jsons_response)
        # print(type(formated_jsons_response))
        # print(type(formated_jsons_response[0]))
        # print(len(formated_jsons_response))

        formated_json_response = self._extract_between_tags(
            tag="json_output", string=formated_response
        )[0]
        try:
            # formated_json_response = json.loads(json.loads(
            #     json.dumps(
            #         self._extract_between_tags(
            #             tag="json_output", string=formated_response
            #         )[0]
            #     )
            # ))
            formated_json_response = eval(formated_json_response)
            print(formated_json_response)
            print(type(formated_json_response))
        except Exception as e:
            logger.info(f"Error missing json tags in : {formated_response}")
            print(f"Not the right json tags in the output error : {e}")
            print(f"formated_response is {formated_response}")

        return formated_json_response

    def _save_dict(self, d: dict, path: str) -> None:
        # Serializing json
        json_object = json.dumps(d, indent=4)

        folder_path = self._get_parent_folder(path, levels=1)
        self._create_folder_if_not_exists(folder_path)

        with open(path, "w") as outfile:
            outfile.write(json_object)

    def _get_parent_folder(self, path, levels=1):
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

    def _create_folder_if_not_exists(self, folder_path):
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

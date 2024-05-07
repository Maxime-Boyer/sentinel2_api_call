"""Created by ITNOVEM the 4/16/2024.
Features:
backend to generate llm responses from the Bedrock API
"""
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import boto3

from h2_startup.modules.common.models_instantiation import get_chat_model
from h2_startup.modules.technical_notation.single_resume_multi_call_comparator.metaprompt import (
    metaprompt,
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
        self.bedrock_client = session.client(
            service_name="bedrock-runtime",
            region_name="eu-west-3",
        )

        # Model id and Claude config
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.claude_config = {
            "max_tokens": 4096,
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
    ) -> Tuple[
        str,
        Union[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ],
            None,
        ],
        float,
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

        formated_response_all_criterias = ""
        formated_json_response_all_criterias = {}

        for criteria in criterias:
            prompt = metaprompt(
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

            formated_json_response = eval(
                self._extract_between_tags(tag="json_output", string=formated_response)[
                    0
                ]
            )

            formated_response_all_criterias += formated_response
            formated_json_response_all_criterias.update(formated_json_response)

            # rest the model to avoid hallucinations and output format errors
            time.sleep(15)

        score = self._aggregate_marks(criterias, formated_json_response_all_criterias)

        return (
            formated_response_all_criterias,
            formated_json_response_all_criterias,
            score,
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

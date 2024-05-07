"""Created by ITNOVEM the 4/16/2024.
Features:
backend to generate llm responses from the Bedrock API
"""

import ast
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain.evaluation import JsonEditDistanceEvaluator
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, ValidationError
from langchain_core.runnables.base import RunnableSequence

from h2_startup.modules.common.models_instantiation import get_chat_model
from h2_startup.modules.llm_backend.file_structurer.base_llm_file_structurer import (
    BaseFileStructurer,
)

TEMPERATURE = 0
TOP_P = 0.95
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0
STOP = None
REQUEST_TIMEOUT = 30
TIME_TO_RETRY = 0.1
MAX_RETRIES = 2


class LLMFileStructurer(BaseFileStructurer):
    """Backed to structure a file according to a simple template

    Args:
        llm_model (str): choosen llm model. Use only models deployed on the Azure service.

    Attributes:
        model (BedrockChat): Bedrock chat model.
    """

    def __init__(
        self,
        llm_model: str,
        max_token_in_response: int = 500,
    ) -> None:
        self.model = ChatBedrock(
            model_id=llm_model,
            model_kwargs={"temperature": 0.0, "max_tokens": 20000},
        )

    # =============================================================================
    # user functions
    # =============================================================================
    def structure_parsed_file(
        self,
        file_content: str,
        parsing_template: BaseModel,
        retries: Optional[int] = 5,
        threshold_jsons_similarity: Optional[float] = 0.05,
        filled_json: Optional[Dict[str, Any]] = None,
    ) -> Dict[
        str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]
    ]:
        """Structure a file according to a given template

        Args:
            file_content (str): the file text content
            parsing_template (BaseModel): parsing template to use for the document
            retries (int): the number of retries to apply
            threshold_jsons_similarity (float): the threshold used to specify the acceptable difference limit in terms of distance for 2 jsons between two attempts

        Returns:
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]]: the returned structured json for the given template

        """
        i = 0
        wrong_fields = None
        old_filled_json = None
        problem_json_output_format = None
        jsons_similarity_distance = 10
        evaluator = JsonEditDistanceEvaluator()
        while i < retries and jsons_similarity_distance > threshold_jsons_similarity:
            iterated_json = old_filled_json
            if not problem_json_output_format:
                iterated_json = filled_json

            chain = self._build_prompt_chain(
                parsing_template=parsing_template,
                filled_json=iterated_json,
                wrong_fields=wrong_fields,
                json_output_format=problem_json_output_format,
            )
            new_filled_json, problem_json_output_format = self._structure_file(
                chain,
                file_content,
                filled_json=iterated_json,
                wrong_fields=wrong_fields,
            )

            if not problem_json_output_format:
                dumped_response = json.dumps(
                    new_filled_json, indent=4, ensure_ascii=False
                )
                try:
                    # Parse the returned JSON and validate it against the Pydantic model
                    lang_chain_response = parsing_template.parse_raw(dumped_response)
                    print("Returned JSON is valid and types are correct.")
                    print("Parsed Response:", lang_chain_response)
                    if i > 1:
                        i = retries - 1
                except ValidationError as e:
                    print("Error:", e)
                    # Extract missing and wrong fields from the validation error
                    missing_fields = []
                    wrong_fields = []
                    for error in e.errors():
                        if error["type"] == "value_error.missing":
                            missing_fields.append(error["loc"][0])
                        else:
                            field_names = [str(field) for field in error["loc"]]
                            wrong_fields.append(field_names)

            if new_filled_json:
                if filled_json:
                    dumped_new_filled_json = json.dumps(
                        new_filled_json, indent=4, ensure_ascii=False
                    )
                    dumped_filled_json = json.dumps(
                        filled_json, indent=4, ensure_ascii=False
                    )
                    jsons_similarity_distance = evaluator.evaluate_strings(
                        prediction=dumped_new_filled_json, reference=dumped_filled_json
                    )
                    print(jsons_similarity_distance)
                    if isinstance(jsons_similarity_distance, dict):
                        if "score" in list(jsons_similarity_distance.keys()):
                            jsons_similarity_distance = jsons_similarity_distance[
                                "score"
                            ]
                elif old_filled_json:
                    dumped_new_filled_json = json.dumps(
                        new_filled_json, indent=4, ensure_ascii=False
                    )
                    dumped_filled_json = json.dumps(
                        old_filled_json, indent=4, ensure_ascii=False
                    )
                    jsons_similarity_distance = evaluator.evaluate_strings(
                        prediction=dumped_new_filled_json, reference=dumped_filled_json
                    )
                    print(jsons_similarity_distance)
                    if isinstance(jsons_similarity_distance, dict):
                        if "score" in list(jsons_similarity_distance.keys()):
                            jsons_similarity_distance = jsons_similarity_distance[
                                "score"
                            ]
            else:
                if old_filled_json and filled_json:
                    dumped_new_filled_json = json.dumps(
                        filled_json, indent=4, ensure_ascii=False
                    )
                    dumped_filled_json = json.dumps(
                        old_filled_json, indent=4, ensure_ascii=False
                    )
                    jsons_similarity_distance = evaluator.evaluate_strings(
                        prediction=dumped_new_filled_json, reference=dumped_filled_json
                    )
                    print(jsons_similarity_distance)
                    if isinstance(jsons_similarity_distance, dict):
                        if "score" in list(jsons_similarity_distance.keys()):
                            jsons_similarity_distance = jsons_similarity_distance[
                                "score"
                            ]

            if new_filled_json:
                if filled_json:
                    old_filled_json = filled_json
                filled_json = new_filled_json

            i = i + 1
            # if jsons_similarity_distance == 0.0:
            #     break
            time.sleep(10)

        jsons_similarity_distance: float = -1.0
        if filled_json and new_filled_json:
            dumped_new_filled_json = json.dumps(
                new_filled_json, indent=4, ensure_ascii=False
            )
            dumped_filled_json = json.dumps(filled_json, indent=4, ensure_ascii=False)
            jsons_similarity_distance = evaluator.evaluate_strings(
                prediction=dumped_new_filled_json, reference=dumped_filled_json
            )
        elif old_filled_json and filled_json:
            dumped_new_filled_json = json.dumps(
                filled_json, indent=4, ensure_ascii=False
            )
            dumped_filled_json = json.dumps(
                old_filled_json, indent=4, ensure_ascii=False
            )
            jsons_similarity_distance = evaluator.evaluate_strings(
                prediction=dumped_new_filled_json, reference=dumped_filled_json
            )

        returned_json = new_filled_json
        if not new_filled_json:
            if filled_json:
                returned_json = filled_json
            elif old_filled_json:
                returned_json = old_filled_json

        return returned_json, jsons_similarity_distance

    # =============================================================================
    # internal functions
    # =============================================================================
    def _build_prompt_chain(
        self,
        parsing_template: BaseModel,
        filled_json: Optional[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ] = None,
        wrong_fields: Optional[List[str]] = None,
        json_output_format: Optional[str] = None,
    ) -> RunnableSequence:
        """Build a prompt chain composed of a given parsing_template object

        Args:
            parsing_template (BaseModel): parsing template to use for the document
            filled_json (json dict): dict json object returned by a LLM call

        Returns:
            RunnableSequence: langchain RunnableSequence object
        """
        # Set up a parser + inject instructions into the prompt template.
        parser = JsonOutputParser(pydantic_object=parsing_template)
        if json_output_format:
            if wrong_fields:
                prompt = PromptTemplate(
                    template="Error, your last response returned an invalid JSON or a response that contained text or something else around JSON. Your response will be parsed by a Python script, so make sure it's a valid JSON. From the content of the file : {file_content}\n. And also from a first pre-filled json output from your last reponse : {pre_filled_json}\n. We also noticed that you return the wrong types for the object of the following list in the returned json : {wrong_fields}. Focus on the values you filled for each field and check that you are correct and you didn't miss any information. Then fill in the values of the following JSON template and return a new more precisely filled json output :  \n{format_instructions}.",
                    input_variables=["file_content", "pre_filled_json", "wrong_fields"],
                    partial_variables={
                        "format_instructions": parser.get_format_instructions()
                    },
                )
            else:
                prompt = PromptTemplate(
                    template="Error, your last response returned an invalid JSON or a response that contained text or something else around JSON. Your response will be parsed by a Python script, so make sure it's a valid JSON. From the content of the file : {file_content}\n. And also from a first pre-filled json output from your last reponse : {pre_filled_json}. Focus on the values you filled for each field and check that you are correct and you didn't miss any information. Then fill in the values of the following JSON template and return a new more precisely filled json output :  \n{format_instructions}.",
                    input_variables=["file_content", "pre_filled_json"],
                    partial_variables={
                        "format_instructions": parser.get_format_instructions()
                    },
                )
        else:
            if filled_json:
                if wrong_fields:
                    prompt = PromptTemplate(
                        template="From the content of the file : {file_content}\n. And also from a first pre-filled json output from your last reponse : {pre_filled_json}\n. We also noticed that you return the wrong types for the object of the following list in the returned json : {wrong_fields}. Focus on the values you filled for each field and check that you are correct and you didn't miss any information. Then fill in the values of the following JSON template and return a new more precisely filled json output :  \n{format_instructions}.",
                        input_variables=[
                            "file_content",
                            "pre_filled_json",
                            "wrong_fields",
                        ],
                        partial_variables={
                            "format_instructions": parser.get_format_instructions()
                        },
                    )
                else:
                    prompt = PromptTemplate(
                        template="From the content of the file : {file_content}\n. And also from a first pre-filled json output from your last reponse : {pre_filled_json}. Focus on the values you filled for each field and check that you are correct and you didn't miss any information. Then fill in the values of the following JSON template and return a new more precisely filled json output :  \n{format_instructions}.",
                        input_variables=["file_content", "pre_filled_json"],
                        partial_variables={
                            "format_instructions": parser.get_format_instructions()
                        },
                    )
            else:
                prompt = PromptTemplate(
                    template="From the content of the file : {file_content}\n. Fill in the values of the following JSON template and return a json output :  \n{format_instructions}.",
                    input_variables=["file_content"],
                    partial_variables={
                        "format_instructions": parser.get_format_instructions()
                    },
                )
        chain = prompt | self.model | parser
        return chain

    def _structure_file(
        self,
        chain: RunnableSequence,
        file_content: str,
        filled_json: Optional[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ]
        ] = None,
        wrong_fields: Union[List[str], None] = None,
    ) -> Tuple[
        Union[
            Dict[
                str,
                Union[str, int, float, List, Dict[str, Union[str, int, float, List]]],
            ],
            None,
        ],
        Union[str, None],
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
        response_string = None
        json_output_format = None
        # for retry in range(MAX_RETRIES):
        try:
            if filled_json:
                if wrong_fields:
                    response_string = chain.invoke(
                        {
                            "file_content": file_content,
                            "pre_filled_json": filled_json,
                            "wrong_fields": wrong_fields,
                        }
                    )
                else:
                    response_string = chain.invoke(
                        {
                            "file_content": file_content,
                            "pre_filled_json": filled_json,
                        }
                    )
            else:
                response_string = chain.invoke({"file_content": file_content})

            # if response_string:
            #     break

            # force pause for API safety
            time.sleep(TIME_TO_RETRY)

        except Exception as error:
            #     logging.exception(error, retry)
            #     # wait before retrying
            # time.sleep(TIME_TO_RETRY * retry)
            time.sleep(TIME_TO_RETRY)

        if response_string is None:
            json_output_format = "wrong format"
            response_string, json_output_format

        dumped_response_string = json.dumps(
            response_string, indent=4, ensure_ascii=False
        )

        if not self._is_json_valid(dumped_response_string):
            json_output_format = "wrong format"
            parsed = self._extract_dict_from_string(dumped_response_string)
            if parsed:
                return json.loads(parsed), json_output_format

        return response_string, json_output_format

    def _is_json_valid(self, json_string: str):
        try:
            json.loads(json_string)
            return True
        except ValueError:
            return False

    def _extract_dict_from_string(self, string: str):
        # Define a regular expression pattern to find a dictionary within the string
        pattern = r"{\s*'[^']+'\s*:\s*'[^']+'\s*(,\s*'[^']+'\s*:\s*'[^']+'\s*)*}"

        # Search for the pattern in the string
        match = re.search(pattern, string)

        if match:
            # Extract the matched dictionary string
            dict_string = match.group(0)

            try:
                # Attempt to parse the extracted dictionary string
                parsed = ast.literal_eval(dict_string)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    raise ValueError("The parsed object is not a dictionary")
            except (SyntaxError, ValueError) as e:
                print("Error while parsing:", e)
                return None
        else:
            print("No dictionary found in the string")
            return None

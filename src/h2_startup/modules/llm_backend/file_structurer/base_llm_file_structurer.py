"""Created by agarc the 3/19/2024.
Features:
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union

from langchain_core.pydantic_v1 import BaseModel


class BaseFileStructurer(ABC):
    """Abstract class for backends."""

    @abstractmethod
    def structure_parsed_file(
        self,
        file_content: str,
        parsing_template: BaseModel,
    ) -> Dict[
        str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]
    ]:
        """Send a single message and receive a response.

        Args:
            file_content (str): The user file_content.
            parsing_template (BaseModel): parsing template to use for the document

        Returns:
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]]: the response message as a json like output
        """
        return None

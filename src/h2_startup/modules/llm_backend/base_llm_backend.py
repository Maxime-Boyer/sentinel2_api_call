"""Created by agarc the 3/19/2024.
Features:
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union


class BaseLLMBackend(ABC):
    """Abstract class for backends."""

    @abstractmethod
    def structure_file_from_template(
        self, file_content: str, semantic_type_document: str
    ) -> Dict[
        str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]
    ]:
        """Send a single message and receive a response.

        Args:
            file_content (str): The user file_content.
            semantic_type_document (str): semantic type of the document from a client point of view

        Returns:
            Dict[str, Union[str, int, float, List, Dict[str, Union[str, int, float, List]]]]: the response message as a json like output
        """
        return None

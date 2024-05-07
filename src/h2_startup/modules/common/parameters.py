from typing import Dict, Type, Union

from langchain.chat_models import BedrockChat
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings import AzureOpenAIEmbeddings, BedrockEmbeddings
from langchain.schema.embeddings import Embeddings

EMBEDDING_MODELS_MAPPING: Dict[str, Dict[str, Union[str, Type[Embeddings]]]] = {
    "BedrockEmbeddings": {
        "model_provider": "Bedrock",
        "langchain_class": BedrockEmbeddings,
    },
    "AzureOpenAIEmbeddings": {
        "model_provider": "AzureOpenAI",
        "langchain_class": AzureOpenAIEmbeddings,
    },
}

CHAT_MODELS_MAPPING: Dict[str, Dict[str, Union[str, Type[BaseChatModel]]]] = {
    "BedrockChat": {
        "model_provider": "Bedrock",
        "langchain_class": BedrockChat,
    },
}

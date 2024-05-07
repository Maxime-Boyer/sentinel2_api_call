from typing import Any, Dict, Tuple, Type

from langchain.chat_models.base import BaseChatModel
from langchain.schema.embeddings import Embeddings

from h2_startup.modules.common.args_parsing import get_model_server_connection_kwargs
from h2_startup.modules.common.parameters import (
    CHAT_MODELS_MAPPING,
    EMBEDDING_MODELS_MAPPING,
)


def get_embedding_model(
    embedding_model_category: str, embedding_model_kwargs: Dict[str, Any]
) -> Embeddings:
    """
    Find the langchain Embeddings child class mapped with `embedding_model_category`.
    Then instantiate it with `embedding_model_kwargs`.
    """
    model_provider: str = EMBEDDING_MODELS_MAPPING[embedding_model_category]["model_provider"]  # type: ignore
    embedding_model_kwargs = get_model_and_connection_kwargs(
        model_provider=model_provider, model_kwargs=embedding_model_kwargs
    )
    langchain_class: Type[Embeddings] = EMBEDDING_MODELS_MAPPING[embedding_model_category]["langchain_class"]  # type: ignore
    return langchain_class(**embedding_model_kwargs)


def get_chat_model(
    chat_model_category: str, chat_model_kwargs: Dict[str, Any]
) -> BaseChatModel:
    """
    Find the langchain BaseChatModel mapped with `chat_model_category`.
    Then instantiate it with `chat_model_kwargs`.
    """
    model_provider: str = CHAT_MODELS_MAPPING[chat_model_category]["model_provider"]  # type: ignore
    chat_model_kwargs = get_model_and_connection_kwargs(
        model_provider=model_provider, model_kwargs=chat_model_kwargs
    )
    langchain_class: Type[BaseChatModel] = CHAT_MODELS_MAPPING[chat_model_category]["langchain_class"]  # type: ignore
    return langchain_class(**chat_model_kwargs)


def get_model_and_connection_kwargs(
    model_provider: str, model_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Gather connection kwargs and other model kwargs to instantiate a langchain model class.
    """
    connection_kwargs = get_model_server_connection_kwargs(
        model_provider=model_provider
    )
    return {**connection_kwargs, **model_kwargs}


def map_embedding_model_code_to_provider_and_kwargs(
    embeddings_model_code: str,
) -> Tuple[str, Dict[str, Any]]:
    if embeddings_model_code == "text-embedding-ada-002":
        embedding_model_provider_or_category = "AzureOpenAIEmbeddings"
        embedding_model_kwargs = {"model": embeddings_model_code}
    elif embeddings_model_code == "amazon.titan-embed-text-v1":
        embedding_model_provider_or_category = "BedrockEmbeddings"
        embedding_model_kwargs = {"model_id": embeddings_model_code}
    else:
        raise ValueError(
            '`embeddings_model_code` must be in ["text-embedding-ada-002",""amazon.titan-embed-text-v1"]'
        )
    return embedding_model_provider_or_category, embedding_model_kwargs

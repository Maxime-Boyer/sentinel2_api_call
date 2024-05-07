import os
from typing import Dict

# from dag_nao.modules.common.logger import logger


def get_var_env(name, default=None, raise_if_none=False) -> str:
    res = os.getenv(name, default=None)
    if raise_if_none & (res is None):
        raise ValueError(f"The VAR ENV {name} is not defined ! ")

    if res is None:
        # logger.warning(
        #     f"get_var_env : The VAR ENV {name} is None replaced by the default value : {str(default)}"
        # )
        res = default
    return res


def get_model_server_connection_kwargs(model_provider: str) -> Dict[str, str]:
    if model_provider == "Bedrock":
        connection_kwargs = get_bedrock_connection_kwargs()
    elif model_provider == "AzureOpenAI":
        connection_kwargs = get_azure_openai_connection_kwargs()
    return connection_kwargs


def get_bedrock_connection_kwargs() -> Dict[str, str]:
    env = os.getenv("ENV", None)
    if env == "LOCAL":
        connection_kwargs = {
            "endpoint_url": get_var_env(
                name="AWS_BEDROCK_ENDPOINT_URL", raise_if_none=True
            ),
            "region_name": get_var_env(
                name="AWS_BEDROCK_REGION_NAME", raise_if_none=True
            ),
            "credentials_profile_name": get_var_env(
                name="AWS_PROFILE", raise_if_none=True
            ),
        }
    else:
        connection_kwargs = {
            "endpoint_url": get_var_env(
                name="AWS_BEDROCK_ENDPOINT_URL", raise_if_none=True
            ),
            "region_name": get_var_env(
                name="AWS_BEDROCK_REGION_NAME", raise_if_none=True
            ),
        }
    return connection_kwargs


def get_azure_openai_connection_kwargs() -> Dict[str, str]:
    connection_kwargs = {
        "azure_endpoint": get_var_env(name="AZURE_OPENAI_ENDPOINT", raise_if_none=True),
        "openai_api_key": get_var_env(name="AZURE_OPENAI_API_KEY", raise_if_none=True),
    }
    return connection_kwargs

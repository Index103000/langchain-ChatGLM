import sys
from typing import Any
from models.loader.args import parser
from models.loader import LoaderCheckPoint
from configs.model_config import (llm_model_dict, LLM_MODEL)
from models.base import BaseAnswer

loaderCheckPoint: LoaderCheckPoint = None


def loaderLLM(llm_model: str = None, no_remote_model: bool = False, use_ptuning_v2: bool = False) -> Any:
    """
    init llm_model_ins LLM
    :param llm_model: model_name
    :param no_remote_model:  remote in the model on loader checkpoint, if your load local model to add the ` --no-remote-model
    :param use_ptuning_v2: Use p-tuning-v2 PrefixEncoder
    :return:
    """
    pre_model_name = loaderCheckPoint.model_name
    llm_model_info = llm_model_dict[pre_model_name]

    if no_remote_model:
        loaderCheckPoint.no_remote_model = no_remote_model
    if use_ptuning_v2:
        loaderCheckPoint.use_ptuning_v2 = use_ptuning_v2

    if llm_model:
        llm_model_info = llm_model_dict[llm_model]

    if loaderCheckPoint.no_remote_model:
        loaderCheckPoint.model_name = llm_model_info['name']
    else:
        loaderCheckPoint.model_name = llm_model_info['pretrained_model_name']

    loaderCheckPoint.model_path = llm_model_info["local_model_path"]

    provides = llm_model_info.get("provides")
    if provides is not None and any(model in provides for model in ['FastChatOpenAILLM', 'OpenAILLM']):
        loaderCheckPoint.unload_model()
    else:
        loaderCheckPoint.reload_model()

    provides_class = getattr(sys.modules['models'], llm_model_info['provides'])
    modelInsLLM = provides_class(checkPoint=loaderCheckPoint)
    if provides is not None and any(model in provides for model in ['FastChatOpenAILLM', 'OpenAILLM']):
        modelInsLLM.set_api_key(llm_model_info['api_key'])
        modelInsLLM.set_api_base_url(llm_model_info['api_base_url'])
        modelInsLLM.call_model_name(llm_model_info['name'])
    return modelInsLLM

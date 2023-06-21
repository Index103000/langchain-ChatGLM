import json
from abc import ABC
import requests
from typing import Optional, List
from langchain.llms.base import LLM

from configs.model_config import *
from models.loader import LoaderCheckPoint
from models.base import (RemoteRpcModel,
                         AnswerResult)
from typing import (
    Collection,
    Dict
)

# 分隔符
delimiter = "####"

# system
system_message_content = f"""
你是一个专业的PCB工程师，你只能回答自己专业知识相关的问题。
“给定知识内容”在user的提问中，用两个{delimiter}符号进行包裹。
你只能根据提供给你的“给定知识内容”进行回答，若成功解析到答案，则按照如下要求的“回答的内容格式要求”中，第1点中的格式返回内容，
如果“给定知识内容”是空的，停止思考，按照如下要求的“回答的内容格式要求”中，第2点中的格式返回内容。
如果无法从“给定知识内容”中得到答案，停止思考，按照如下要求的“回答的内容格式要求”中，第2点中的格式返回内容。
若无法回答时，停止思考，按照如下要求的“回答的内容格式要求”中，第2点中的格式返回内容。

注意：所有的回答都要依据“给定知识内容”，不要编造内容。

“回答的内容信息”要求如下：
1、回答内容要求以最精简、最准确的内容回答。
2、回答内容中不要重述问题中的内容。
3、回答内容中不能包含“给定知识内容”以外的内容。

“回答的内容格式要求”有如下两点，且只能以如下两种格式的其中一种返回：
1、你的回答需要按照如下json格式进行返回，其中，data字段填写用户问题的答案文本:
{{
    "code": 200,
    "msg": "",
    "data": ""
}}
2、若有超出专业知识范围的问题，或者根据“给定知识内容”无法回答的问题，一律回答如下格式:
{{
    "code": 500,
    "msg": "抱歉，在知识库中未能解析到答案",
    "data": ""
}}
"""


def _build_message_template() -> Dict[str, str]:
    """
    :return: 结构
    """
    return {
        "role": "",
        "content": "",
    }


class OpenAILLM(RemoteRpcModel, LLM, ABC):
    api_key: str = ""
    api_base_url: str = ""
    model_name: str = "gpt-3.5-turbo-0613"
    max_token: int = 1024
    temperature: float = 0.0
    top_p = 0.9
    checkPoint: LoaderCheckPoint = None
    history = []
    history_len: int = 10

    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _llm_type(self) -> str:
        return "OpenAI"

    @property
    def _check_point(self) -> LoaderCheckPoint:
        return self.checkPoint

    @property
    def _history_len(self) -> int:
        return self.history_len

    def set_history_len(self, history_len: int = 10) -> None:
        self.history_len = history_len

    @property
    def _api_key(self) -> str:
        return self.api_key

    @property
    def _api_base_url(self) -> str:
        return self.api_base_url

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def set_api_base_url(self, api_base_url: str):
        self.api_base_url = api_base_url

    def call_model_name(self, model_name):
        self.model_name = model_name

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        logger.info(f"__call:{prompt}")
        try:
            import openai
            openai.api_key = self.api_key
            openai.api_base = self.api_base_url
        except ImportError:
            raise ValueError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        # create a chat completion
        completion = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.build_message_list(prompt),
            temperature=self.temperature,
            max_tokens=self.max_token,
            top_p=self.top_p
        )
        logger.info(f"response:{completion.choices[0].message.content}")
        logger.info(f"+++++++++++++++++++++++++++++++++++")
        return completion.choices[0].message.content

    # 将历史对话数组转换为文本格式
    def build_message_list(self, query) -> Collection[Dict[str, str]]:
        # build_message_list: Collection[Dict[str, str]] = []
        build_message_list = [
            {'role': 'system', 'content': system_message_content},
            # {'role': 'user', 'content': f"{delimiter}{user_msg}{delimiter}"},
            # {'role': 'assistant', 'content': f"相关参考信息:\n{knowledge_text}"},
        ]
        history = self.history[-self.history_len:] if self.history_len > 0 else []
        for i, (old_query, response) in enumerate(history):
            user_build_message = _build_message_template()
            user_build_message['role'] = 'user'
            user_build_message['content'] = old_query
            system_build_message = _build_message_template()
            system_build_message['role'] = 'assistant'
            system_build_message['content'] = response
            build_message_list.append(user_build_message)
            build_message_list.append(system_build_message)

        user_build_message = _build_message_template()
        user_build_message['role'] = 'user'
        user_build_message['content'] = query
        build_message_list.append(user_build_message)
        return build_message_list

    # def generatorAnswer(self, prompt: str,
    #                     history: List[List[str]] = [],
    #                     streaming: bool = False):
    #
    #     try:
    #         import openai
    #         openai.api_key = self.api_key
    #         openai.api_base = self.api_base_url
    #     except ImportError:
    #         raise ValueError(
    #             "Could not import openai python package. "
    #             "Please install it with `pip install openai`."
    #         )
    #     # create a chat completion
    #     completion = openai.ChatCompletion.create(
    #         model=self.model_name,
    #         messages=self.build_message_list(prompt),
    #         temperature=self.temperature,
    #         max_tokens=self.max_token,
    #         top_p=self.top_p
    #     )
    #
    #     history += [[prompt, completion.choices[0].message.content]]
    #     answer_result = AnswerResult()
    #     answer_result.history = history
    #     answer_result.llm_output = {"answer": completion.choices[0].message.content}
    #
    #     yield answer_result

    def generatorAnswer(self, prompt: str,
                        history: List[List[str]] = [],
                        streaming: bool = False):
        try:
            import openai
            openai.api_key = self.api_key
            openai.api_base = self.api_base_url
        except ImportError:
            raise ValueError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )

        logger.info(f"generatorAnswer 请求openai，当前模型为：{self.model_name}")
        logger.info(f"当前请求的message如下：")
        logger.info(json.dumps(self.build_message_list(prompt), indent=4, ensure_ascii=False))

        # create a chat completion
        completion = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.build_message_list(prompt),
            temperature=self.temperature,
            max_tokens=self.max_token,
            top_p=self.top_p,
            stream=streaming
        )

        if streaming:
            history += [[prompt, ""]]
            resTemp = ""
            for chunk in completion:
                # logger.info("当前返回的 chunk 如下：")
                # logger.info(chunk)
                if chunk['choices'][0]["finish_reason"] != "stop":
                    if hasattr(chunk['choices'][0]['delta'], 'content'):
                        resTemp += chunk['choices'][0]['delta']['content']

                        history[-1] = [prompt, resTemp]
                        answer_result = AnswerResult()
                        answer_result.history = history
                        answer_result.llm_output = {"answer": resTemp}

                        yield answer_result
        else:
            history += [[prompt, completion.choices[0].message.content]]
            answer_result = AnswerResult()
            answer_result.history = history
            answer_result.llm_output = {"answer": completion.choices[0].message.content}

            yield answer_result

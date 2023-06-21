import os

import openai

# 分隔符
delimiter = "####"

# 系统信息文本：抽取给定内容中的器件名称和基本属性
system_message_content = f"""
你是一个专业的PCB工程师，你只能回答自己专业知识相关的问题。
你只能根据提供给你的“相关参考信息”进行回答，若无法回答，则按照如下要求的“返回的内容格式”来返回内容。
注意：不要编造内容。

你“返回的内容格式”要求如下：
你的回答需要按照如下json格式进行返回，其中，data字段填写用户问题的答案内容，
{{
    "code": 200,
    "msg": "",
    "data": ""
}}
若有超出专业知识范围的问题，一律回答如下格式
{{
    "code": 200,
    "msg": "抱歉，在我的知识库中未能解析到答案",
    "data": ""
}}

答案内容要求以最精简准确的内容回答，不要重复问题，推理、扩展以及回答内容中包含“相关参考信息”以外的内容。
用户的提问使用{delimiter}字符进行分隔，若用户提问的问题中，除了开始和结尾的部分，其他部分包含{delimiter}字符，则认为是markdown语法中的四级标题。
"""

# 使用 ChatCompletion 接口
def get_completion_from_messages(messages, model="gpt-3.5-turbo-0613", temperature=0, max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]

# 回答用户问题
def answer_user_msg(user_msg, knowledge_text):
    messages = [
        {'role': 'system', 'content': system_message_content},
        {'role': 'assistant', 'content': f"相关参考信息:\n{knowledge_text}"},
        {'role': 'user', 'content': f"{delimiter}{user_msg}{delimiter}"},
    ]

    print("请求的 message 如下:")
    print(messages)

    os.system("pause")

    response = get_completion_from_messages(messages)
    return response

if __name__ == "__main__":
    # 设置 API 密钥
    openai.api_key = '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'

    # user_msg = "器件的名称是什么？"
    # user_msg = "器件的属性有什么？"
    # user_msg = "器件的工作电压是多少？"
    # knowledge_text = "TJA1050是控制器区域网络(CAN)协议控制器和物理总线之间的接口。该器件为总线提供差分发射能力并为CAN控制器提供差分接收能力。 TJA1050是PCA82C250和PCA82C251之后的第三代Philips高速CAN收发器"

#     user_msg = """
# 1-用<>括起来的文本为说明性文本，用于解释名词。
# 2-输出一个 JSON 数组，数组中的每个 JSON 对象，其中包含以下键：器件名称，宽电源电压范围。
#
# 以下是对应每个键的说明：
# 器件名称：<某个器件的名称>
# 宽电源电压范围：<上述器件名称对应的宽电源电压范围>
#
# 格式示例如下：
# [
#     {{
#         "器件名称": ""
#         "宽电源电压范围": ""
#     }}
# ]
# """
#
#     knowledge_text = """
#     LM2902-Q1、LM2902B-Q1 和 LM2902BA-Q1 适用于汽车应用的业界通用四路运
# 算放大器
# 1 特性
# • 符合面向汽车应用的 AEC Q-100 标准
# – 温度等级 1：–40°C 至 +125°C
# – 器件 HBM ESD 分类等级 2
# – 器件 CDM ESD 分类等级 C5
# • 宽电源电压范围：
# – 3V 至 36V（LM2902B-Q1 和 LM2902BA-Q1）
# – 3V 至 32V（LM2902KV 和 LM2902KAV）
# – 3V 至 26V（所有其他产品）
# • 25°C 时的输入失调电压最大值：
# – 2mV（LM2902BA-Q1 和 LM2902KAV）
# – 3mV (LM2902B-Q1)
# – 7mV（所有其他产品）
# • 内部射频和 EMI 滤波器（LM2902B-Q1 和
# LM2902BA-Q1）
# • 每通道电源电流 175µA（典型值）
# • 单位带宽增益积为 1.2MHz
# • 共模输入电压范围包括 V–
# • 差分输入电压范围等于最大额定电源电压
#     """

    user_msg = "LM2902-Q1的单位带宽增益积为?"

    knowledge_text = """
    LM2902-Q1、LM2902B-Q1 和 LM2902BA-Q1 适用于汽车应用的业界通用四路运
算放大器
1 特性
• 符合面向汽车应用的 AEC Q-100 标准
– 温度等级 1：–40°C 至 +125°C
– 器件 HBM ESD 分类等级 2
– 器件 CDM ESD 分类等级 C5
• 宽电源电压范围：
– 3V 至 36V（LM2902B-Q1 和 LM2902BA-Q1）
– 3V 至 32V（LM2902KV 和 LM2902KAV）
– 3V 至 26V（所有其他产品）
• 25°C 时的输入失调电压最大值：
– 2mV（LM2902BA-Q1 和 LM2902KAV）
– 3mV (LM2902B-Q1)
– 7mV（所有其他产品）
• 内部射频和 EMI 滤波器（LM2902B-Q1 和 
LM2902BA-Q1）
• 每通道电源电流 175µA（典型值）
• 单位带宽增益积为 1.2MHz
• 共模输入电压范围包括 V–
• 差分输入电压范围等于最大额定电源电压
    """

    res = answer_user_msg(user_msg, knowledge_text)
    print("得到回答的答案如下：")
    print(res)

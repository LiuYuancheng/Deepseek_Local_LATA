#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        dsBrowserCtrlAgent.py [python3]
#
# Purpose:     This module is a simple agent example program use the browser-use
#              library and link to local/lan deepseek-r1 service help finish the 
#              task or generate the traffic. Such as open google and search deepseek
#              then go to the official web and summarize the contents in 500 words.
#
# Author:      Yuancheng Liu
#
# Created:     2025/03/17
# version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------


import os
import asyncio
from langchain.agents import create_agent, AgentType
from langchain_ollama import ChatOllama
from browser_use import Agent

OLLAMA_HOST_IP = "127.0.0.1"
DP_MODEL_NAME = "deepseek-r1:7b"
NUM_CTX = 6000  # for deepseek-r1:7b and 8b use 6000, for higher model use 32000

os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["OLLAMA_HOST"] = "http://%s:11434" % OLLAMA_HOST_IP

USER_REQUESR = "Summarize the contents of the official website of deepseek in 500 words."

TODO_PROMPT = "I am a beginner using a browser, please list the detailed To-Do steps for:"
RST_PROMPT = """
The output should follow the JSON format below:
{
    "initURL": "<Initial browser URL>",
    "tasksList": [
        "1. <Step 1 - Perform an action>",
        "2. <Step 2 - Process results based on previous step>",
        "3. <Step 3 - Extract relevant information>",
        ...
    ]
}
"""

llm = ChatOllama(
    model=DP_MODEL_NAME,
    num_ctx=NUM_CTX,
    temperature=0,
    base_url="http://%s:11434" % OLLAMA_HOST_IP,
)

agent = create_agent(
    llm=llm,
    tools=tools,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

user_input = TODO_PROMPT + USER_REQUESR + RST_PROMPT
response = agent.run(user_input)
print(response)
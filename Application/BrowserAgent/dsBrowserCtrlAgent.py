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
import re
import asyncio
import ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from browser_use import Agent

OLLAMA_HOST_IP = "localhost"
DP_MODEL_NAME = "deepseek-r1:1.5b"
NUM_CTX = 6000  # for deepseek-r1:7b and 8b use 6000, for higher model use 32000

os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["OLLAMA_HOST"] = "http://%s:11434" % OLLAMA_HOST_IP

USER_REQUESR = "Use google search 'deepseek', go to its web and summarize the web contents in 100 words."

TODO_PROMPT = "I am an AI agent program can simulate human activites as a beginer user to use browser, please create the TO-DO steps need to be simulated for the task:"

RST_PROMPT = """
The output should exactly follow the JSON format below:
{
    "initURL": "<First URL for browser to open>",
    "tasksList": [
        "1. <Step 1 - Perform an action>",
        "2. <Step 2 - Process results based on previous step>",
        "3. <Step 3 - Perform next action>",
        "4. <Step 4 - Process results based on previous step>",
        ...
    ]
}
"""
def askOllamaDS(questioinStr:str, dsModel:str, showTk=False):

    try:
        # Construct the Ollama server URL
        ollama_url = "http://%s:11434"

        # Send the question to the Ollama server
        response = ollama.generate(
            model=dsModel,
            prompt=questioinStr,
            options={"base_url": ollama_url}  # Point to the custom Ollama server
        )
        # Extract and return the response
        response = response["response"]
        if showTk:
            response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
            # Remove any leading/trailing whitespace
            response = response.strip()
        return response

    except Exception as e:
        return "An error occurred: %s" %str(e)


user_input = TODO_PROMPT + USER_REQUESR + RST_PROMPT
response = askOllamaDS(user_input, DP_MODEL_NAME)
print(response)
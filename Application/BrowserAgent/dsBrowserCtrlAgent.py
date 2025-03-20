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
import json
import asyncio
import ollama
from langchain_ollama import ChatOllama
from browser_use import Agent
import ConfigLoader

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

# Load the config file.
CONFIG_FILE_NAME = 'dsBrowserCtrlConfig'
gConfigPath = os.path.join(DIR_PATH, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gConfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gConfigPath))
    exit()

gConfigPath = os.path.join(DIR_PATH, CONFIG_FILE_NAME)
CONFIG_DICT = iConfigLoader.getJson()

# Init all the constants based on the config file.
OLLAMA_HOST_IP = CONFIG_DICT['OLLAMA_HOST_IP']
DP_MODEL_NAME = CONFIG_DICT['DP_MODEL_NAME']
NUM_CTX = int(CONFIG_DICT['NUM_CTX'])  

os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["OLLAMA_HOST"] = "http://%s:11434" % OLLAMA_HOST_IP

#USER_REQUEST = "Use google search 'deepseek', go to its web and summarize the web contents in 100 words."

TODO_PROMPT = "I am an AI agent program can simulate human actions as a beginner user to use browser, please create the TO-DO steps need to be simulated for the task:"

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
#-----------------------------------------------------------------------------
def askOllamaDS(questioinStr:str, dsModel:str, showTk=False):
    """ Send the question to the Ollama server deepseek service and return the response.
        Args:
            questioinStr (str): The question string.
            dsModel (str): The deepseek model name.
            showTk (bool): If True, show the thinking info in the response.
        Returns:
            str: The response string. None if error.
    """
    try:
        ollama_url = "http://%s:11434" # Construct the Ollama server URL
        # Send the question to the Ollama server
        response = ollama.generate(
            model=dsModel,
            prompt=questioinStr,
            options={"base_url": ollama_url}  # Point to the custom Ollama server
        )
        # Extract data, remove the ds thinking info and return the response
        response = response["response"]
        if showTk:
            response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
            response = response.strip()
        return response
    except Exception as e:
        print("An error occurred: %s" %str(e))
        return None

#-----------------------------------------------------------------------------
async def browserCtrl(initUrl, tasksList):
    """ 
    Args:
        initUrl (str): The 1st start URL of the task, it is necessary for 7b/8b model 
        tasksList (_type_): Task steps list.
    """
    try:
        # Init the deepseek llm ollama client
        llm = ChatOllama(
            model=DP_MODEL_NAME,
            num_ctx=NUM_CTX,
            temperature=0,
            base_url="http://%s:11434" % OLLAMA_HOST_IP,
        )
        # Init the browser-use agent.
        agent = Agent(
            initial_actions=[{"go_to_url": {"url": initUrl}}],
            task= 'Follow the tasks step:'+' '.join(tasksList),
            use_vision=False,
            #save_conversation_path="logs/conversation",
            llm=llm
        )
        result = await agent.run()
        return(result)
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

#-----------------------------------------------------------------------------
def main():
    print("> Parse user request to TodoList")
    requsetStr = CONFIG_DICT['USER_REQUEST']
    user_input = TODO_PROMPT + requsetStr + RST_PROMPT
    response = askOllamaDS(user_input, DP_MODEL_NAME)
    print(" - result:\n %s" %str(response))
    if not response: exit()
    print("> Parse TodoList to browser task list")
    respData = json.loads(response)
    initURL = respData['initUrl']
    tasksList = respData['tasksList']
    rest = asyncio.run(main(initURL, tasksList))
    print(" - result:\n %s")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()


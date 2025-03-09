#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        simpleAgentExample.py [python3]
#
# Purpose:     This module is a simple agent example program use the browser-use
#              library and link to local/lan deepseek-r1 service help finish the 
#              task or generate the traffic. Such as open google and search deepseek
#              then go to the official web and summarize the contents in 500 words.
#
# Author:      Yuancheng Liu
#
# Created:     2025/03/07
# version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" The model requests at least deepseek-r1:7b model, for 1.5b most of the tasks 
    will be failed at step2. 
    Lib needed:
    - langchain_ollama: https://pypi.org/project/langchain-ollama/
    - browser-user: https://github.com/browser-use/browser-use/tree/main
    Reference: https://github.com/browser-use/browser-use/issues/442
"""
import os
import asyncio
from langchain_ollama import ChatOllama
from browser_use import Agent

OLLAMA_HOST_IP = "127.0.0.1"
DP_MODEL_NAME = "deepseek-r1:8b"
NUM_CTX = 6000  # for deepseek-r1:7b and 8b use 6000, for higher model use 32000

os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["OLLAMA_HOST"] = "http://%s:11434" % OLLAMA_HOST_IP

#-----------------------------------------------------------------------------
async def main(initUrl, tasksList):
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
        print(result)
    except Exception as e:
        print(f"Error occurred: {e}")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    # An example tasks with 4 steps to open google and search deepseek then go to the official 
    # web and summarize the contents in 500 words.
    initURL = "https://github.com/"
    tasksList = [ "1. Click the seach icon(magnifier) at the top of the page.",
                  "2. Type in 'Deepseek_Local_LATA' in th earch bar.",
                  "2. Select the link LiuYuancehng/Deepseek_Local_LATA in the result",
                  "3. Select README.md file link and scroll down"
                  "4. Base on the readme content in the link, summarize the contents in 100 words"
                 ]
    asyncio.run(main(initURL, tasksList))

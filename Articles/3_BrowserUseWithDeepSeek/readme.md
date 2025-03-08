# Use Local/LAN DeepSeek Service Control Browser

This article will introduce how to use the impressive browser interaction library [browser-use](https://github.com/browser-use/browser-use) with the deepseek LLM Module to create a Agent which can help operate the browser to finish some tasks or generate network traffic with human language. We will introduce step by steps to setup the Ollama Deepseek service in the LAN, then link the agent to the agent to control the browser.

```
# Created:     2025/03/08
# version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]



------

### Environment Introduction

Assume we have 2 or more machine in a LAN, one GPU computer and multiple normal Laptop. Now we want to create an AI Agent which can help control the browser on the Laptop and the GPU computer. The network topology is shown below:



To setup the environment we need to setup Deepseek service on the GPU server and open for the other LAN nodes. Then we install the agent on the operating machine. 












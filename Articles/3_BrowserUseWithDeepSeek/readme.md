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

Assume we have 2 or more machines in a LAN, one GPU computer and multiple normal Laptop. Now we want to create an AI Agent which can help control the browser on the Laptop and the GPU computer. The network topology is shown below:

![](img/s_03.png)

To setup the environment we need to setup Deepseek service on the GPU server and open for the other LAN nodes. Then we install the agent on the operating Laptops. Configuration:

| VM name          | IP address     | Program                 | Human Language Requests                                      |
| ---------------- | -------------- | ----------------------- | ------------------------------------------------------------ |
| Local GPU server | 192.168.50.12  | Ollama [deepseek-r1:8b] | N.A                                                          |
| Laptop01         | 192.168.50.112 | Browser Control Agent   | Google search deepseek and summarize the product features in 500 words. |
| Laptop02         | 192.168.50.113 | Browser Control Agent   | Find the project “**[Deepseek_Local_LATA](https://github.com/LiuYuancheng/Deepseek_Local_LATA)**” and open the readme file, summarize the project in 100 words. |








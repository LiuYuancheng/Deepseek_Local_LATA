# Creating an MCP Agent with Local/LAN DeepSeek Service for Browser Control

In this article, we explore how to build an AI-driven Model Context Protocol (MCP) Agent that can help user to operate a web browser to complete tasks or generate network traffic based on human language instructions. This is achieved using the powerful [browser-use](https://github.com/browser-use/browser-use) library in combination with a Local/LAN configured DeepSeek LLM module service.

We will Introduce step by step through setting up the **Ollama DeepSeek service** in a local LAN environment, integrating it with the MCP Agent, and integrate with browser automation. Since the DeepSeek model runs locally, you won't have to worry about the "deepseek service busy" issues and token fees. Additionally, this setup allows for testing various models or including customized fine-tuned DeepSeek versions to compare the performance of different models.

This article will cover the following sections:

- **Agent Test Scenario Introduction** – Overview of use cases with the demo.
- **Agent Operation Detailed Design** – Technical introduction of how the MCP Agent interacts with the browser.
- **Test Environment Setup** – Configuring the local DeepSeek service and browser interaction module.
- **Test Result Summary and Conclusion** – Evaluating performance, insights, and potential improvements.

```
# Created:     2025/03/08
# version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### MCP Agent Task Scenarios

To demonstrate the capabilities of the MCP Agent, we evaluate its performance through two task scenarios. In each case, the agent receives a human language input string and autonomously interacts with a web browser to retrieve and summarize relevant information. The final output is a concise text summary file.

#### Scenario 1: General Information Search & Summarization

In this scenario, the agent performs a **web search**, gathers relevant content, and generates a structured summary.

Human Language Input string:

```
Google search DeepSeek and summarize the product features in 500 words. 
```

**Agent Operation:** The agent initiates a search query, extracts key details from multiple sources, and compiles a summary. The demo video is shown below:

![](img/s_01.gif)



#### Scenario 2: Targeted Web Content Extraction & Summarization

Here, the agent is tasked with visiting a specific website or project repository, extracting critical details (e.g., a README file), and summarizing the content.

Human Language Input string:

```
Find the project “Deepseek_Local_LATA,” open the README file, and summarize the project in 100 words.
```

**Agent Operation:** The agent locates the repository, extracts the README content, and generates a concise summary.The demo video is shown below:

![](img/s_02.gif)These scenarios showcase how the MCP Agent can autonomously navigate the web, retrieve relevant information, and provide structured summaries—all powered by **local/LAN DeepSeek AI processing** for efficiency and control.



------

### MCP Agent Operation Detailed Design

Before diving into the agent’s detailed design, let's first introduce the **Model Context Protocol (MCP)**. MCP is an open standard that enables secure and standardized connections between AI assistants and various data sources. It allows Large Language Models (LLMs) to access tools and datasets directly, improving their ability to retrieve and process information.

#### Background: Model Context Protocol (MCP)

In an MCP architecture, **MCP Servers** act as lightweight programs that expose specific functionalities through the standardized protocol. The **MCP Service** serves as an intermediary layer, bridging applications or tools with the LLM service. These services include various **MCP Agents**, each providing tools, resources, and prompt templates that enable dynamic interactions between AI systems and clients.

For this project, we develop a simple **MCP Agent** that interacts with a web browser. The **workflow** of this agent is illustrated below:

![](img/s_04.png)

By managing resources with URI-based access patterns and supporting capability negotiation, MCP Servers play a crucial role in extending the functionalities of AI systems, allowing them to perform actions or retrieve information securely and efficiently.

#### Agent Workflow Overview

The agent workflow is very simple as shown below and it operates in three primary steps:

- Step 1: Add Scenario Prompt & Generate a To-Do List
- Step 2: Interact with the Browser
- Step 3: Generate the Final Summary

![](img/s_05.png)

##### Step 1: Add Scenario Prompt & Generate a To-Do List

The agent begins by **modifying the user’s input request** into a structured **To-Do list**. This step ensures that the agent understands how to systematically execute the requested task. Below is an example prompt we append before the user's request:

```
Prompt: I am a beginner using a browser, please list the detailed To-Do steps for...
```

When the user input string `Google search DeepSeek and summarize the product features in 500 words`, the request agent send to AI will be modified to below contents : 

```
I am a beginner using a browser, please help list the detailed To-Do steps for using Google search to find DeepSeek and summarize its product features in 500 words. 

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
```

Then we send the request to the Deepseek to get below ToDo list:

```
tasksList = [ 
	"1. Type in for 'deepseek' in the Google page's search bar",
	"2. Click the first search result",
	"3. Select the first deepseek link in the google search result page"
	"4. Base on the web content in the link, summarize the contents in 500 words"
]
```



##### Step 2: Interact with the Agent Host's Browser

Once the **To-Do list** is generated, the agent executes the steps autonomously using the Playwright library and browser-use interaction module:

1. Open the initial URL (Google search page).
2. Perform sequential actions from the To-Do list (e.g., typing, clicking, navigating).
3. Analyze the current webpage’s content using browser-use and decide whether it satisfies the step requirements.
4. Continue to the next step until all tasks are completed.

Each step is evaluated against real-time webpage analysis to ensure accurate execution. If a step cannot be completed, the agent attempts corrective measures or logs an error.

Reference: 

- Playwright : https://github.com/microsoft/playwright
- Browser-Use: https://github.com/browser-use/browser-use



**Step3: Generate the result summary**

Once all tasks in the To-Do list are completed, the extracted content is sent to DeepSeek LLM for summarization. The Final Verification Prompt Sent to LLM:

```
The result content is: <Extracted text>. 

Can this content fulfill the user's request to Google search DeepSeek and summarize its product features in 500 words? 
```

The final output consists of:

- The extracted content summary.
- DeepSeek’s verification of result accuracy.
- Archived test results for further evaluation.



This design ensures a structured, automated, and accurate approach to executing browser-based tasks with an MCP-powered AI agent. By integrating local DeepSeek LLM processing, users benefit from lower latency, cost efficiency, and customization flexibility compared to cloud-based solutions.

This agent can be further expanded to support different AI models, customized browsing automation, and multi-step reasoning tasks based on user-defined scenarios.

------



### Environment Introduction and setup

Assume we have 2 or more machines in a LAN, one GPU computer and multiple normal Laptop. Now we want to create an AI Agent which can help control the browser on the Laptop and the GPU computer. The network topology is shown below:

![](img/s_03.png)

To setup the environment we need to setup Deepseek service on the GPU server and open for the other LAN nodes. Then we install the agent on the operating Laptops. Configuration:

| VM name          | IP address     | Hardware spec            | OS          | Program                 | Human Language Requests                                      |
| ---------------- | -------------- | ------------------------ | ----------- | ----------------------- | ------------------------------------------------------------ |
| Local GPU server | 192.168.50.12  | Intel-i5, 32GB, RTX-3060 | Windows- 11 | Ollama [deepseek-r1:8b] | N.A                                                          |
| Laptop01         | 192.168.50.112 | Intel-i5, 16GB, RTX-1060 | Windows- 11 | Browser Control Agent   | Google search deepseek and summarize the product features in 500 words. |
| Laptop02         | 192.168.50.113 | Intel-i5, 16GB, no GPU   | Windows- 11 | Browser Control Agent   | Find the project “**[Deepseek_Local_LATA](https://github.com/LiuYuancheng/Deepseek_Local_LATA)**” and open the readme file, summarize the project in 100 words. |



#### Configure the DeepSeek Service on GPU Node

On the GPU server, follow below steps to setup the deepseek service with the Ollama and make it open to other nodes in the subnet. 

##### Step 1 Install Ollama

Download **Ollama** from the official website: https://ollama.com/download, and select the installation package for your operating system. 

##### Step 2 Download and Run DeepSeek-R

For my local configuration, I use a 3060GPU(12GB), so I can try the 8b. We can use the `ollama pull to down load the model`  or just use the run command, if the module is not download, Ollama will auto download it:

```
ollama run deepseek-r1:8b
```

##### Step 3 Expose the DeepSeek service to LAN

**Setting environment variables on Mac**

If Ollama is run as a macOS application, environment variables should be set using `launchctl`:

1. For each environment variable, call `launchctl setenv`.

```
launchctl setenv OLLAMA_HOST "0.0.0.0:11434"
```

2. Restart Ollama application.

**Setting environment variables on Linux**

If Ollama is run as a systemd service, environment variables should be set using `systemctl`:

1. Edit the systemd service by calling `systemctl edit ollama.service`. This will open an editor.

2. For each environment variable, add a line `Environment` under section `[Service]`:

   ```
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0:11434"
   ```

3. Save and exit.

4. Reload `systemd` and restart Ollama:

   ```
   systemctl daemon-reload
   systemctl restart ollama
   ```


**Setting environment variables on Windows**

On Windows, Ollama inherits your user and system environment variables.

1. First Quit Ollama by clicking on it in the task bar.
2. Start the Settings (Windows 11) or Control Panel (Windows 10) application and search for *environment variables*.
3. Click on *Edit environment variables for your account*.
4. Edit or create a new variable for your user account for `OLLAMA_HOST`, set its value to `0.0.0.0`
5. Click OK/Apply to save.
6. Start the Ollama application from the Windows Start menu.

>  Reference : https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server



#### Configure the Agent on Operation Node

The operation node need to install a browser and python (>=3.11), then install the related lab.

##### Step1 :  Install the python lib

Install the langchain-ollama 0.2.3 with pip

```
pip install langchain-ollama
```

Install the lib browser-use with pip

```
pip install browser-use
```

Install the playwright 

```
playwright install
```



##### Step2 : Configure the agent parameters



------

> last edit by LiuYuancheng (liu_yuan_cheng@hotmail.com) by 18/03/2025 if you have any problem, please send me a message. 
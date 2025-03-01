# Use a Simple Web Wrapper to Share the Local Deep Seek-R1 Model Service to LAN Users

In the previous article [Deploying DeepSeek-R1 Locally with a Custom RAG Knowledge Data Base](../1_LocalDeepSeekWithRAG/), we introduced the detail steps about deploying DeepSeek-R1:7b locally with a custom RAG knowledge database on a desktop with RTX3060. Once the LLM deepseek-r1:7b is running on the local GPU-equipped computer, a new challenge emerges: I can only use the LLM service on the GPU computer, what if I want to use it from other device in my LAN, is there any way I can access it from a mobile device or share this service with friends in the same network? By default, Ollama only opens its API to the localhost, meaning that external devices in your LAN cannot easily interact with the model. Changing the configuration to expose the API fully may solve connectivity issues—but it also removes the safeguards that limit potentially risky operations, such as creating complete conversational chains. The user need a controlled interface that:

- Limits access to only the necessary functions (e.g., sending questions and receiving responses).
- Provides an intuitive web-based interface for mobile devices.
- Enables programmatic API calls with controlled access.
- Acts as a central hub for connecting to multiple GPU servers and different DeepSeek LLM versions.

```
# Created:     2025/02/28
# version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### Introduction

This article explores how a simple Python-Flask-based web wrapper acts as a controlled “bridge” between the local DeepSeek service and LAN users and fullfill below five request:

- Connect multiple local GPU servers running different DeepSeek LLM versions within a subnet.
- Limit the Ollama API access for the user.
- Enable remote testing and performance comparison of LLM responses.
- Provide controlled access to specialized/fine-tuned models without exposing server credentials.
- Facilitate prompt engineering by modifying user queries before model submission.

The use case flow diagram is shown below:



By implementing this web wrapper, users gain secure, controlled access to DeepSeek models through a user-friendly interface, suitable for both web-based and programmatic interaction. This article provides an overview of the Flask wrapper, explores practical use case scenarios, and explains how to configure Ollama to expose the service for LLM API calls effectively.



------

### Introduction of the DeepSeek Flask Web Wrapper 

This application provides a user-friendly interface for remote access to multiple LLM models running on different GPUs ( using the Ollama host the model). The chatbot is designed for the following purposes:

- Testing the functionality of GPU-hosted Ollama LLM instances.
- Allowing shared access to specialized LLMs (fine-tuned or RAG embedded) without requiring direct SSH access.
- Comparing the performance of different LLM models, such as DeepSeek R1-1.5B and DeepSeek R1-7B, in response to the same query.

The chat bot web UI is shown below :

![](img/s_03.png)

Users can interact with the chatbot via a web-based UI that includes a model selection dropdown in the navigation bar. The Mobile device view is shown below:

![](img/s_04.png)

The remote API function call (Http `GET` ) is show below:

```python
resp = requests.get("http://127.0.0.1:5000/getResp", json={'model':'localhost-DS1.5b', 'message':"who are you"})
print(resp.content)
```

Program source repo: https://github.com/LiuYuancheng/Deepseek_Local_LATA/tree/main/Testing/1_Simple_Flask_Deepseek_ChatBot



------

### Expose Ollama Service API in LAN

Using the web wrapper, you can safely expose your Ollama service to LAN users. Instead of directly modifying Ollama’s configuration—which would expose all API functions—the wrapper acts as an intermediary. 

For example, a typical API request via the wrapper might look like this:

```
curl http://localhost:11434/api/generate -d '{ "model": "deepseek-r1:1.5b", "prompt": "Why is the sky blue?"}'
```

This controlled access ensures that while users can send questions and receive answers, but we do not have the ability to modify internal system states or access logs and debugging details and if you use a mobile device such as phone or Ipad which are not easy to create a command line, it will be inconvenient to use the Ollama server. 

To configure the Ollama server for different OS, 

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
4. Edit or create a new variable for your user account for `OLLAMA_HOST`, set its value to 0.0.0.0
5. Click OK/Apply to save.
6. Start the Ollama application from the Windows Start menu.

>  Reference : https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server



------

### Use Case Scenarios

#### Use Case Scenario 01: Secure Sharing on a Headless GPU Server

**Problem:**
Imagine you have a GPU server running DeepSeek on an Ubuntu system without a desktop environment. You want to share the LLM service with others on the same subnet without exposing SSH credentials or the full Ollama API functionality.

You want to limited the access such as only allow response without showing deepseek's "thinking" log and you also want to add some customized filter for the user's request and LLM's response.

The use case scenario diagram is shown below:



**Solution:**
The web wrapper allows you to:

- Expose only the necessary API endpoints (e.g., sending questions and receiving answers) on port 5000.
- Prevent direct access to sensitive parts of the Ollama API.
- Provide a clean web interface accessible from any device on the network, including mobile devices.
- Provide a limited http API for the program 



### Use Case Scenario 02: Customized Query Handling Based on User Expertise

**Problem:**
Different users have different levels of expertise. A beginner might need a simplified explanation of an algorithm like bubble sort, whereas an expert might require a detailed technical example.

**Solution:**
The wrapper can intercept user queries and append context-specific prompts before sending the query to the LLM. For example:

- **Beginner Query:** The system modifies “What is bubble sort?” to “I am new to sorting algorithms. What is bubble sort?”
- **Advanced Query:** It transforms the question into “I am an expert and need a Python example. What is bubble sort?”

This dynamic prompt engineering tailors responses to the user’s needs.





Assume you have one GPU server running DeepSeek on an Ubuntu server without a desktop environment (which is difficult for the user to use the Desktop application tool such as anything LLM and the LM-studio), now you want to share the LLM service to the people in the same subnet, you may meet these problems:

1. You don't want to share people the GPU server ssh login credentials. 
2. You don't want to open all the Ollama service API to people, you want to limited the access such as only allow response without showing deepseek's "thinking" log. 
3. When you expose the Ollama API, other people can use command line curl to generate a request as , but if people want to use mobile device 
4. You want to add some customized filter for the user's request and LLM's response.

This chatbot allows external users to query the model without needing SSH access. The chatbot web host runs on the server and exposes port 5000 for multiple users within the same network and the scenario workflow diagram is shown below:



#### Use Case Scenario 02

The application allow the admin to modify user queries by appending relevant prompt context before send to the LLM. For example, user ask LLM to explain what is bubble sort algo, based on different users, the program can add the prompt to change the question to :

- A beginner query: "I am new to sorting algorithms. What is bubble sort?"
- An advanced query: "I am an expert and need a Python example. What is bubble sort?"

This allows for more tailored responses based on user expertise.

The scenario workflow diagram is shown below :



#### Use Case Scenario 03

For environments with multiple GPU servers running different LLM models (e.g., DeepSeek R1-1.5B, DeepSeek R1-7B, DeepSeek Coder V2), the chatbot serves as a bridge between users and these models. Users can compare responses from different models via a centralized UI. The scenario workflow diagram is shown below :



https://github.com/ollama/ollama/blob/main/docs/api.md

Reference: 
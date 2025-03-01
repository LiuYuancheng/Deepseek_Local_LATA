# Use a simple web wrapper to share the Local Deep Seek-R1 Model Service to LAN users

In the previous article [Deploying DeepSeek-R1 Locally with a Custom RAG Knowledge Data Base](../1_LocalDeepSeekWithRAG/), we have deploy the LLM deepSeek-r1:7b in a local computer with GPU, now what if we want to share the deepseek-R1 service to your friend in the same subnet or if you want to use your phone to access the deepseek LLM model or access multiple GPUs in the subnet. When you configured the Ollama, it provide the API for you to interact with the module now is running, but by default it is only open for the localhost, the other computer can not call it if you don't change the Ollama configuration and once our change the config, all the API are exposed to outside, what if you want to limit the access (such as only allow send question instead of create the conversating chain) ? There is a very simple way to create a wrapper web host program to call the Ollama API and provide a web interface for your mobile device and a get API interface for your program.



We can create a simple python-flask-based chatbot as a "bridge" to connect to multiple local GPU servers within the same subnet for filling below four requirements :

- Connect multiple local GPU servers running different DeepSeek LLM versions within a subnet.
- Limit the Ollama API access for the user.
- Enable remote testing and performance comparison of LLM responses.
- Provide controlled access to specialized/fine-tuned models without exposing server credentials.
- Facilitate prompt engineering by modifying user queries before model submission.

In this article , we will give a short introduction about the flask wrapper program and the use case scenarios it can help the user to solve. We will also show how to configure Ollama to expose the service for LLM model Ollama-API call.



------

### Introduction of the Flask web wrapper 

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





------

### Expose Ollama Service For LAN User call Ollama API

With our using the warpper, we can also change the Ollama setting to expose the LLM service for LAN user, the user can use curl to send the request and get the response as shown below:

```
curl http://localhost:11434/api/generate -d '{ "model": "deepseek-r1:1.5b", "prompt": "Why is the sky blue?"}'
```

Ollama API document link : https://github.com/ollama/ollama/blob/main/docs/api.md

But if you use a mobile device such as phone or pad which are not easy to create a command line, it will be inconvenient to use the Ollama server. 

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



------

#### Use Case Scenario 01

Assume you have one GPU server running DeepSeek on an Ubuntu server without a desktop environment (which is difficult for the user to use the Desktop application tool such as anything LLM and the LM-studio), now you want to share the LLM service to the people in the same subnet, you may meet these problems:

1. You don't want to share people the GPU server ssh login credentials. 
2. You don't want to open all the Ollama service API to people, you want to limited the access such as only allow response without showing deepseek's "thinking" log. 
3. When you expose the Ollama API, other people can use command line curl to generate a request as , but if people want to use mobile device 
4. You want to add some customized filter for the user's request and LLM's reponse.

This chatbot allows external users to query the model without needing SSH access. The chatbot web host runs on the server and exposes port 5000 for multiple users within the same network and the scenario workflow diagram is shown below:



#### Use Case Scenario 02

The application allow the admin to modify user queries by appending relevant prompt context before send to the LLM. For example, user ask LLM to explain what is bubble sort algo, based on different users, the program can add the prompt to change the question to :

- A beginner query: "I am new to sorting algorithms. What is bubble sort?"
- An advanced query: "I am an expert and need a Python example. What is bubble sort?"

This allows for more tailored responses based on user expertise.

The scenario workflow diagram is shown below :



#### Use Case Scenario 03

For environments with multiple GPU servers running different LLM models (e.g., DeepSeek R1-1.5B, DeepSeek R1-7B, DeepSeek Coder V2), the chatbot serves as a bridge between users and these models. Users can compare responses from different models via a centralized UI. The scenario workflow diagram is shown below :



Reference: https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server
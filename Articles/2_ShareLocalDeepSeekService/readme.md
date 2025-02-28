# Use a simple web wrapper to share the Local Deep Seek-R1 Model Service 

In the previous article [Deploying DeepSeek-R1 Locally with a Custom RAG Knowledge Data Base](../1_LocalDeepSeekWithRAG/), we have build the deepSeek-r1 in a local computer with GPU, now if we want to share the deepseek-R1 service to your friend in the same subnet or if you want to use your phone to access the deepseek LLM model or access multiple GPUs in the subnet. There is a very simple way to create a wrapper web host program to call the Ollama API and provide a web interface for your mobile device.





------

Step1: 

Ollama server can be configured with environment variables.

### Setting environment variables on Mac



If Ollama is run as a macOS application, environment variables should be set using `launchctl`:

1. For each environment variable, call `launchctl setenv`.

   ```
   launchctl setenv OLLAMA_HOST "0.0.0.0:11434"
   ```

   

2. Restart Ollama application.

### Setting environment variables on Linux



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

   

### Setting environment variables on Windows



On Windows, Ollama inherits your user and system environment variables.

1. First Quit Ollama by clicking on it in the task bar.
2. Start the Settings (Windows 11) or Control Panel (Windows 10) application and search for *environment variables*.
3. Click on *Edit environment variables for your account*.
4. Edit or create a new variable for your user account for `OLLAMA_HOST`, `OLLAMA_MODELS`, etc.
5. Click OK/Apply to save.
6. Start the Ollama application from the Windows Start menu.





Reference: https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server
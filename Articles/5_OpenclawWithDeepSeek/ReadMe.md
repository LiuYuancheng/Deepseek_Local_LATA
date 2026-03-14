# Deploy Multiple OpenClaw AI Assistant Cluster With Local GPU Running Qwen3.5 or DeepSeek-r1

**Project Design Purpose** : In this article, I will share the design and deployment of a distributed multiple OpenClaw AI assistants cluster connected to locally hosted Large Language Models (LLMs) running on a GPU-enabled server or gaming laptop.  Instead of relying on cloud-based AI APIs. I used the open-source models such as `Qwen 3.5` or `DeepSeek-R1` to provide inference services for multiple OpenClaw agents, so we can reduces cloud AI token costs and compare the performance of different LLM model.

In this AI Assistant Cluster System, the GPU server acts as the centralized AI reasoning engine, and the distributed agents (computers run OpenClaw communicate with the LLM server over the network) execute tasks, collect system information, and interact with the model for decision-making. This article covers the following three sections:

- Setting up the open-source LLM model on a GPU server or gaming laptop/computer.
- Configuring and exposing the LLM inference service so that it can be accessed by remote OpenClaw nodes.
- Deploying OpenClaw agents on target computers or laptops and connecting them to the centralized LLM service

```python
# Author:      Yuancheng Liu
# Created:     2026/03/10
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
```

 **Table of Contents**

[TOC]

------

### 1. Introduction

In this project, the OpenClaw cluster design separates LLM inference services from agent execution nodes. A GPU-enabled server or gaming laptop inside the internal network hosts the LLM models through Ollama, which provides a lightweight local API service for running open-source models. Multiple computers or laptops running OpenClaw agents connect to this centralized LLM service to perform reasoning and task execution.

#### 1.1 Abstract and Background 

Over the past month, the personal AI assistant [OpenClaw](https://openclaw.ai/) has rapidly become one of the most discussed open-source AI projects. Its rapid rise in popularity has led to a wave of new services and businesses around the ecosystem. For example in China, many individuals and organizations now offer installation services, remote deployment support, and children training courses on how to use OpenClaw effectively. Some companies even market “all-in-one OpenClaw machines/Laptop” preinstalled with OpenClaw and local large language models. And the major technology companies such as **Tencent** have also begun offering related OpenClaw deployment services: 

![](img/s_03.png)

One of the key reasons behind the rapid adoption of OpenClaw is its "skills" based architecture, which enables the agent to call multiple tools and reasoning steps dynamically when executing tasks. While this design significantly enhances the intelligence and automation capability of the AI assistant, it also dramatically increases the number of LLM API calls. As a result, token consumption can be tens or even hundreds of times higher than that of traditional single-prompt AI agents. If you don't need to do complex tasks and have a GPU server or station such as Nvidia GB10 Spark or a gaming laptop with RTX-series 50XX graphics cards, you can link your OpenClaw to the open source LLM like **Qwen 3.5** or **DeepSeek‑R1** running on these local machine to save the costs especially when you have several OpenClaw Agents running on different device.



#### 1.2 System Architecture

The overall system follows a distributed agent + centralized inference architecture as shown below diagram. so it allows a single GPU server to support **multiple OpenClaw agents simultaneously**, forming a lightweight **AI agent cluster** while keeping hardware and cloud costs low.

![](img/s_04.png)

The Architecture includes four layers:

- **LLM Host Layer** :  A GPU server or AI/gaming laptop hosts open-source LLM models through Ollama.
- **Network Access Layer** : Secure access is provided via SSH port forwarding through routers, gateways, or jump hosts.
- **Agent Layer** : Multiple OpenClaw agents run on user laptops or computers and send LLM requests through the forwarded port.
- **User Interaction Layer** : Users interact with the agents through their local system or messaging platforms such as mobile applications.

To improve security and avoid directly exposing the LLM service to the public network, the architecture uses SSH port forwarding. The Ollama inference service runs locally on port 11434, and this port is forwarded securely to authorized OpenClaw nodes through SSH (port 22). So with this approach:

- The LLM API is not exposed directly to the network.
- Only authenticated users with valid SSH accounts can access the model service
- External users can connect through a gateway, router, or jump host
- Access control can be easily managed by enabling or disabling user accounts on the GPU server



------

### 2. Setting Up the OpenClaw Compatible Open-source LLM on GPU

All the configurations in this section should be performed on the **GPU server** that will host the Large Language Model (LLM). 

To run OpenClaw locally without relying on cloud APIs, we first need to deploy a compatible open-source LLM. One of the easiest ways to manage and run LLMs locally is by using **Ollama**, which provides a lightweight runtime for downloading, managing, and serving open-source LLMs with a simple command-line interface.

#### 2.1 Install Ollama on the GPU Server

To install Ollama on your GPU server. You can download it from the official page:https://ollama.com/download/linux

For most Linux systems, the installation can be completed using: 

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

After installation, verify that the service is working and start the service

```
ollama --version
ollama serve
```

Ollama will expose a **local API endpoint** (default port `11434`) that OpenClaw agents can later connect to.

#### 2.2 Pull OpenClaw Compatible Open-Source Models

OpenClaw supports multiple open-source LLMs as long as they provide tool-calling and reasoning capabilities. Through Ollama, users can easily deploy a variety of models depending on their available GPU resources.

Below is a reference table of commonly used models compatible with OpenClaw:

| **Model Name**       | **Parameter Size** | **Best Use Case**                        | **Context Window** | **Recommended Hardware**            |
| -------------------- | ------------------ | ---------------------------------------- | ------------------ | ----------------------------------- |
| **GLM-5**            | 744B (MoE)         | Complex debugging & multi-step coding    | 200K               | Enterprise (A100/H100) or Cloud API |
| **GPT-OSS-120B**     | 120B               | High-stakes reasoning & data privacy     | 128K               | Dual RTX 6000 / Mac Studio (Ultra)  |
| **DeepSeek-V3.2**    | 671B (MoE)         | General-purpose high-speed agentic tasks | 128K               | Cloud API / Multi-GPU Server        |
| **Kimi-K2.5**        | 1T (MoE)           | Vision + Text (multimodal agent tasks)   | 1M                 | Cloud API / 8x H100                 |
| **Qwen 3.5 (32B)**   | 32B                | Best balance for high-end consumer GPUs  | 128K               | RTX 4090 (24GB VRAM)                |
| **Llama 4 Maverick** | 70B                | Reliable daily assistant & tool calling  | 128K               | Mac Studio / Multi-RTX 3090         |
| **Qwen 3.5 (14B)**   | 14B                | Entry-level local agent tasks            | 64K                | RTX 3060/4070 (12GB+ VRAM)          |
| **MiMo-V2-Flash**    | ~30B (Active)      | Ultra-fast "thinking" & long research    | 256K               | RTX 4080/4090                       |

You can also browse compatible models directly from the Ollama model repository. On the Ollama website, check the Application tag to verify whether a model supports OpenClaw tool-calling functionality as shown below:

![](img/s_05.png)

#### 2.3 Downloading the LLM Model

In this experiment, the GPU server is equipped with **RTX 3060** and **RTX A5000** GPUs. Therefore, two models were selected:

- **Qwen3.5-35B-A3B-FP8** for high-quality reasoning
- **DeepSeek-R1-Tool-Calling-14B** for lightweight tool-calling tasks

Pull and run the Qwen3.5-35B-A3B-FP8

```
ollama pull qwen3.5:35b
ollama run qwen3.5:35b
```

Pull and run the deepseek-r1-tool-calling:14b model:

```
ollama pull MFDoom/deepseek-r1-tool-calling:14b
ollama run deepseek-r1-tool-calling:14b
```

Once the models are downloaded, Ollama will automatically load them when they are first called through the API.

#### 2.4 Running the Model as a Background Service(optional)

After installation, the Ollama service typically runs in the background. When an API request is sent to the Ollama endpoint, the required model will automatically be loaded into GPU memory.  The first API request may take longer because the model must be initialized. To reduce this latency, you can configure the model to run as a **persistent service**.

On Linux systems, a simple **systemd service** can be created to keep the model loaded, as example is shown below:

```bash
[Unit]
Description=ollamaQwen35B_service
After=network.target
[Service]
ExecStart=ollama run qwen3.5:35b
WorkingDirectory=/home/<username>/ollama
User=root
Restart=always
RestartSec=5
StandardOutput=null
StandardError=null
[Install]
WantedBy=multi-user.target
```

The copy the file `ollamaQwen35B_service.service` to the `/etc/systemd/system` director and start the service: 

```
sudo systemctl start ollamaQwen35B_service
```

After completing this step, the GPU server will host a locally running LLM inference service.



------

### 3. Forward the Ollama LLM Service to the User's Computer

All the configurations in this section should be performed on the computer or laptop where the OpenClaw agent will be installed.

Instead of exposing the Ollama API directly to the network (which may introduce security risks), we can use SSH port forwarding to securely tunnel the service to the local machine, so the OpenClaw agent running on a user’s laptop or workstation can interact with the LLM service as if it were running locally.

For security and access control, it is recommended to create a **dedicated user account** on the GPU server that will only be used for forwarding the LLM service traffic, for example I create a normal user `llmService` on the GPU. 

#### 3.1 Create an SSH Port Forwarding Tunnel

On the **target computer or laptop** where OpenClaw will run, execute the following SSH command to create a tunnel between the local machine and the GPU server.

If both machines are located in the **same subnet or internal network**, run:

```bash
ssh -L localhost:11434:localhost:11434 llmService@<GPU_Server_IP_Address>
```

This command creates a secure tunnel that maps:

```
Local Computer:   localhost:11434
        │
        │ (SSH Tunnel)
        ▼
GPU Server:       localhost:11434 (Ollama API)
```

#### 3.3 Test the Ollama API Connection

Once the SSH tunnel is established, you can verify the connection by sending a test request to the Ollama API.

Linux / macOS

```
curl http://localhost:11434/api/chat -d "{\"model\":\"qwen3.5:9b\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}"
```

Windows PowerShell

```
curl.exe http://localhost:11434/api/chat -d '{"model":"qwen3.5:9b","messages":[{"role":"user","content":"Hello!"}]}'
```

If the connection is working correctly, the API will return a JSON response generated by the LLM model as shown below:

![](img/s_06.png)

#### 3.4 Connecting Through a Jump Host (Optional)

In some environments, the GPU server may reside inside a **restricted internal network** and cannot be accessed directly from the user’s computer. In this case, a **jump host (bastion server)** can be used to relay the SSH connection.

On the target computer, run the following command:

```
ssh -L localhost:11434:localhost:11434 -J <jumphostUser>@<Jump_Host_IP> llmService@<GPU_Server_Ip_Address>
```

This creates the following connection path:

```
User Computer
      │
      ▼
Jump Host (SSH Gateway)
      │
      ▼
GPU Server (Ollama LLM Service)
```



------

























https://blog.csdn.net/u010026928/article/details/158582591

https://www.nvidia.com/en-sg/products/workstations/dgx-spark/

https://news.hubeidaily.net/pc/c_5240661.html

https://www.pingwest.com/w/311980

https://xueqiu.com/5680323216/377215813

https://www.bilibili.com/video/BV1vdwczDEoR/?spm_id_from=333.1007.tianma.2-1-4.click&vd_source=5ff50dfdd1613df97004d3548592e433


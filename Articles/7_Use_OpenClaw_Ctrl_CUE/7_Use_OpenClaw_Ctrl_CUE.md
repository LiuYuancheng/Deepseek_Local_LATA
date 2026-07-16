# Use Open-Claw to Deploy and Monitor the Cluster User Activities Emulator for Cyber Exercises

In the previous article ["Cluster User Emulation System (CUE Agent) for Automated Blue Team and Red Team Activities in Cyber Exercises"](https://www.linkedin.com/pulse/cluster-user-emulation-system-cue-agent-auto-blue-team-yuancheng-liu-vngtc) ,  I introduced the **Cluster User Emulation System (CUE)** which is a framework can be used to automatically generate realistic Blue Team and Red Team user activities for cyber exercises. By emulating the daily behavior of legitimate users as well as attacker operations, the system helps create more realistic and dynamic cyber range environments while significantly reducing the manual effort required from exercise operators.

This article will introduce the details about how to use general-purpose AI agent (such as Open-Claw) to help the green team to configure and deploy the system in the cyber exercise. This article includes four main parts: 

- **Basic System Deployment** – Deploying the CUE system within a cyber exercise infrastructure, including the required components and network architecture.
- **System Execution Workflow** – Show the execution process after deployed in the infra includes the communication flow and interactions between the System Orchestrator and distributed CUE agents during operation.
- **AI-Assisted User Profile Generation** – Demonstrating how Open-Claw interprets API documentation to automatically generate realistic simulated user profiles and activity procedures.
- **AI-Assisted Remote Deployment** – Explaining how Open-Claw remotely installs, configures, and manages CUE agents on target machines, enabling large-scale automated deployment with minimal operator intervention.

```python
# Author:      Yuancheng Liu
# Created:     2026/07/16
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     GNU Lesser General Public License v3.0
```

**Table of Contents**

[TOC]

------

### 1. System Deployment

The **Cluster User Emulation (CUE) System** is designed with a distributed architecture that enables deployment across a wide range of computing environments, including a single workstation, multiple physical servers, virtual machines (VMs), Software Defined Network (SDN) environments, and lightweight IoT devices such as Raspberry Pi. This flexibility allows the system to emulate realistic user activities in cyber exercises ranging from small laboratory environments to large-scale enterprise cyber ranges.

The deployment network topology diagram is shown below:

![](img/s_03.png)

#### 1.1 Deploy Activities Modules Repository

The **Activities Generation Modules Repository** stores the reusable action modules that generate simulated user behaviors, including network traffic, application usage, human-computer interactions, and operating system operations. The repository can be deployed in one of two modes either in a file server or on one local VM/Node:

- **Centralized Repository** – Hosted on a database or file server that is accessible by all emulator nodes within the cluster.
- **Local Repository** – Installed on each emulator node, allowing the required activity modules to be imported locally without relying on network connectivity.

Supporting both deployment models provides greater flexibility for different cyber exercise environments while simplifying module updates and maintenance.

#### 1.2 Deploy User Action Emulator

The **User Action Emulator** is deployed on every endpoint that participates in the cyber exercise, including physical computers, virtual machines, cloud instances, or embedded devices. Each emulator executes scheduled user activities according to its assigned user profile while communicating with the Orchestrator to report execution status.

A typical emulator deployment package contains the following files:

| File                          | Description                                                  |
| ----------------------------- | ------------------------------------------------------------ |
| `setup.bat`                   | Installs the required software, Python runtime, libraries, and dependencies on the target machine. |
| `scheduleCfg.txt`             | Configuration file containing emulator parameters, such as the local repository path, Orchestrator IP address, authentication settings, logging configuration, and other runtime options. |
| `actorFunctions_<xxxxx>.py`   | Imports the required Activity Generation Modules and defines the functions used to execute simulated user activities. |
| `scheduleProfile_<xxxxxx>.py` | Defines the user activity schedule, including the timeline, execution sequence, event intervals, and scenario-specific behaviors. |

After deployment, each emulator automatically loads its configuration, imports the required activity modules, connects to the Orchestrator, and begins executing scheduled tasks according to the assigned simulation profile.
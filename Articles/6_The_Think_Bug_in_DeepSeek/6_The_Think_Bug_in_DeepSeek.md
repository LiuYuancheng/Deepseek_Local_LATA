# The Special Token `<think>` Problem/Bug of Latest DeepSeek LLM 

**us English** | [cn 中文](6_The_Think_Bug_in_DeepSeek_CN.md)

Recently the users observed an issue/bug in the latest version of the DeepSeek LLM: during testing, it was found that when specific incomplete or special tokens such as `<think>` or `<think` are included in the user prompt, the model may produce highly unstable responses, severe hallucinations, abnormal reasoning outputs, or unexpected behavior.

![](img/title.png)

The purpose of this article is to document the issue, demonstrate how the behavior can be reproduced, and discuss the verification experiments conducted to better understand the possible cause of the problem. This article is organized into three main sections:

- **Introduction and Replication of the `<think>` Token Problem** : A walkthrough of the discovered issue, including example prompts and observed abnormal model behaviors.
- **Verification Experiment Design and Result Analysis**: Introduction of the local verification experiment setup, testing methodology, collected outputs, and analysis of the verification results.
- **Discussion and Some Assumptions** :  Discussion and assumptions related to tokenizer behavior, prompt parsing mechanisms, and potential security implications.

```python
# Author:      Yuancheng Liu
# Created:     2026/05/18
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### 1. Bug Introduction and Replication

#### 1.1 Bug Introduction

Around three days ago (16/05/2026), multiple users reported abnormal behavior when interacting with the DeepSeek LLM model web chat. During testing, users found that if the prompt only contained the special token `<think>` or the incomplete token `<think`, the model could unexpectedly generate unrelated responses, hidden reasoning traces, or answer questions that were never asked by the current user.

In several cases, the generated content appeared to be logically structured and contextually meaningful .Because some of the responses looked like fragments of valid user queries, online discussions quickly raised concerns regarding possible cross-session data leakage or inference cache exposure.

At the time of discovery, several possible explanations were discussed by the community:

- **GPU cache or load balancer cache leakage** : Some users suspected that the inference server cache was not being properly cleared between requests, potentially causing fragments of other users’ prompts or reasoning traces to appear in unrelated sessions.
- **Tokenizer or prompt parser bug** : Others believed the issue was related to the tokenizer or internal prompt formatting mechanism, where the `<think>` token may accidentally trigger hidden reasoning-mode behavior or special internal instructions.
- **Special token parsing issue** : Another assumption was that `<think>` might be treated as a reserved control token used internally by the model during chain-of-thought generation, causing unstable outputs when directly exposed to user input.



#### 1.2 Bug Replication

The bug is relatively easy to reproduce. In this experiment, the official DeepSeek web interface was used with the following configuration:

- **Online Search Function:** Disabled
- **Deep Think Function:** Enabled

The testing method was straightforward: the input prompt only contained the text `<think>` and the returned result was recorded. Seven independent test rounds were conducted using separate chat sessions without any conversation history or contextual prompts.

Now we send the word `<think>` and check the answer and we test several around (seven individual chat without any context)

**1.2.1 Test 01 [no bug]**

As shown below, the model correctly interpreted the input and returned a normal explanation of the `<think>` token.

![](img/s_02.png)

**1.2.2 Test 02 [bug appeared]**

In this round, the model generated a completely unrelated response. When the reasoning trace was expanded, it showed that the model was attempting to answer the question *“How to draw a cube?”*, even though this question had never been asked in the current session.

![](img/s_03.png)

**1.2.3 Test 03 [no bug]**

In this test, the model treated the `<think>` token as a system-level instruction or reserved keyword, which is a more reasonable and expected behavior.

![](img/s_04.png)

**1.2.4 Test 04 [bug appeared]** 

In this round, the model unexpectedly attempted to answer the mathematical question:

> “Is it true that all n-dimensional vector spaces over a field F are isomorphic to the space of n-tuples F^n?”

The generated content was unrelated to the user input.

![](img/s_05.png)

**1.2.5 Test 05 [bug appeared]**

In this round, the model generated the sentence:

> “There is an additional constraint: the aja_jaj are distinct positive integers.”

The output appeared to be a fragment/part  extracted from a larger mathematical or algorithm-related prompt (as shown below)

![](img/s_07.png)

**1.2.6 Test 06 [no bug]**

This round produced a relatively normal and reasonable response. The model indicated that it was preparing its reasoning process before answering the user request.

![](img/s_06.png)

**1.2.7 Test 07 [bug appeared]**

In the final round, the model attempted to answer an unrelated programming question ""We have a dataset of numbers representing the number of messages sent per day by a user. Define a function calculate_limits(mean, std_dev) that returns the lower and upper bounds of the acceptable range based on the 68-95-99.7 rule.", and even started generating Python code automatically as shown below:

![](img/s_08.png)

Based on the seven independent tests, (4/7) sessions generated unrelated or abnormal responses. This indicates a relatively high probability that the `<think>` token can trigger unstable model behavior under the tested configuration.



#### 1.3 Official Explanation and Initial Discussion

Today 19/05/2026, the official DeepSeek account released an explanation (“关于 `<think>` 字符触发模型异常回复的说明”). According to the official explanation, the issue was caused by a special token triggering abnormal hallucination behavior inside the model, and the company stated that there was no evidence of private information leakage.(As shown below)

![](img/s_09.png)

Although the official explanation attributes the problem to hallucination triggered by special tokens, an important question still remains:

> If the abnormal behavior is purely caused by tokenizer or model-level hallucination, would the same issue also appear in a completely isolated local deployment of the DeepSeek model running on a standalone GPU server without shared inference infrastructure?

To further investigate this possibility, additional verification experiments were conducted using locally deployed DeepSeek models.



------

### 2. Verification Experiment Setup and Result

Based on DeepSeek’s official explanation, the abnormal behavior is caused by hallucination triggered by a special token. If this explanation is correct, then I guess the same behavior should also be reproducible on a completely isolated local deployment of the DeepSeek model running on a standalone GPU server without any shared cloud inference infrastructure or request cache system.

#### 2.1 Experiment Platform

The experiment platform used in this test was an NVIDIA GB10 DGX-Spark AI workstation with 128 GB shared memory. The hardware resources were sufficient to locally deploy and run the larger DeepSeek-R1 32B model through Ollama.

The experiment environment included:

- **Hardware Platform:** NVIDIA GB10 DGX-Spark
- **LLM Framework:** Ollama
- **Model Used:** `deepseek-r1:32b`
- **Execution Mode:** Fully local inference without external API access

The main objective of the experiment was to determine whether the `<think>` token alone could consistently trigger the same abnormal hallucination behavior observed in the official DeepSeek web service.

#### 2.2 Experiment Program

A simple Python test program was created to repeatedly send the `<think>` token to the locally deployed model and record both the reasoning trace and final response.

The experiment code is shown below:

```python
from ollama import chat
for i in range(10):
    print("Test Around %s" %str(i))
    response = chat(
        model='deepseek-r1:32b',
        messages=[{'role': 'user', 'content': '<think>'}],
        think=True,
    )
    print('Thinking:\n', response.message.thinking)
    print("Response from Model:")
    print(response.message.content)
```

#### 2.3 Experiment Result

The experiment was executed multiple times to observe whether the abnormal behavior could be reproduced under a fully local deployment environment.

**2.3.1 Execution Round 01**

![](img/s_10.png)

![](img/s_11.png)

In the first execution round, all ten responses were directly related to the `<think>` token itself. The model consistently identified the token as either a special keyword, formatting tag, or incomplete instruction.

No unrelated questions, hidden prompts, or abnormal reasoning traces were observed during this round.

The responses showed that the model correctly interpreted or safely handled the `<think>` token without generating random hallucinated content.

**2.3.2 Execution Round 02**

The experiment was then repeated using the same configuration and input.

![](img/s_12.png)

In this round, the model again correctly handled the `<think>` token in all test cases. Most responses indicated that the input was incomplete, unclear, or insufficient to generate a meaningful answer.

The model either ignored the token safely or treated it as a formatting-related placeholder rather than generating unrelated responses.

No abnormal outputs similar to those observed in the DeepSeek web service were reproduced.

**2.3.3 Execution Round 03**

The experiment was repeated for a third round.

![](img/s_13.png)

![](img/s_14.png)

Similar to the previous rounds, the model consistently handled the `<think>` token correctly. The generated responses remained stable and contextually reasonable throughout all test iterations.

Again, there were no cases where the model unexpectedly generated unrelated mathematical questions, programming tasks, or hidden reasoning traces from other contexts.



#### 2.4 Initial Observation and Discussion

Based on the first 30 test cases, the locally deployed DeepSeek-R1 32B model did not reproduce the abnormal behavior observed in the official DeepSeek web service.

Additional experiment rounds (another 30 tests) were also conducted afterward, and the same issue still could not be reproduced under the current experimental environment.





------

### 3. Guess and Discussion

Based on the experiment results and online discussions, the exact cause of the `<think>` token issue is still not 100% confirm. Although DeepSeek officially explained that the abnormal behavior was caused by hallucination triggered by a special token, the verification results from different users appear inconsistent.

Some people mentioned that they were able to reproduce similar abnormal outputs even in locally deployed environments, while other tests — including the experiment described in this article — failed to reproduce the issue under standalone GPU execution. This suggests that the problem may not be caused by a single factor alone.

One important discussion point is the nature of the hallucinated content itself. If the generated “random” answers contain information, events, or references that are newer than the model’s original training cutoff or release timeline ( as we already ), then the issue becomes more complicated. In that scenario, it raises questions about whether the responses are purely hallucinations generated by the model, or whether some form of unintended information exposure or context leakage may exist within the inference infrastructure.

At the current stage, there is still no public evidence proving actual cross-user private data leakage. However, this case highlights several important security concerns related to modern LLM systems:

- Hidden or reserved special tokens may unintentionally expose internal reasoning mechanisms.
- Improper prompt parsing may allow users to trigger unstable model states.
- Shared inference infrastructure may increase the risk of context contamination between requests.
- Reasoning-mode models may expose hidden chain-of-thought processing behavior when special tokens are injected.
- Frontend prompt formatting and backend inference pipelines may behave differently from standalone local deployments.

From an LLM security perspective, this case can also be viewed as a form of **special token attack** or **prompt-state manipulation attack**, where carefully crafted tokens attempt to interfere with the model’s internal reasoning or control flow. Even if no real data leakage exists, unstable hidden-state behavior itself can still become a security risk because it may expose internal prompts, hidden reasoning structures, or unintended model behaviors.



------

> last edit by LiuYuancheng (liu_yuan_cheng@hotmail.com) by 20/05/2026 if you have any question , please send me a message. 
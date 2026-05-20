# **The Special Token** `<think>` Problem/Bug of Latest DeepSeek LLM 

**Project Design Purpose** : This article will introduce a recent problem/bug people found when using the latest version Deepseek if you send the word ` <think>` or  `<think` there will be very high chance the model will generate very bad AI Hallucination and also show some experiment I tried to verify the problem and some guess about this bug from security view. This article will includes 3 part of section: 

- Introduce and Replicate the `<think>` tag bug/problem. 
- Introduce the design setup and result of verification experiment I did. 
- Some guess based on the experiment and discussion. 

```python
# Author:      Yuancheng Liu
# Created:     2026/05/19
# Version:     v_0.0.2
# Copyright:   Copyright (c) 2026 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### 1. Bug Introduction and Replication

#### 1.1 Bug Introduction 

Three days ago in 16/06/2026, some people found when they are using the new Deepseek LLM model (V3), if you send the word `<think>` or `<think`, there will be high possibility the model will random give you some information and the user's request information which you never asked before. As the questions a reasonable, some people think it may caused by the GPU load balancer's cache is not clear so you can see other people's question and consider as private data leakage,  some people think it is just a simple bug in the API's tokenizer. 

#### 1.2 Bug Replication

The bug is very easy to replicate, for the setting we use the official deepseek web with the setting: 

- Model type: V4-instant 
- Online search function: disabled
- Deep think function: enabled 

Now we send the word `<think>` and check the answer and we test several around (seven individual chat without any context)

**Test 01** :  As shown below, the model detected the question correct and give the correct answer

![](img/s_02.png)



**Test 02** :  As shown below, when we send the question again, we can see the model is answering some thing un-related and if we turn on the thinking progress we can see it is trying to answer the question "How to draw a cube?"  which I never asked it before

![](img/s_03.png)



Test 03 :  As shown below, when we send the question again,  we can see this around the model detect the  word `<think>` as one system prompt which is correct. 

![](img/s_04.png)



**Test 04** : In this round , we can see the model is trying to answer a question "Is it true that all n-dimensional vector spaces over a field F are isomorphic to the space of n-tuples F^n?" as shown below:

![](img/s_05.png)

Test 05: In this round, the module is trying to answer a question  "There is an additional constraint: the a_j are distinct positive integers."(as shown below) it seems it is part of the additional question of a request. 

![](img/s_07.png)

Test 06 : In this round the answer is also correct and reasonable, the model shows it need to activate thing as ready for answer user's question. 

![](img/s_06.png)

Test 07: In this round, the module try to answer a question ""We have a dataset of numbers representing the number of messages sent per day by a user. Define a function calculate_limits(mean, std_dev) that returns the lower and upper bounds of the acceptable range based on the 68-95-99.7 rule." as create a python program as shown below:

![](img/s_08.png)

Based on the seven test there will be high possibility (4/7) that the model will answer some un-related questions.









https://www.bilibili.com/video/BV1tZLE6gEK2/?spm_id_from=333.1007.tianma.1-2-2.click&vd_source=5ff50dfdd1613df97004d3548592e433
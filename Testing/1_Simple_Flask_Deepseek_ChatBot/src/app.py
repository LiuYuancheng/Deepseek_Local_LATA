#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        app.py [python3]
#
# Purpose:     This module is a simple flask AI chat bot program to connect to 
#              an Ollama server which is running on a remote machine with DeepSeek 
#              model deployed.
#  
# Author:      Yuancheng Liu
#
# Created:     2025/02/23
# version:     v_0.0.1
# Copyright:   Copyright (c) 2025 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
import json
import requests
from collections import OrderedDict
from flask import Flask, render_template, request, jsonify, Response

# Config flask parameters here
gFlaskHost = '0.0.0.0'
gFlaskPort = 5000
gFlaskDebug = False
gFlaskMultiTH = False 

# Config Ollama server parameters here
OllamaHosts = OrderedDict()
# Add your new host ip and model here
OllamaHosts['localhost-DS1.5b'] = {'ip': 'localhost', 'model': 'deepseek-r1:1.5b'}
OllamaHosts['RTX3060-DS7b'] = {'ip': '172.26.190.53', 'model': 'deepseek-r1:7b'}

selectModel = "localhost-DS1.5b"

app = Flask(__name__)

#-----------------------------------------------------------------------------
@app.route('/')
def index():
    posts = {
        'models': OllamaHosts.keys(),
        'name': str(selectModel),
        'host': OllamaHosts[selectModel]['ip'],
        'model': OllamaHosts[selectModel]['model'],
    }
    return render_template('index.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/<string:modelname>')
def select(modelname):
    global selectModel
    if modelname in OllamaHosts.keys(): selectModel = str(modelname) 
    posts = {
        'models': OllamaHosts.keys(),
        'name': str(selectModel),
        'host': OllamaHosts[selectModel]['ip'],
        'model': OllamaHosts[selectModel]['model'],
    }
    return render_template('index.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    #ollama_url = 'http://localhost:11434/api/generate'
    ollama_url = 'http://%s:11434/api/generate' % OllamaHosts[selectModel]['ip']
    print(ollama_url)
    data = {
        'model': OllamaHosts[selectModel]['model'],
        'prompt': user_message,
        'stream': True
    }
    
    try:
        response = requests.post(ollama_url, json=data, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print('Error:%s' %str(e))
        return Response(f"Error connecting to Ollama: {str(e)}", status=500)

    def generate():
        for line in response.iter_lines():
            if line:
                try:
                    json_chunk = json.loads(line.decode('utf-8'))
                    yield json_chunk.get('response', '')
                except json.JSONDecodeError:
                    continue

    return Response(generate(), mimetype='text/plain')



#-----------------------------------------------------------------------------
@app.route('/getResp', methods=['GET', ])
def getLastRst():
    """ Api to get the question answer
        requests.get(http://%s:%s/getLastRst, json={'model':<modelname>, 'message':<user_message>})
    """
    content = request.json
    response = None 
    if content:
        content = dict(content)
        model = str(content['model'])
        message = str(content['message'])
        if model in OllamaHosts.keys():
            ollama_url = 'http://%s:11434/api/generate' % OllamaHosts[model]['ip']

            data = {
                'model': OllamaHosts[model]['model'],
                'prompt': message,
                'stream': False
            }
        
        try:
            response = requests.post(ollama_url, json=data, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print('Error:%s' %str(e))
            return Response(f"Error connecting to Ollama: {str(e)}", status=500)

    return jsonify({"respose": str(response.content)})

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host=gFlaskHost, port=gFlaskPort, debug=gFlaskDebug, threaded=gFlaskMultiTH)

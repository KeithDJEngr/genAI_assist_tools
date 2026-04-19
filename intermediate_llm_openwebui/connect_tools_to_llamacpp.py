# Setup
## once:
#uv venv --python 3.12 --seed
#source .venv/bin/activate
#uv pip install fastapi uvicorn pydantic
#uv pip install openai
#uv pip install asyncio playwright markdownify beautifulsoup4 httpx && playwright install chromium
#uv pip install docker
## every time
#source .venv/bin/activate
#uvicorn connect_to_open_webui:app --reload --host XXX.XXX.XXX.XXX --port 8001

#TODO:
# add serach tool
# 


import os


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time



import requests

import json, random
from typing import Any


import docker, subprocess


import asyncio
import httpx
from playwright.async_api import async_playwright
from markdownify import markdownify as md
from bs4 import BeautifulSoup

async def fetch_live_page(url: str, use_js: bool = True) -> str:
    if use_js:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            html = await page.content()
            await browser.close()
        soup = BeautifulSoup(html, "html.parser")
        text = md(str(soup), heading_style="ATX", strip=["script", "style", "img"])
    else:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            text = md(resp.text, heading_style="ATX", strip=["script", "style", "img"])
    return text.strip()

def get_json(src_path: str) -> str:
    try:
        with open (src_path,'r') as f:
            contents=f.read()
            data = json.loads(contents)
            #data = json.load(f) # fails for some reason
    except FileNotFoundError:
        print(f"File not found: {src_path}")
        return f"File not found: {src_path}"
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return f"Invalid JSON: {e}"
    except Exception as e:
        print(f"Unrecognized error: {e}")
        return f"Unrecognized error: {e}"
    return str(data)

def write_json(json_content: str,target_path: str) -> str:
    # Slight problem now. Need to resolve.
    try:
        print(f"opening {target_path}")
        with open (target_path,'w') as f:
            print(f"f: {f}")
            a=json.loads(json_content)
            print(f"json loaded")
            f.write(json_content)
            return "True"
    except FileNotFoundError:
        print("A")
        print(f"File not found: {target_path}")
        return f"File not found: {target_path}"
    except json.JSONDecodeError as e:
        print("B")
        print(f"Invalid JSON: {e}")
        return f"Invalid JSON: {e}"
    except Exception as e:
        print("C")
        print(f"Unrecognized error: {e}")
        return f"Unrecognized error: {e}"
    return "False"



BASE_URL = "http://192.168.0.118"
PORT_LLM = "8000"
PORT_SEARXNG = "8080"
PORT_OPENWEBUI = "3000"



async def write_a_story() -> str:
    return random.choice([
        "A long time ago in a galaxy far far away...",
        "There were 2 friends who loved sloths and code...",
        "The world was ending because every sloth evolved to have superhuman intelligence...",
        "Unbeknownst to one friend, the other accidentally coded a program to evolve sloths...",
    ])
async def get_user_info() -> str:
    src_path="./data/user.json"
    return get_json(src_path)
async def get_system_info() -> str:
    src_path="./data/system.json"
    return get_json(src_path)
async def write_user_info(json_content: str) -> str:
    print("setting user info")
    write_json(json_content,"./data/user.json")
    #print(f"json_content: {json_content}")
    #try:
    #   with open ("./data/user.json",'rw') as f:
    #       print(f"f: {f}")
    #       data = json.load(f)
    #       print(f"updating original user file: \n{data}\n to: {json_content}")
    #       f.write(json_content)
    #except FileNotFoundError:
    #    return f"File not found: {f}"
    #except json.JSONDecodeError as e:
    #    return f"Invalid JSON: {e}"
    return str(data)
async def write_system_info(json_content: str) -> str:
    print("setting system info")
    write_json(json_content,"./data/system.json")
    try:
        with open ("./data/system.json",'rw') as f:
            print(f"f: {f}")
            data = json.load(f)
            print(f"updating original system file: \n{data}\n to: {json_content}")
            f.write(json_content)
    except FileNotFoundError:
        return f"File not found: {f}"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"
    return True
async def validate_json(json_content: str) -> str:
    def is_valid_json(json_content):
        try:
            json.loads(json_content)
            return "True"
        except:
            return "False"


async def terminal(command: str) -> str:
    try:
        client = docker.from_env()
        result=client.containers.run(image="ubuntu",command=["bash", "-c", code]).decode('utf-8')
        #exec(code, data)
    except Exception as E:
        return f"ERROR running code: {E}"
    return str(result)
    #if "rm" in command or "sudo" in command or "dd" in command or "chmod" in command:
    #    msg = "Cannot execute 'rm, sudo, dd, chmod' commands since they are dangerous"
    #    print(msg); return msg
    #print(f"Executing terminal command `{command}`")
    #try:
    #    return str(subprocess.run(command, capture_output = True, text = True, shell = True, check = True).stdout)
    #except subprocess.CalledProcessError as e:
    #    return f"Command failed: {e.stderr}"


async def websearch(search: str) -> str:
    print(f"REQUESTED WEBSEARCH: l{search}")
    response = requests.get(
            f"{BASE_URL}:{PORT_SEARXNG}/search",
        params={"q": f"{search}", "format": "json"}
    )
    response.raise_for_status()
    data = response.json()
    
    output=""
    for result in data.get("results", []):
        out+=f"{result.get('title') + " @ " + result.get('url')}"
    return output
async def webpage_request(url: str) -> str:
    print(f"\n\nREQUESTED WEBPAGE: {url}")
    raw_text = await fetch_live_page(url)
    #while type(raw_text != type('str')):
    #           print("Waiting for webpage to be pulled up")
    #           time.sleep(0.1)
    return raw_text

async def run_python(code: str) -> str:
    try:
        client = docker.from_env()
        result=client.containers.run(image="python:3.9",command=["python", "-c", code]).decode('utf-8')
        #exec(code, data)
    except Exception as E:
        return f"ERROR running code: {E}"
    return str(result)


MAP_FN = {
    "write_a_story": write_a_story,
    "get_user_info": get_user_info,
    "get_system_info": get_system_info,
    "write_user_info": write_user_info,
    "write_system_info": write_system_info,
    "validate_json": validate_json,
    "terminal": terminal,
    "run_python": run_python,
    "websearch":websearch,
    "webpage_request":webpage_request,
}



tools = [
    {
        "type": "function",
        "function": {
            "name": "write_a_story",
            "description": "Writes a random story.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "Get known info on user.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get known compute system info.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_user_info",
            "description": "Write json for user info. Ensure you are confident this is the current status of the user. Ask if unsure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "json_content": {
                        "type": "string",
                        "description": "The json of the user info. Read the user info first to be sure you don't lose info.",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_system_info",
            "description": "Write json for compute system info. Ensure you are confident this is the current status of the compute system. Ask if unsure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "json_content": {
                        "type": "string",
                        "description": "The json of the user info. Read the system info first to be sure you don't lose info.",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validate_json",
            "description": "Ensure string is valid json.",
            "parameters": {
                "type": "object",
                "properties": {
                    "json_content": {
                        "type": "string",
                        "description": "The json to validate.",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "Perform operations from the terminal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command you wish to launch, e.g `ls`, `rm`, ...",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Call a Python interpreter with some Python code that will be ran.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to run",
                    },
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "websearch",
            "description": "Perform a web search to get webpages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "The search to perform.",
                    },
                },
                "required": ["search"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "webpage_request",
            "description": "Get the content of a webpage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The webpage to access.",
                    },
                },
                "required": ["url"],
            },
        },
    },
]
# Other examples:


#def add_number(a: float | str, b: float | str) -> float:
#    return float(a) + float(b)
#def multiply_number(a: float | str, b: float | str) -> float:
#    return float(a) * float(b)
#def substract_number(a: float | str, b: float | str) -> float:
#    return float(a) - float(b)


#MAP_FN = {
#    "add_number": add_number,
#    "multiply_number":multiply_number,
#    "subtract_number":subtract_number,
#}


#    {
#        "type": "function",
#        "function": {
#            "name": "add_number",
#            "description": "Add two numbers.",
#            "parameters": {
#                "type": "object",
#                "properties": {
#                    "a": {
#                        "type": "string",
#                        "description": "The first number.",
#                    },
#                    "b": {
#                        "type": "string",
#                        "description": "The second number.",
#                    },
#                },
#                "required": ["a", "b"],
#            },
#        },
#    },
#    {
#        "type": "function",
#        "function": {
#            "name": "multiply_number",
#            "description": "Multiply two numbers.",
#            "parameters": {
#                "type": "object",
#                "properties": {
#                    "a": {
#                        "type": "string",
#                        "description": "The first number.",
#                    },
#                    "b": {
#                        "type": "string",
#                        "description": "The second number.",
#                    },
#                },
#                "required": ["a", "b"],
#            },
#        },
#    },
#    {
#        "type": "function",
#        "function": {
#            "name": "substract_number",
#            "description": "Substract two numbers.",
#            "parameters": {
#                "type": "object",
#                "properties": {
#                    "a": {
#                        "type": "string",
#                        "description": "The first number.",
#                    },
#                    "b": {
#                        "type": "string",
#                        "description": "The second number.",
#                    },
#                },
#                "required": ["a", "b"],
#            },
#        },
#    },



# --- Configuration ---
LLAMA_CPP_URL = f"{BASE_URL}:{PORT_LLM}/v1/chat/completions"
# Model: {BASE_URL}:{PORT_LLM}/?model=Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf
#MODEL_NAME = "Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-Q5_K_P.gguf"  # IMPORTANT: Change this to the name of the model loaded by llama.cpp
#TEMPERATURE = 0.7                   # Creativity level (0.0 = deterministic, 1.0 = highly creative)
#MAX_TOKENS = 512                    # Maximum length of the response
MODEL_NAME = "Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"  # IMPORTANT: Change this to the name of the model loaded by llama.cpp
TEMPERATURE = 0.7                   # Creativity level (0.0 = deterministic, 1.0 = highly creative)
MAX_TOKENS = 115000                    # Maximum length of the response


#def get_llm_response(user_prompt: str, system_instruction: str = "You are a helpful, concise robotics assistant. Respond in YAML format when possible.") -> str:
#        "messages": [
#            # System message sets the stage (crucial for robotics!)
#            {"role": "system", "content": system_instruction},
#            # User message is the actual query
#            {"role": "user", "content": user_prompt}
#        ],
#def get_llm_response(messages) -> str:
#    """
#    Sends a prompt to the Llama.cpp server and returns the generated text content.
#
#    Args:
#        user_prompt: The specific question or command from the robot.
#        system_instruction: The context or persona for the LLM.
#
#    Returns:
#        The text response from the LLM, or an error message string.
#    """
#    
#    # 1. Construct the Request Payload (JSON Body)




async def get_llm_response(messages) -> str:
    """
    Sends a prompt to the Llama.cpp server and returns the generated text content.

    Args:
        user_prompt: The specific question or command from the robot.
        system_instruction: The context or persona for the LLM.

    Returns:
        The text response from the LLM, or an error message string.
    """

    # 1. Construct the Request Payload (JSON Body)
    #payload = {
    #    "model": MODEL_NAME,
    #    "messages": messages,
    #    "max_tokens": MAX_TOKENS,
    #    "temperature": 1,
    #    "top_p": 0.95,
    #    "top_k": 20,
    #    "min_p": 0.0,
    #    "presence_penalty": 1.5,
    #    "repeat_penalty": 1.0,
    #    "max_tokens": 115200,
    #    # Optional: If you need to enforce JSON output strictly
    #    "response_format": {"type": "json_object"},
    #    "tools": tools,
    #    "tool_choice": "auto"
    #}
    for msg_num in range(0,len(messages)):
        if messages[msg_num]['role'] == "system":
            if messages[msg_num]['content'][-1]!='.':
                messages[msg_num]['content']+='.'
            messages[msg_num]['content']+=" Validate results with tools if possible. If tools don't give enough info, request from user in chat."
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": 1,
        "top_p": 0.95,
        "presence_penalty": 1.5,
        "repeat_penalty": 1.0,
        "extra_body": {"top_k": 20, "min_p": 0.0,},
        # Optional: If you need to enforce JSON output strictly
        "response_format": {"type": "json_object"},
        "tools": tools,
        "tool_choice": "auto"
        }

    # 2. Make the HTTP POST Request
    print(f"🤖 Sending request to {LLAMA_CPP_URL}...\n")
    print(f"{payload}")
    try:
        response = requests.post(LLAMA_CPP_URL, json=payload)

        # 3. Check for HTTP Errors
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        # 4. Parse the JSON Response
        print("    Waiting for response")
        data = response.json()

        # 5. Extract the Content
        # The structure is typically: response -> choices (list) -> [0] (first choice) -> message -> content
        print("    Received response")
        print(f"    data: \n{data}")

        if data.get("choices") and len(data["choices"]) > 0:
            llm_tool_call = data["choices"][0].get("message", {}).get("tool_calls")
            #print(f"Interjection! Need to handle tool call: {llm_tool_call}")
            if llm_tool_call:
                for tool_call in llm_tool_call:
                    print(f"\n    Tool call: {tool_call}")
                    fx, args, _id = tool_call['function']['name'], tool_call['function']['arguments'], tool_call['id']
                    print(f"fx, args, _id: {fx}, {args}, {_id}")
                    out = await MAP_FN[fx](**json.loads(args))
                    print(f"out: {out}")
                    messages.append({"role": "tool", "tool_call_id": _id, "name": fx, "content": str(out),})
        if llm_tool_call is not None:
            print(f"\n\nFollowing up with request: {messages}")
            return await get_llm_response(messages)
        print("No tool call needed, continuing ...")

        if data.get("choices") and len(data["choices"]) > 0:
            llm_content = data["choices"][0].get("message", {}).get("content")
            return llm_content
        else:
            return "Error: Response received but no content found in the 'choices' array."

    except requests.exceptions.HTTPError as e:
        print(f"\n--- HTTP Error Occurred ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        return f"HTTP Error: Could not reach server or request failed. ({e})"
    except requests.exceptions.ConnectionError:
        print(f"\n--- Connection Error Occurred ---")
        return "Connection Error: Is Llama.cpp server running on {BASE_URL}:{PORT_LLM}?"
    except requests.exceptions.RequestException as e:
        print(f"\n--- An Unexpected Error Occurred ---")
        os._exit(os.EX_OK)
        return f"General Request Error: {e}"
    except:
        print(f"\n--- An Unexpected Error Occurred ---")
        os._exit(os.EX_OK)


# ====================================================
# --- TEST SCENARIOS ---
# ====================================================

# Test 3: Tool call (testing new features)
#user_prompt = "What is 1+2?"
#system_instruction = "You are a helpful, concise robotics assistant. Respond in YAML format when possible."
#
#messages= [
#    # System message sets the stage (crucial for robotics!)
#    {"role": "system", "content": system_instruction},
#    # User message is the actual query
#    {"role": "user", "content": user_prompt}
#]
#llm_final_response = await get_llm_response(messages)
#print(f"\n>>> PROMPT: {user_prompt}")
#print(f"\n🤖 RESPONSE:\n{llm_final_response}")
#print("="*50)



























# --- 1. Define the Request Body Schema (Mimicking OpenAI Chat Request) ---
class ChatCompletionRequest(BaseModel):
    model: str = "dummy-llm-model"
    messages: List[dict]
    temperature: float = 0.0
    max_tokens: int = 150

# --- 2. Define the Response Body Schema (Mimicking OpenAI Response) ---
class Choice(BaseModel):
    index: int
    message: dict
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]

# --- 3. Initialize FastAPI App ---
app = FastAPI(
    title="Dummy LLM Mock Server",
    description="A simple FastAPI mock server responding with 'testing' to any request."
)

# (Assuming you have already defined FastAPI app, BaseModel, etc.)

@app.get("/models")
async def get_models():
    """
    Returns a dummy list of available models, which Open WebUI calls upon startup
    to populate its dropdown list.
    """
    # This list mimics what a real LLM backend would return
    return [
        {
            "id": "dummy-llm-model",
            "object": "model",
            "description": "A simple, fixed-response dummy model for testing purposes.",
            "created": int(time.time()),
            "parameters": {
                "type": "object",
                "properties": {
                    "max_tokens": {"type": "integer", "description": "Maximum tokens to generate."},
                    "temperature": {"type": "number", "description": "Sampling temperature."}
                }
            }
        }
    ]

@app.post("/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """
    Handles the primary LLM chat completion request. 
    It ignores the input and always returns the fixed response: "testing".
    """
    print(f"Received request to /v1/chat/completions. Prompting model: {request.model}")
    print(f"Received request: {request}")
    
    # --- Core Logic: Force the response to be "testing" ---
    # Construct the message object containing the fixed response
    mock_message_content = "testing"
    # Create the Choice object
    mock_choice = Choice(
        index=0,
        message=dict(content=mock_message_content),
        finish_reason="stop"
    )


    # Pseudo test prompt remplacement
    #user_prompt = "what is 1+3?"
    #system_instruction = "You are a helpful, concise robotics assistant. Respond in YAML format when possible."
    #actual_message= [
    #    # System message sets the stage (crucial for robotics!)
    #    {"role": "system", "content": system_instruction},
    #    # User message is the actual query
    #    {"role": "user", "content": user_prompt}
    #]
    actual_message = request.messages
    llm_final_response = await get_llm_response(actual_message)
    #print(f"\n>>> PROMPT: {user_prompt}")
    #print(f"\n🤖 RESPONSE:\n{llm_final_response}")
    #print("="*50)

    actual_choice = Choice(
        index=0,
        message=dict(content=llm_final_response),
        finish_reason="stop"
    )

    
    
    
    # Construct the final response object
    response = ChatCompletionResponse(
        id="chatcmpl-dummy-12345",
        created=int(time.time()), # Using current timestamp
        model=request.model,
        choices=[actual_choice] # choices=[mock_choice]
    )
    
    return response

#@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
#async def chat_completion_endpoint(request: ChatCompletionRequest):
#    """
#    Handles the primary LLM chat completion request. 
#    It ignores the input and always returns the fixed response: "testing".
#    """
#    print(f"Received request to /v1/chat/completions. Prompting model: {request.model}")
#    
#    # --- Core Logic: Force the response to be "testing" ---
#    
#    # Construct the message object containing the fixed response
#    mock_message_content = "testing"
#    
#    # Create the Choice object
#    mock_choice = Choice(
#        index=0,
#        message=dict(content=mock_message_content),
#        finish_reason="stop"
#    )
#    
#    # Construct the final response object
#    response = ChatCompletionResponse(
#        id="chatcmpl-dummy-12345",
#        created=int(time.time()), # Using current timestamp
#        model=request.model,
#        choices=[mock_choice]
#    )
#    
#    return response

# --- How to Run This Code ---
# 1. Install dependencies: pip install fastapi uvicorn pydantic
# 2. Save the code above as main.py
# 3. Run from your terminal: uvicorn main:app --reload
# -----------------------------------

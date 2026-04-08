# Setup
## once:
#uv venv --python 3.12 --seed
#source .venv/bin/activate
#uv pip install fastapi uvicorn pydantic
#uv pip install openai
## every time
#source .venv/bin/activate
#uvicorn connect_to_open_webui:app --reload --host XXX.XXX.XXX.XXX --port 8001


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time










import requests

import json, subprocess, random
from typing import Any



















def add_number(a: float | str, b: float | str) -> float:
    return float(a) + float(b)
def multiply_number(a: float | str, b: float | str) -> float:
    return float(a) * float(b)
def substract_number(a: float | str, b: float | str) -> float:
    return float(a) - float(b)
def write_a_story() -> str:
    return random.choice([
        "A long time ago in a galaxy far far away...",
        "There were 2 friends who loved sloths and code...",
        "The world was ending because every sloth evolved to have superhuman intelligence...",
        "Unbeknownst to one friend, the other accidentally coded a program to evolve sloths...",
    ])
def terminal(command: str) -> str:
    if "rm" in command or "sudo" in command or "dd" in command or "chmod" in command:
        msg = "Cannot execute 'rm, sudo, dd, chmod' commands since they are dangerous"
        print(msg); return msg
    print(f"Executing terminal command `{command}`")
    try:
        return str(subprocess.run(command, capture_output = True, text = True, shell = True, check = True).stdout)
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.stderr}"
def python(code: str) -> str:
    data = {}
    exec(code, data)
    del data["__builtins__"]
    return str(data)
MAP_FN = {
    "add_number": add_number,
    "multiply_number": multiply_number,
    "substract_number": substract_number,
    "write_a_story": write_a_story,
    "terminal": terminal,
    "python": python,
}
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_number",
            "description": "Add two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string",
                        "description": "The first number.",
                    },
                    "b": {
                        "type": "string",
                        "description": "The second number.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_number",
            "description": "Multiply two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string",
                        "description": "The first number.",
                    },
                    "b": {
                        "type": "string",
                        "description": "The second number.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "substract_number",
            "description": "Substract two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string",
                        "description": "The first number.",
                    },
                    "b": {
                        "type": "string",
                        "description": "The second number.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
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
            "name": "python",
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
]



# --- Configuration ---
LLAMA_CPP_URL = "http://192.168.0.118:8000/v1/chat/completions"
MODEL_NAME = "Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-Q5_K_P.gguf"  # IMPORTANT: Change this to the name of the model loaded by llama.cpp
TEMPERATURE = 0.7                   # Creativity level (0.0 = deterministic, 1.0 = highly creative)
MAX_TOKENS = 512                    # Maximum length of the response

def get_llm_response(messages) -> str:
    """
    Sends a prompt to the Llama.cpp server and returns the generated text content.

    Args:
        user_prompt: The specific question or command from the robot.
        system_instruction: The context or persona for the LLM.

    Returns:
        The text response from the LLM, or an error message string.
    """

    # 1. Construct the Request Payload (JSON Body)
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        # Optional: If you need to enforce JSON output strictly
        "response_format": {"type": "json_object"},
        "tools": tools,
        "tool_choice": "auto"
    }

    # 2. Make the HTTP POST Request
    print(f"🤖 Sending request to {LLAMA_CPP_URL}...")
    try:
        response = requests.post(LLAMA_CPP_URL, json=payload)

        # 3. Check for HTTP Errors
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        # 4. Parse the JSON Response
        data = response.json()

        # 5. Extract the Content
        # The structure is typically: response -> choices (list) -> [0] (first choice) -> message -> content
        #print(f"    data: \n{data}")

        if data.get("choices") and len(data["choices"]) > 0:
            llm_tool_call = data["choices"][0].get("message", {}).get("tool_calls")
            #print(f"Interjection! Need to handle tool call: {llm_tool_call}")
            if llm_tool_call:
                for tool_call in llm_tool_call:
                    print(f"\n    Tool call: {tool_call}")
                    fx, args, _id = tool_call['function']['name'], tool_call['function']['arguments'], tool_call['id']
                    out = MAP_FN[fx](**json.loads(args))
                    messages.append({"role": "tool", "tool_call_id": _id, "name": fx, "content": str(out),})
        if llm_tool_call is not None:
            return get_llm_response(messages)
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
        return "Connection Error: Is Llama.cpp server running on http://localhost:8000?"
    except requests.exceptions.RequestException as e:
        print(f"\n--- An Unexpected Error Occurred ---")
        return f"General Request Error: {e}"

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
#llm_final_response = get_llm_response(messages)
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
    llm_final_response = get_llm_response(actual_message)
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

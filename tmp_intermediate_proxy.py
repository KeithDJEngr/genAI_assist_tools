
## once:
#uv venv --python 3.12 --seed
#source .venv/bin/activate
#pip install openai
## every time
#source .venv/bin/activate


#from fastapi import FastAPI
#
## Idea - I work as a go-between from open webui to llama.cpp
#
## Note: I need to make a dummy server that listens like llama.cpp was
#
## Then I put that in a messages thing in here:
#"""
#curl http://localhost:8080/v1/chat/completions -d '{
#  "model": "gpt-3.5-turbo",
#  "tools": [
#    {
#      "type": "function",
#      "function": {
#        "name": "python",
#        "description": "Runs code in an ipython interpreter and returns the result of the execution after 60 seconds.",
#        "parameters": {
#          "type": "object",
#          "properties": {
#            "code": {
#              "type": "string",
#              "description": "The code to run in the ipython interpreter."
#            }
#          },
#          "required": ["code"]
#        }
#      }
#    }
#  ],
#  "messages": [
#    {
#      "role": "user",
#      "content": "Print a hello world message with python."
#    }
#  ]
#}'
#"""
##I then see if the request returned has a message content or it requests tool call(s)
#
#
#app = FastAPI(titel="Llamacpp Proxy")


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





#from openai import OpenAI
#def unsloth_inference(
#    messages,
#    temperature = 1.0,
#    top_p = 0.95,
#    top_k = 40,
#    min_p = 0.01,
#    repetition_penalty = 1.0,
#):
#    messages = messages.copy()
#    openai_client = OpenAI(
#        base_url = "http://127.0.0.1:8000/v1",
#        api_key = "sk-no-key-required",
#    )
#    model_name = next(iter(openai_client.models.list())).id
#    print(f"Using model = {model_name}")
#    has_tool_calls = True
#    original_messages_len = len(messages)
#    while has_tool_calls:
#        print(f"Current messages = {messages}")
#        response = openai_client.chat.completions.create(
#            model = model_name,
#            messages = messages,
#            temperature = temperature,
#            top_p = top_p,
#            tools = tools if tools else None,
#            tool_choice = "auto" if tools else None,
#            extra_body = {"top_k": top_k, "min_p": min_p, "repetition_penalty" :repetition_penalty,}
#        )
#        tool_calls = response.choices[0].message.tool_calls or []
#        content = response.choices[0].message.content or ""
#        tool_calls_dict = [tc.to_dict() for tc in tool_calls] if tool_calls else tool_calls
#        messages.append({"role": "assistant", "tool_calls": tool_calls_dict, "content": content,})
#        for tool_call in tool_calls:
#            fx, args, _id = tool_call.function.name, tool_call.function.arguments, tool_call.id
#            out = MAP_FN[fx](**json.loads(args))
#            messages.append({"role": "tool", "tool_call_id": _id, "name": fx, "content": str(out),})
#        else:
#            has_tool_calls = False
#    return messages
#
#messages = [{
#    "role": "user",
#    "content": [{"type": "text", "text": "Create a Fibonacci function in Python and find fib(20)."}],
#}]
#unsloth_inference(messages, temperature = 1.0, top_p = 0.95, top_k = 40, min_p = 0.00)





import requests
import json

# --- Configuration ---
LLAMA_CPP_URL = "http://192.168.0.118:8000/v1/chat/completions"

# Model: http://192.168.0.118:3000/?model=Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf
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
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 20,
        "min_p": 0.0,
        "presence_penalty": 1.0,
        "repeat_penalty": 1.0,
        "max_tokens": 256,
        # Optional: If you need to enforce JSON output strictly
        "response_format": {"type": "json_object"},
        "tools": tools,
        "tool_choice": "auto"
    }
#        "extra_body": {"top_k": top_k, "min_p": min_p, "repetition_penalty" :repetition_penalty}

#        response = openai_client.chat.completions.create(
#            model = model_name,
#            messages = messages,
#            temperature = temperature,
#            top_p = top_p,
#            tools = tools if tools else None,
#            tool_choice = "auto" if tools else None,
#            extra_body = {"top_k": top_k, "min_p": min_p, "repetition_penalty" :repetition_penalty,}
#        )

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
        print(f"    data: \n{data}")

        if data.get("choices") and len(data["choices"]) > 0:
            llm_tool_call = data["choices"][0].get("message", {}).get("tool_calls")
            print(f"Interjection! Need to handle tool call: {llm_tool_call}")
            if llm_tool_call:
                for tool_call in llm_tool_call:
                    print(f"\n    Tool call: {tool_call}")
                    fx, args, _id = tool_call['function']['name'], tool_call['function']['arguments'], tool_call['id']
                    #fx, args, _id = tool_call[function][name], tool_call[function][arguments], tool_call.id
                    out = MAP_FN[fx](**json.loads(args))
                    messages.append({"role": "tool", "tool_call_id": _id, "name": fx, "content": str(out),})
#        for tool_call in tool_calls:
#            fx, args, _id = tool_call.function.name, tool_call.function.arguments, tool_call.id
#            out = MAP_FN[fx](**json.loads(args))
#            messages.append({"role": "tool", "tool_call_id": _id, "name": fx, "content": str(out),})
        if llm_tool_call is not None:
            return get_llm_response(messages)
        print("No tool call needed, continuing ...")


        print("Getting message content")
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

## Test 1: Basic Navigation Query
#prompt_1 = "The robot is in a kitchen. It needs to go from the charging dock to the refrigerator. What is the shortest path description?"
#print("\n" + "="*50)
#response_1 = get_llm_response(prompt_1, system_instruction="You are a concise navigation planner. Respond ONLY with a YAML block detailing the path.")
#print(f"\n>>> PROMPT: {prompt_1}")
#print(f"\n🤖 RESPONSE:\n{response_1}")
#print("="*50)
#
#
## Test 2: Complex Tool/Action Request (Good for robotics)
#prompt_2 = "The object detected is a red, cylindrical cup placed on the table. Generate a JSON command to pick it up and move it to the designated 'StagingArea'."
#print("\n" + "="*50)
#response_2 = get_llm_response(prompt_2, system_instruction="You are an expert motion planning AI. Respond ONLY with a valid JSON object structured like: { 'action': 'pickup', 'target_object': '...', 'destination': '...' }")
#print(f"\n>>> PROMPT: {prompt_2}")
#print(f"\n🤖 RESPONSE:\n{response_2}")
#print("="*50)
#
#
## Test 3: Tool call (testing new features)
#prompt_2 = "What is 1+2?"
#print("\n" + "="*50)
#response_2 = get_llm_response(prompt_2, system_instruction="You are an advanced AI with access to tools. Call them if necessary.")
#print(f"\n>>> PROMPT: {prompt_2}")
#print(f"\n🤖 RESPONSE:\n{response_2}")
#print("="*50)







# Test 3: Tool call (testing new features)
user_prompt = "What is 1+2?"
system_instruction = "You are a helpful, concise robotics assistant. Respond in YAML format when possible."

messages= [
    # System message sets the stage (crucial for robotics!)
    {"role": "system", "content": system_instruction},
    # User message is the actual query
    {"role": "user", "content": user_prompt}
]
llm_final_response = get_llm_response(messages)
print(f"\n>>> PROMPT: {user_prompt}")
print(f"\n🤖 RESPONSE:\n{llm_final_response}")
print("="*50)

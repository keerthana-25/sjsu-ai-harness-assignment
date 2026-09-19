"""
Part A: Simple Coding Harness with OpenRouter API

Minimal implementation that:
- Connects to OpenRouter API (supports 100+ models)
- Implements basic tools (bash, read_file, write_file)
- Runs an agent loop with tool use
- Handles streaming and tool responses

Run:
  export OPENROUTER_API_KEY="your_key_here"
  python part_a_openrouter.py
"""

import os
import json
import subprocess
import sys
from openai import OpenAI

# ============ Configuration ============

BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-v4-flash"  # Can use gemini-pro, gpt-4-mini, etc.

if not API_KEY:
    print("Error: OPENROUTER_API_KEY not set")
    sys.exit(1)

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """
You are a coding agent. Your job is to solve problems using code.

Use the bash tool to run commands and explore the system.
Use read_file to read file contents.
Use write_file to create and edit files.

Think step by step. When you need to understand something, use the tools.
Always finish by summarizing what you did.
"""

# ============ Tool Definitions ============

def bash_tool(command: str) -> str:
    """Execute a bash command and return the output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        output = result.stdout + result.stderr
        return output[:2000] if len(output) > 2000 else output
    except Exception as e:
        return f"Error: {str(e)}"

def read_file(path: str) -> str:
    """Read contents of a file."""
    try:
        with open(path, 'r') as f:
            content = f.read()
        return content[:2000] if len(content) > 2000 else content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"File written to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

TOOLS = {
    "bash_tool": bash_tool,
    "read_file": read_file,
    "write_file": write_file,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "bash_tool",
            "description": "Execute a bash command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        }
    }
]

# ============ Agent Loop ============

def call_llm(messages: list) -> dict:
    """Call OpenRouter API with tool definitions."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMAS,
        temperature=0.7,
        max_tokens=1000,
    )
    
    message = response.choices[0].message
    return {
        "role": "assistant",
        "content": message.content,
        "tool_calls": message.tool_calls,
    }

def process_tool_calls(tool_calls):
    """Execute tool calls and return results."""
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_input = json.loads(tool_call.function.arguments)
        
        print(f"\n> Tool: {tool_name}")
        print(f"  Input: {tool_input}")
        
        if tool_name in TOOLS:
            result = TOOLS[tool_name](**tool_input)
            print(f"  Result: {result[:200]}...")
            
            results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
    
    return results

def agent_loop(user_input: str, max_turns: int = 10):
    """Run the agent loop."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]
    
    print(f"\n{'='*60}")
    print(f"User: {user_input}")
    print(f"{'='*60}\n")
    
    for turn in range(max_turns):
        response = call_llm(messages)
        
        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": response["content"],
            "tool_calls": response["tool_calls"],
        })
        
        # Print agent response
        if response["content"]:
            print(f"Agent: {response['content']}")
        
        # Check if we need to call tools
        if not response["tool_calls"]:
            print("\n" + "="*60)
            print("Agent finished (no more tool calls)")
            print("="*60)
            break
        
        # Process tool calls
        tool_results = process_tool_calls(response["tool_calls"])
        messages.extend(tool_results)
    
    print("\n" + "="*60)
    print("Agent loop complete")
    print("="*60)

# ============ Main ============

if __name__ == "__main__":
    # Example usage
    user_task = """
    Create a Python script that prints "Hello from Part A!" 
    and save it to hello.py. Then run it to show the output.
    """
    
    agent_loop(user_task)

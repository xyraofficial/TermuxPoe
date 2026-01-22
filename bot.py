import os
import sys
import time
import json
import requests
import threading
import itertools
import subprocess
import re
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt

# Initialize Rich Console
console = Console()

# Poe API Configuration
api_key = os.getenv("POE_API_KEY")

if not api_key:
    console.print("[bold red]Error: POE_API_KEY not found in environment variables.[/bold red]")
    console.print("Please set it using: export POE_API_KEY='your_api_key'")
    sys.exit(1)

# ANSI Color Codes
CYAN = "\033[96m"
WHITE = "\033[97m"
GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_banner():
    clear_screen()
    console.print(f"{DIM}# Environment: AI-TERMINAL-X1 (AGENT MODE)\n# Protocol: POE-v1-SECURE{RESET}")
    banner_content = Text.assemble(
        (f"~/firmware", "bold white"),
        (" > ", "cyan"),
        ("AI AUTONOMOUS AGENT", "bold green")
    )
    console.print(Panel(banner_content, border_style="cyan", expand=False))

class FirmwareAnimation:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None
        self.message = "Processing"

    def animate(self):
        chars = itertools.cycle(['○', '◔', '◑', '◕', '●'])
        while not self.stop_event.is_set():
            char = next(chars)
            sys.stdout.write(f"\r{DIM} {char} {self.message}...{RESET}")
            sys.stdout.flush()
            time.sleep(0.15)
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

    def start(self, message="Processing"):
        self.message = message
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()

def get_ai_response(messages, system_prompt=None):
    url = "https://api.poe.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "Termux AI Agent"
    }
    
    payload_messages = []
    if system_prompt:
        payload_messages.append({"role": "system", "content": system_prompt})
    payload_messages.extend(messages)

    payload = {
        "model": "Claude-3.5-Sonnet",
        "messages": payload_messages,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"ERROR: {str(e)}"

def execute_command(command):
    # Auto-prepend 'yes |' for installations to prevent hanging
    if any(pkg_cmd in command for pkg_cmd in ["apt install", "pkg install", "pip install", "npm install"]):
        if "yes |" not in command:
            command = f"yes | {command}"
            
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": 1}

def write_file(filename, content):
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"File '{filename}' written successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"

SYSTEM_PROMPT = """You are an autonomous AI Agent in Termux. You MUST respond in a specific structured format to perform tasks.

FORMAT RULES:
1. Always start with 'PLAN:' followed by your step-by-step plan.
2. Use 'CODE:' followed by the content of a file you want to write.
3. Use 'FILENAME:' followed by the name of the file for the code.
4. Use 'TEST:' followed by a SINGLE bash command to execute.

Example:
PLAN: I will create a script and run it.
FILENAME: test.py
CODE:
print("Hello")
TEST: python test.py

If you only need to run a command without writing code:
PLAN: I will check the system version.
TEST: uname -a
"""

def parse_agent_response(response):
    plan = re.search(r'PLAN:(.*?)(?:CODE:|TEST:|FILENAME:|$)', response, re.DOTALL | re.IGNORECASE)
    filename = re.search(r'FILENAME:(.*?)(?:CODE:|TEST:|PLAN:|$)', response, re.DOTALL | re.IGNORECASE)
    test = re.search(r'TEST:(.*?)(?:CODE:|PLAN:|FILENAME:|$)', response, re.DOTALL | re.IGNORECASE)
    
    # Code is usually more complex, look for CODE: block until next keyword or end
    code_match = re.search(r'CODE:(.*?)(?:TEST:|PLAN:|FILENAME:|$)', response, re.DOTALL | re.IGNORECASE)
    
    plan_text = plan.group(1).strip() if plan else "No plan provided."
    filename_text = filename.group(1).strip() if filename else "generated_script.py"
    test_text = test.group(1).strip() if test else None
    
    code_text = None
    if code_match:
        code_text = code_match.group(1).strip()
        # Clean up markdown code blocks if AI included them
        code_text = re.sub(r'^```\w*\n', '', code_text)
        code_text = re.sub(r'\n```$', '', code_text)

    return plan_text, code_text, filename_text, test_text

def main():
    draw_banner()
    messages = []
    anim = FirmwareAnimation()

    while True:
        try:
            user_input = Prompt.ask(f"\n[bold cyan]~/firmware[/bold cyan] [white]>[/white]")
            
            if user_input.lower() in ['exit', 'quit', ':q']:
                break

            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})
            
            # AGENT LOOP
            while True:
                anim.start("Agent Thinking")
                response = get_ai_response(messages, SYSTEM_PROMPT)
                anim.stop()
                
                plan, code, filename, test = parse_agent_response(response)
                
                # Show Plan
                console.print(Panel(Markdown(f"### Plan\n{plan}"), title="[bold yellow]PLAN[/bold yellow]", border_style="yellow"))
                
                # Ask to continue
                cont = Prompt.ask("Continue with this plan? [Y/n]", default="y")
                if cont.lower() != 'y': break
                
                # Handle CODE
                if code:
                    console.print(f"[bold blue]FILENAME:[/bold blue] {filename}")
                    anim.start(f"Writing {filename}")
                    result = write_file(filename, code)
                    anim.stop()
                    console.print(f"[green]✓[/green] {result}")
                
                # Handle TEST
                if test:
                    console.print(Panel(f"Command: [bold cyan]{test}[/bold cyan]", title="TEST", border_style="blue"))
                    cont_test = Prompt.ask("Execute command? [Y/n]", default="y")
                    if cont_test.lower() == 'y':
                        anim.start("Executing")
                        result = execute_command(test)
                        anim.stop()
                        
                        output = f"STDOUT:\n{result['stdout']}\nSTDERR:\n{result['stderr']}"
                        console.print(Panel(output, title=f"Exit Code: {result['exit_code']}", border_style="white"))
                        
                        if result['exit_code'] != 0:
                            console.print("[bold red]ERROR DETECTED! Starting Reflection Loop...[/bold red]")
                            messages.append({"role": "assistant", "content": response})
                            messages.append({"role": "user", "content": f"The command failed with exit code {result['exit_code']}.\nError log:\n{result['stderr']}\nPlease analyze and fix it."})
                            continue # Loop back to AI for reflection
                
                # Task Complete
                console.print("[bold green]✓ Task Complete.[/bold green]")
                messages.append({"role": "assistant", "content": response})
                break # Exit agent loop

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]FATAL: {e}[/bold red]")

if __name__ == "__main__":
    main()

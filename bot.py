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
from rich.text import Text

# Initialize Rich Console
console = Console()

# Poe API Configuration
api_key = os.getenv("POE_API_KEY")

if not api_key:
    console.print("[bold red]Error: POE_API_KEY not found in environment variables.[/bold red]")
    console.print("Please set it using: export POE_API_KEY='your_api_key'")
    sys.exit(1)

# System Prompt for the AI
SYSTEM_PROMPT = """You are an AI Terminal Assistant with Shell Execution capabilities.
Your workflow:
1. Plan: Explain what you will do.
2. Code: Provide the code or commands.
3. Test: Run the code/commands to verify.
4. Reflect: If error occurs, analyze logs and fix.

When you want to execute a command, wrap it in:
```bash
command_here
```
Important: Always use -y for installs (e.g., pkg install -y git).
"""

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
    console.print(f"{DIM}# Environment: AI-TERMINAL-X1\n# Protocol: POE-v1-REFLECT{RESET}")
    banner_content = Text.assemble(
        ("~/firmware", "bold white"),
        (" > ", "cyan"),
        ("AI AUTO-EXEC ENGINE", "bold green")
    )
    console.print(Panel(banner_content, border_style="cyan", expand=False))

class FirmwareAnimation:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def animate(self):
        stages = [
            "Initializing neural link",
            "Accessing memory blocks",
            "Decrypting response data",
            "Finalizing stream"
        ]
        chars = itertools.cycle(['○', '◔', '◑', '◕', '●'])
        
        start_time = time.time()
        idx = 0
        while not self.stop_event.is_set():
            char = next(chars)
            if time.time() - start_time > 1.2:
                idx = (idx + 1) % len(stages)
                start_time = time.time()
                
            sys.stdout.write(f"\r{DIM} {char} {stages[idx]}...{RESET}")
            sys.stdout.flush()
            time.sleep(0.15)
        
        sys.stdout.write("\r" + " " * 45 + "\r")
        sys.stdout.flush()

    def start(self):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()

def execute_shell(command):
    # Auto-add -y to common install commands if missing
    # Supports pkg install, apt install, npm install, pip install
    if re.search(r'\b(pkg|apt|npm|pip)\s+install\b', command) and '-y' not in command and '--yes' not in command:
        command = re.sub(r'\b(pkg|apt|npm|pip)\s+install\b', r'\1 install -y', command)
    
    try:
        console.print(f"[bold yellow]Executing:[/bold yellow] [white]{command}[/white]")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def get_ai_response(messages):
    url = "https://api.poe.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Ensure system prompt is present
    payload_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
    payload = {
        "model": "Claude-3.5-Sonnet",
        "messages": payload_messages,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"FIRMWARE_ERR: {str(e)}")

def main():
    draw_banner()
    messages = []
    anim = FirmwareAnimation()

    while True:
        try:
            user_input = console.input(f"[bold cyan]~/firmware[/bold cyan] [white]>[/white] ")
            
            if user_input.lower() in ['exit', 'quit', ':q']:
                console.print(f"\n[dim]Terminating session... Done.[/dim]")
                break
                
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            max_retries = 5
            for attempt in range(max_retries):
                anim.start()
                try:
                    ai_message = get_ai_response(messages)
                finally:
                    anim.stop()

                # Show AI Response
                console.print(Panel(Markdown(ai_message), title=f"[bold green]AI (Attempt {attempt+1})[/bold green]", border_style="green", expand=False))
                messages.append({"role": "assistant", "content": ai_message})

                # Check for bash blocks
                commands = re.findall(r'```bash\s*\n(.*?)\n```', ai_message, re.DOTALL)
                
                if not commands:
                    break # No commands to run, wait for next user input

                all_success = True
                for cmd in commands:
                    cmd = cmd.strip()
                    if not cmd: continue
                    
                    code, out, err = execute_shell(cmd)
                    
                    if out: console.print(Panel(Text(out.strip(), style="dim"), title="STDOUT", border_style="blue"))
                    if err: console.print(Panel(Text(err.strip(), style="bold red"), title="STDERR", border_style="red"))

                    if code != 0:
                        all_success = False
                        messages.append({"role": "user", "content": f"Command failed with exit code {code}.\nSTDOUT: {out}\nSTDERR: {err}\nPlease reflect and fix."})
                        console.print("[bold red]Reflection triggered... repairing code.[/bold red]")
                        break # Exit current command loop to let AI try again
                
                if all_success:
                    console.print("[bold green]All commands executed successfully.[/bold green]")
                    break
            else:
                console.print("[bold red]Reached maximum reflection attempts.[/bold red]")

        except KeyboardInterrupt:
            console.print(f"\n[bold yellow]SIGINT received. Exiting.[/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red][!] FATAL: {e}[/bold red]")

if __name__ == "__main__":
    main()

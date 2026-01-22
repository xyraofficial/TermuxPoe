import os
import sys
import time
import json
import threading
import itertools
import subprocess
import re
import requests
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.box import ROUNDED, DOUBLE_EDGE

# Initialize Rich Console
console = Console()

# Replit AI Integration Configuration
# Using raw requests to avoid dependency on 'openai' library in Termux

# System Prompt for the AI
SYSTEM_PROMPT = """You are an AI Terminal Assistant with Shell Execution capabilities in Termux.
Your workflow:
1. Plan: Explain what you will do.
2. Code: Provide the code or commands.
3. Test: Run the code/commands to verify.
4. Reflect: If error occurs, analyze logs and fix.

RULES:
- Keep responses simple and concise. Only provide necessary information.
- For simple questions, give simple answers. Don't over-explain.
- DO NOT use the `which` command (it might be missing). Use `command -v <app>` or `pkg list-installed` instead.
- When you want to execute a command, wrap it in:
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
    console.print(f"{DIM}# Environment: AI-TERMINAL-X2 | Protocol: REPLIT-v1-REFLECT{RESET}", justify="center")
    banner_text = Text.assemble(
        (" ~/firmware ", "bold white on blue"),
        (" > ", "bold cyan"),
        (" AI AUTO-EXEC ENGINE ", "bold black on green")
    )
    console.print(Panel(banner_text, box=DOUBLE_EDGE, border_style="bright_blue", expand=False, padding=(0, 2)), justify="center")
    console.print()

class FirmwareAnimation:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def animate(self):
        stages = ["Neural Link", "Memory Block", "Decrypting", "Finalizing", "Executing"]
        chars = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        
        start_time = time.time()
        idx = 0
        while not self.stop_event.is_set():
            char = next(chars)
            if time.time() - start_time > 1.0:
                idx = (idx + 1) % len(stages)
                start_time = time.time()
                
            sys.stdout.write(f"\r {CYAN}{char}{RESET} {DIM}{stages[idx]}...{RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
        
        sys.stdout.write("\r" + " " * 30 + "\r")
        sys.stdout.flush()

    def start(self):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.animate, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()

def execute_shell(command, anim):
    if re.search(r'\b(pkg|apt|npm|pip)\s+install\b', command) and '-y' not in command and '--yes' not in command:
        command = re.sub(r'\b(pkg|apt|npm|pip)\s+install\b', r'\1 install -y', command)
    
    console.print(f" [bold yellow]⚡[/bold yellow] [bold white]Running:[/bold white] [cyan]{command}[/cyan]")
    
    anim.start()
    process = None
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=300)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        if process:
            process.kill()
        return 1, "", "Execution Timeout (300s)"
    except Exception as e:
        return 1, "", str(e)
    finally:
        anim.stop()

def get_ai_response(messages):
    # Try multiple endpoints if one is unreachable
    endpoints = [
        "https://api.replit.com/ai/v1/chat/completions",
        "https://ai-proxy.replit.com/ai/v1/chat/completions"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer replit"
    }
    
    payload_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    payload = {
        "model": "gpt-4o-mini",
        "messages": payload_messages,
    }
    
    for url in endpoints:
        for api_attempt in range(2):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
            except requests.exceptions.RequestException:
                if api_attempt == 0:
                    time.sleep(1)
                    continue
                break # Try next endpoint
                
    raise Exception("Network Error: Could not reach AI service. Please check your Termux internet connection.")

def main():
    draw_banner()
    messages = []
    anim = FirmwareAnimation()

    while True:
        try:
            prompt = Text.assemble(
                (" ~/firmware ", "bold white on cyan"),
                (" ", "default"),
                ("❯ ", "bold green")
            )
            user_input = console.input(prompt)
            
            if user_input.lower() in ['exit', 'quit', ':q']:
                console.print(Panel("Session Terminated Safely", border_style="dim", box=ROUNDED))
                break
                
            if not user_input.strip(): continue

            messages.append({"role": "user", "content": user_input})

            max_retries = 5
            for attempt in range(max_retries):
                anim.start()
                try:
                    ai_message = get_ai_response(messages)
                except Exception as e:
                    anim.stop()
                    err_str = str(e)
                    console.print(Panel(err_str, title="[bold red]CRITICAL ERROR[/bold red]", border_style="bright_red", box=DOUBLE_EDGE))
                    return
                finally:
                    anim.stop()

                title = " AI CORE "
                console.print(Panel(Markdown(ai_message), title=title, border_style="bright_green", box=ROUNDED, padding=(1, 2)))
                messages.append({"role": "assistant", "content": ai_message})

                commands = re.findall(r'```bash\s*\n(.*?)\n```', ai_message, re.DOTALL)
                if not commands: break

                all_success = True
                for cmd in commands:
                    cmd = cmd.strip()
                    if not cmd: continue
                    
                    code, out, err = execute_shell(cmd, anim)
                    
                    if out.strip():
                        filtered_out = "\n".join([line for line in out.strip().split("\n") if not re.search(r"Reading database \.\.\. \d+%", line)])
                        if filtered_out.strip():
                            console.print(Panel(filtered_out.strip(), title="[bold blue]STDOUT[/bold blue]", border_style="blue", box=ROUNDED, subtitle=f"Code: {code}"))
                    
                    if code != 0:
                        all_success = False
                        error_msg = err.strip() or "Unknown Error"
                        console.print(Panel(error_msg, title="[bold red]STDERR / ERROR[/bold red]", border_style="red", box=DOUBLE_EDGE))
                        
                        messages.append({
                            "role": "user", 
                            "content": f"Command `{cmd}` failed.\nSTDOUT: {out}\nSTDERR: {err}\nPlease reflect and fix."
                        })
                        console.print(" [bold red]![/bold red] [italic red]Self-correction loop triggered...[/italic red]")
                        break 
                
                if all_success:
                    console.print(" [bold green]✔[/bold green] [bold white]All operations completed successfully.[/bold white]\n")
                    break
            else:
                console.print(" [bold red]✘[/bold red] [bold white]Reflection limit reached. Manual intervention required.[/bold white]\n")

        except KeyboardInterrupt:
            console.print(f"\n[bold yellow]SIGINT received. Shutting down.[/bold yellow]")
            break
        except Exception as e:
            console.print(Panel(str(e), title="[bold red]SYSTEM FATAL ERROR[/bold red]", border_style="bright_red", box=DOUBLE_EDGE))

if __name__ == "__main__":
    main()

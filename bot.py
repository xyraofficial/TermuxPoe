import os
import sys
import time
import json
import requests
import threading
import itertools
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.text import Text

# Initialize Rich Console
console = Console()

# Poe API Configuration
api_key = os.getenv("POE_API_KEY")

if not api_key:
    console.print("[bold red]Error: POE_API_KEY not found in environment variables.[/bold red]")
    console.print("Please set it using: export POE_API_KEY='your_api_key'")
    sys.exit(1)

# ANSI Color Codes for non-rich parts
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
    console.print(f"{DIM}# Environment: AI-TERMINAL-X1\n# Protocol: POE-v1-SECURE{RESET}")
    banner_content = Text.assemble(
        (f"~/firmware", "bold white"),
        (" > ", "cyan"),
        ("AI CHATBOT ENGINE", "bold green")
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

def get_ai_response(messages):
    url = "https://api.poe.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "Termux AI Bot"
    }
    
    payload = {
        "model": "Claude-3.5-Sonnet",
        "messages": messages,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
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

            anim.start()
            try:
                ai_message = get_ai_response(messages)
            finally:
                anim.stop()

            # Display AI Response using Panel and Markdown
            md = Markdown(ai_message)
            console.print(Panel(md, title="[bold green][SYSTEM][/bold green]", border_style="green", expand=False))
            console.print()
            
            messages.append({"role": "assistant", "content": ai_message})

        except KeyboardInterrupt:
            console.print(f"\n[bold yellow]SIGINT received. Exiting.[/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red][!] FATAL: {e}[/bold red]")

if __name__ == "__main__":
    main()

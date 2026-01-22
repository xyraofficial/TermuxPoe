import os
import sys
import time
import json
import requests
import threading
import itertools

# Poe API Configuration
api_key = os.getenv("POE_API_KEY")

if not api_key:
    print("\033[91mError: POE_API_KEY not found in environment variables.\033[0m")
    print("Please set it using: export POE_API_KEY='your_api_key'")
    sys.exit(1)

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_banner():
    # Banner lebih ramping agar tidak terpotong di layar HP/Termux
    banner = f"""{DIM}# Environment: AI-TERMINAL-X1
# Protocol: POE-v1-SECURE{RESET}
{CYAN}{BOLD}┌───────────────────────────────────┐
│ {WHITE}~/firmware{CYAN} > {GREEN}AI CHATBOT ENGINE{CYAN}    │
└───────────────────────────────────┘{RESET}"""
    print(banner)

def typing_print(text, delay=0.005):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

class FirmwareAnimation:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def animate(self):
        # Animasi loading bulat (dots/circles)
        stages = [
            "Initializing neural link",
            "Accessing memory blocks",
            "Decrypting response data",
            "Finalizing stream"
        ]
        # Karakter bulat/dots: ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ atau yang lebih simpel seperti 🌑🌒🌓🌔🌕
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
    clear_screen()
    draw_banner()
    
    messages = []
    anim = FirmwareAnimation()

    while True:
        try:
            user_input = input(f"{CYAN}{BOLD}~/firmware{RESET} {WHITE}>{RESET} ")
            
            if user_input.lower() in ['exit', 'quit', ':q']:
                print(f"\n{DIM}Terminating session... Done.{RESET}")
                break
                
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            anim.start()
            try:
                ai_message = get_ai_response(messages)
            finally:
                anim.stop()

            print(f"{GREEN}{BOLD}[SYSTEM]{RESET} ", end="", flush=True)
            typing_print(ai_message)
            
            messages.append({"role": "assistant", "content": ai_message})
            print()

        except KeyboardInterrupt:
            print(f"\n{RED}SIGINT received. Exiting.{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}[!] FATAL: {e}{RESET}")

if __name__ == "__main__":
    main()

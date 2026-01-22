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
BOLD = "\033[1m"
RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_banner():
    banner = f"""
{CYAN}{BOLD}
   █████╗ ██╗     ████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗
  ██╔══██╗██║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║╚██╗██╔╝
  ███████║██║█████╗  ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║ ╚███╔╝ 
  ██╔══██║██║╚════╝  ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║ ██╔██╗ 
  ██║  ██║██║        ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗
  ╚═╝  ╚═╝╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
{RESET}{YELLOW}          Termux AI Chatbot (Poe API - Direct Access)
{RESET}"""
    print(banner)

def typing_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

class ThinkingAnimation:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def animate(self):
        # Cool thinking animation
        chars = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        colors = itertools.cycle([CYAN, BLUE, MAGENTA])
        while not self.stop_event.is_set():
            char = next(chars)
            color = next(colors)
            sys.stdout.write(f"\r{color}{BOLD} {char} AI sedang berpikir...{RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 30 + "\r")
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
        raise Exception(f"API Error: {str(e)}")

def main():
    clear_screen()
    draw_banner()
    print(f"{YELLOW}Type 'exit' or 'quit' to leave.{RESET}\n")

    messages = []
    anim = ThinkingAnimation()

    while True:
        try:
            user_input = input(f"{GREEN}{BOLD}❯❯ {RESET}")
            
            if user_input.lower() in ['exit', 'quit']:
                print(f"\n{YELLOW}Terima kasih telah menggunakan AI Termux. Sampai jumpa!{RESET}")
                break
                
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            # Start animation
            anim.start()
            
            try:
                ai_message = get_ai_response(messages)
            finally:
                # Stop animation regardless of success/fail
                anim.stop()

            print(f"{CYAN}{BOLD}AI ❯ {RESET}", end="", flush=True)
            typing_print(ai_message)
            
            messages.append({"role": "assistant", "content": ai_message})
            print()

        except KeyboardInterrupt:
            print(f"\n{YELLOW}Keluar...{RESET}")
            break
        except Exception as e:
            print(f"\n{RED}Terjadi kesalahan: {e}{RESET}")

if __name__ == "__main__":
    main()

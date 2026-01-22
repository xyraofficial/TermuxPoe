import os
import sys
import time
import json
import requests

# Poe API Configuration
api_key = os.getenv("POE_API_KEY")

if not api_key:
    print("\033[91mError: POE_API_KEY not found in environment variables.\033[0m")
    print("Please set it using: export POE_API_KEY='your_api_key'")
    sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typing_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

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
    print("\033[94m" + "="*50)
    print("       🚀 AI ChatBot Termux (Poe API) 🚀")
    print("       (No Library OpenAI Required)    ")
    print("="*50 + "\033[0m")
    print("Model: Claude-3.5-Sonnet")
    print("Ketik 'exit' atau 'quit' untuk keluar.\n")

    messages = []

    while True:
        try:
            user_input = input("\033[92mAnda: \033[0m")
            
            if user_input.lower() in ['exit', 'quit']:
                print("\033[93mSampai jumpa!\033[0m")
                break
                
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            print("\033[94mAI: \033[0m", end="", flush=True)
            
            ai_message = get_ai_response(messages)
            typing_print(ai_message)
            
            messages.append({"role": "assistant", "content": ai_message})
            print()

        except KeyboardInterrupt:
            print("\n\033[93mKeluar...\033[0m")
            break
        except Exception as e:
            print(f"\n\033[91mTerjadi kesalahan: {e}\033[0m")

if __name__ == "__main__":
    main()

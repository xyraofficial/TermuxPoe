import os
import sys
import time
from openai import OpenAI

# Poe API Configuration
# Get API key from environment variable
api_key = os.getenv("POE_API_KEY")

if not api_key:
    print("\033[91mError: POE_API_KEY not found in environment variables.\033[0m")
    print("Please set it using: export POE_API_KEY='your_api_key'")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.poe.com/v1",
)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typing_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    clear_screen()
    print("\033[94m" + "="*50)
    print("       🚀 AI ChatBot Termux (Poe API) 🚀")
    print("="*50 + "\033[0m")
    print("Model: Claude-Opus-3.5")
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
            
            # Request to Poe API
            response = client.chat.completions.create(
                extra_headers={
                    "X-Title": "Termux AI Bot",
                },
                model="Claude-3.5-Sonnet", # Using a common reliable model name for Poe
                messages=messages,
                stream=False
            )

            ai_message = response.choices[0].message.content
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

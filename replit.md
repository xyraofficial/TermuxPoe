# AI ChatBot Termux (Poe API) - No OpenAI Library

Script Python untuk menjalankan AI ChatBot di Termux menggunakan Poe API tanpa perlu menginstall library `openai`.

## Persyaratan
- Python 3.x
- Requests Library (`pip install requests`)
- Poe API Key (dapatkan di [poe.com/api_key](https://poe.com/api_key))

## Cara Menjalankan di Termux

1. Update package dan install python:
   ```bash
   pkg update && pkg upgrade
   pkg install python
   ```

2. Install library requests (lebih ringan daripada openai):
   ```bash
   pip install requests
   ```

3. Set API Key Poe:
   ```bash
   export POE_API_KEY='isi_api_key_poe_anda'
   ```

4. Jalankan bot:
   ```bash
   python bot.py
   ```

## Catatan
Script ini menggunakan HTTP requests langsung ke API Poe, sehingga sangat ringan dan tidak membutuhkan dependensi library `openai` yang besar.

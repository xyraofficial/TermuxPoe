# AI ChatBot Termux (Poe API)

Script Python untuk menjalankan AI ChatBot di Termux menggunakan Poe API.

## Persyaratan
- Python 3.x
- OpenAI Python Library (`pip install openai`)
- Poe API Key (dapatkan di [poe.com/api_key](https://poe.com/api_key))

## Cara Menjalankan di Termux

1. Update package dan install python:
   ```bash
   pkg update && pkg upgrade
   pkg install python
   ```

2. Install library openai:
   ```bash
   pip install openai
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
Model yang digunakan adalah `Claude-3.5-Sonnet`. Anda bisa mengubah model di file `bot.py` sesuai kebutuhan.

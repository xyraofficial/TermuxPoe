# AI ChatBot Termux (Poe API) - No OpenAI Library

Script Python untuk menjalankan AI ChatBot di Termux menggunakan Poe API tanpa perlu menginstall library `openai`.

## Persyaratan
- Python 3.x
- Requests & Rich Library (`pip install requests rich`)
- Poe API Key (dapatkan di [poe.com/api_key](https://poe.com/api_key))

## Cara Menjalankan di Termux

1. Update package dan install python:
   ```bash
   pkg update && pkg upgrade
   pkg install python
   ```

2. Install library:
   ```bash
   pip install requests rich
   ```

3. Set API Key Poe:
   ```bash
   export POE_API_KEY='isi_api_key_poe_anda'
   ```

4. Jalankan bot:
   ```bash
   python bot.py
   ```

## Fitur
- **Rich Panel**: Tampilan respons AI dalam panel yang rapi.
- **Markdown Support**: Mendukung rendering Markdown (bold, list, code blocks, dll).
- **Firmware UI**: Estetika terminal ala `~/firmware`.
- **Lightweight**: Tidak butuh library `openai`.

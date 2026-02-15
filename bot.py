import requests
from pyrogram import Client, filters

# ================== CONFIG ==================
API_ID = 21552265          # yaha apna api_id daalo
API_HASH = "1c971ae7e62cc416ca977e040e700d09" # yaha apna api_hash daalo
BOT_TOKEN = "6580496721:AAE0E4NMPUUX2jpHy-SWV5boVCreQeWt6CY"  # yaha bot token daalo

MODEL_NAME = "tinyllama"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
# ============================================

app = Client(
    "ai_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def get_ai_response(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        result = response.json()
        return result.get("response", "Kuch samajh nahi aaya 🤔")[:300]

    except Exception as e:
        return "Server thoda busy hai ⚠️"

@app.on_message(filters.text & ~filters.command("start"))
def chat(client, message):
    user_text = message.text

    reply = get_ai_response(user_text)

    message.reply_text(reply)


@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hello 👋\nMain AI Bot hoon.\nMujhse kuch bhi pucho 😎")


print("🤖 Bot Running...")
app.run()

"""
Hybrid Telegram Bot
Learning + Local AI (Ollama)
Owner Secured
"""

import json
import os
import random
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# 🔑 CONFIG
# ==============================

TOKEN = "6580496721:AAE0E4NMPUUX2jpHy-SWV5boVCreQeWt6CY"
OWNER_ID = 8525538455
BOT_NAME = "SmartBot"
DATA_FILE = "conversation_data.json"

# ==============================
# 📂 DATA FUNCTIONS
# ==============================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"conversations": {}, "learned_responses": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==============================
# 🧹 CLEAN TEXT
# ==============================

def clean_text(text):
    remove_words = ["rocky", "ROCKY"]
    for word in remove_words:
        text = text.replace(word, "")
    return text.strip()

# ==============================
# 🤖 AI FUNCTION (OLLAMA)
# ==============================

def get_ai_response(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        return response.json()["response"]
    except:
        return None

# ==============================
# 🧠 LEARNING SYSTEM
# ==============================

def learn_response(user_id, user_message, bot_message):
    data = load_data()

    if user_id not in data["conversations"]:
        data["conversations"][user_id] = []

    data["conversations"][user_id].append({
        "user": user_message,
        "bot": bot_message,
        "time": datetime.now().isoformat()
    })

    words = user_message.lower().split()
    for word in words:
        if len(word) > 3:
            if word not in data["learned_responses"]:
                data["learned_responses"][word] = []
            if bot_message not in data["learned_responses"][word]:
                data["learned_responses"][word].append(bot_message)

    if len(data["conversations"][user_id]) > 100:
        data["conversations"][user_id] = data["conversations"][user_id][-100:]

    save_data(data)

def get_learned_response(message):
    data = load_data()
    words = message.lower().split()

    for word in words:
        if word in data["learned_responses"]:
            responses = data["learned_responses"][word]
            if responses:
                return random.choice(responses)

    return None

# ==============================
# 📌 COMMANDS
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Namaste 🙏\nMain {BOT_NAME} hoon.\nAI + Learning Mode Active 🔥"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only owner allowed.")
        return

    save_data({"conversations": {}, "learned_responses": {}})
    await update.message.reply_text("✅ Memory cleared.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    total = sum(len(v) for v in data["conversations"].values())
    await update.message.reply_text(
        f"Users: {len(data['conversations'])}\n"
        f"Messages: {total}\n"
        f"Learned Words: {len(data['learned_responses'])}"
    )

# ==============================
# 💬 MESSAGE HANDLER
# ==============================

last_replies = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)
    message_text = clean_text(update.message.text)

    if not message_text:
        return

    # 1️⃣ Check learned JSON
    learned = get_learned_response(message_text)

    if learned:
        response = learned
    else:
        # 2️⃣ AI fallback
        ai_reply = get_ai_response(message_text)
        if ai_reply:
            response = ai_reply[:700]
        else:
            # 3️⃣ Stylish fallback
            response = random.choice([
                "🔥 Interesting!",
                "😎 Vibe mast hai!",
                "⚡ Energy detected!",
                "🧠 Processing..."
            ])

    # Anti repeat
    if user_id in last_replies and last_replies[user_id] == response:
        return

    last_replies[user_id] = response

    await update.message.reply_text(response)
    learn_response(user_id, message_text, response)

# ==============================
# 🚀 MAIN
# ==============================

def main():
    print("🔥 Hybrid AI Bot Running...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()

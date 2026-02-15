"""
Secure Telegram Learning Bot
Owner Protected | No Name Spam | Anti Repeat
"""

import json
import os
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# 🔑 CONFIG
# ==============================

TOKEN = "PASTE_NEW_TOKEN_HERE"
OWNER_ID = 8525538455
BOT_NAME = "SmartBot"
DATA_FILE = "conversation_data.json"

# ==============================
# 📂 DATA SYSTEM
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
                return responses[-1]

    return None

# ==============================
# 📌 COMMANDS
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Namaste 🙏\nMain {BOT_NAME} hoon.\nMain seekhta hoon aur reply karta hoon."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n/help\n/learn\n/stats\n/clear (Owner Only)"
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

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    await update.message.reply_text(
        f"Learning Words: {len(data['learned_responses'])}"
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

    learned = get_learned_response(message_text)

    if learned:
        response = clean_text(learned)
    else:
        msg = message_text.lower()

        if any(w in msg for w in ["hello", "hi", "hey", "namaste"]):
            response = f"Namaste {user.first_name}! 🙏"
        elif "how are you" in msg:
            response = "Main badhiya hoon 😊"
        elif "who are you" in msg:
            response = f"Main {BOT_NAME} hoon."
        elif "?" in msg:
            response = "Achha sawaal hai 🤔"
        else:
            response = random.choice([
                "Samajh gaya 👍",
                "Interesting 😄",
                "Aur batao!",
                "Nice 🙂"
            ])

    # Anti repeat spam
    if user_id in last_replies and last_replies[user_id] == response:
        return

    last_replies[user_id] = response

    await update.message.reply_text(response)
    learn_response(user_id, message_text, response)

# ==============================
# 🚀 MAIN
# ==============================

def main():
    print("Bot Running Secure Mode...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()

"""
Telegram Chat Bot with Data Storage (Owner Secured Version)
Only bot owner can use /clear command
"""

import json
import os
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# 🔑 BOT CONFIGURATION
# ==============================

TOKEN = "YOUR_TOKEN_HERE"  # <-- Apna Bot Token yaha daalo
OWNER_ID = 123456789  # <-- Apna Telegram User ID yaha daalo

BOT_NAME = "SmartBot"
DATA_FILE = "conversation_data.json"

# ==============================
# 📂 DATA FUNCTIONS
# ==============================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"conversations": {}, "learned_responses": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
        "timestamp": datetime.now().isoformat()
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
    message_lower = message.lower()

    words = message_lower.split()
    for word in words:
        if word in data["learned_responses"]:
            responses = data["learned_responses"][word]
            if responses:
                return responses[-1]

    for key in data["learned_responses"]:
        if key in message_lower and data["learned_responses"][key]:
            return data["learned_responses"][key][-1]

    return None

# ==============================
# 📌 COMMANDS
# ==============================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello! I'm {BOT_NAME} 🤖\n\n"
        "I work in groups and learn from conversations!\n\n"
        "📌 Available Commands:\n"
        "/start\n"
        "/help\n"
        "/learn\n"
        "/clear (Owner Only)\n"
        "/stats\n",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Help Menu\n\n"
        "• /start - Start bot\n"
        "• /help - Show help\n"
        "• /learn - Learning stats\n"
        "• /clear - Owner only\n"
        "• /stats - Show stats"
    )

async def learn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    learned_count = len(data["learned_responses"])
    conv_count = sum(len(v) for v in data["conversations"].values())

    await update.message.reply_text(
        f"📚 Learning Stats\n\n"
        f"Learned responses: {learned_count}\n"
        f"Total conversations: {conv_count}\n"
        f"Users: {len(data['conversations'])}"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    total_convs = sum(len(v) for v in data["conversations"].values())
    total_learned = len(data["learned_responses"])

    await update.message.reply_text(
        f"📊 Statistics\n\n"
        f"Total conversations: {total_convs}\n"
        f"Learned patterns: {total_learned}\n"
        f"Users: {len(data['conversations'])}"
    )

# 🔒 OWNER ONLY CLEAR
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can use this command!")
        return

    data = {"conversations": {}, "learned_responses": {}}
    save_data(data)

    await update.message.reply_text("✅ Memory cleared successfully by owner!")

# ==============================
# 💬 MESSAGE HANDLER
# ==============================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    user = update.message.from_user
    user_name = user.first_name if user.first_name else "User"
    user_id = str(user.id)

    learned_resp = get_learned_response(message_text)

    if learned_resp:
        response = learned_resp
    else:
        msg_lower = message_text.lower()

        if any(word in msg_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            response = f"Namaste {user_name}! 🙏"
        elif 'how are you' in msg_lower:
            response = "I'm doing great! 😊"
        elif 'who are you' in msg_lower:
            response = f"I'm {BOT_NAME}, your smart learning bot!"
        elif '?' in message_text:
            response = "Good question! I'm still learning 😊"
        else:
            responses = [
                f"Interesting! Tell me more, {user_name}.",
                f"Oh! {message_text} - that's cool!",
                f"I see! Thanks for sharing, {user_name}.",
                f"Aur batao {user_name}! 😄"
            ]
            response = random.choice(responses)

    await update.message.reply_text(response)
    learn_response(user_id, message_text, response)

# ==============================
# 🚀 MAIN FUNCTION
# ==============================

def main():
    print("Starting Secure Telegram Bot...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("learn", learn_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()

"""
Telegram Chat Bot with Data Storage
A bot that works in groups and stores conversation data locally.
"""

import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Your Bot Token from @BotFather
# Replace 'YOUR_TOKEN_HERE' with your actual bot token
TOKEN = "YOUR_TOKEN_HERE"

# Bot configuration
BOT_NAME = "SmartBot"
DATA_FILE = "conversation_data.json"

# Load or initialize conversation data
def load_data():
    """Load conversation data from file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"conversations": {}, "learned_responses": {}}

def save_data(data):
    """Save conversation data to file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Learn from conversations
def learn_response(user_id, user_message, bot_message):
    """Learn from conversation to respond naturally"""
    data = load_data()
    
    # Store conversation
    if user_id not in data["conversations"]:
        data["conversations"][user_id] = []
    
    # Add to conversation history
    data["conversations"][user_id].append({
        "user": user_message,
        "bot": bot_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Learn simple responses (keyword-based learning)
    words = user_message.lower().split()
    for word in words:
        if len(word) > 3:  # Only learn meaningful words
            if word not in data["learned_responses"]:
                data["learned_responses"][word] = []
            if bot_message not in data["learned_responses"][word]:
                data["learned_responses"][word].append(bot_message)
    
    # Keep only last 100 conversations per user
    if len(data["conversations"][user_id]) > 100:
        data["conversations"][user_id] = data["conversations"][user_id][-100:]
    
    save_data(data)

# Get intelligent response based on learned data
def get_learned_response(message):
    """Get response based on learned data"""
    data = load_data()
    message_lower = message.lower()
    
    # Check for learned responses
    words = message_lower.split()
    for word in words:
        if word in data["learned_responses"]:
            responses = data["learned_responses"][word]
            if responses:
                return responses[-1]  # Return most recent learned response
    
    # Check for learned patterns
    for key in data["learned_responses"]:
        if key in message_lower and data["learned_responses"][key]:
            return data["learned_responses"][key][-1]
    
    return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        f"Hello! I'm {BOT_NAME} 🤖\n\n"
        "I work in groups and learn from conversations!\n\n"
        "📌 Available Commands:\n"
        "/start - Welcome message\n"
        "/help - Help menu\n"
        "/learn - Show what I've learned\n"
        "/clear - Clear my memory\n"
        "/stats - Show conversation stats\n\n"
        "Just talk to me and I'll learn from you!",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "📖 <b>Help Menu</b>\n\n"
        "Commands:\n"
        "• /start - Start the bot\n"
        "• /help - Show help\n"
        "• /learn - See what I've learned\n"
        "• /clear - Clear my memory\n"
        "• /stats - Conversation stats\n\n"
        "I learn from group conversations and respond naturally!",
        parse_mode='HTML'
    )

async def learn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show what the bot has learned"""
    data = load_data()
    learned_count = len(data["learned_responses"])
    conv_count = sum(len(v) for v in data["conversations"].values())
    
    await update.message.reply_text(
        f"📚 <b>My Learning Stats</b>\n\n"
        f"• Learned responses: {learned_count}\n"
        f"• Total conversations: {conv_count}\n"
        f"• Users talked to: {len(data['conversations'])}\n\n"
        f"I'm getting smarter every day!",
        parse_mode='HTML'
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear bot's memory"""
    data = {"conversations": {}, "learned_responses": {}}
    save_data(data)
    await update.message.reply_text("✅ I've cleared my memory! Starting fresh!")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show conversation stats"""
    data = load_data()
    total_convs = sum(len(v) for v in data["conversations"].values())
    total_learned = len(data["learned_responses"])
    
    await update.message.reply_text(
        f"📊 <b>Statistics</b>\n\n"
        f"Total conversations: {total_convs}\n"
        f"Learned patterns: {total_learned}\n"
        f"Users: {len(data['conversations'])}",
        parse_mode='HTML'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages - works in groups and learns!"""
    message_text = update.message.text
    user = update.message.from_user
    user_name = user.first_name if user.first_name else "User"
    user_id = str(user.id)
    chat_id = str(update.message.chat.id)
    
    is_group = update.message.chat.type in ['group', 'supergroup']
    
    # Generate response
    learned_resp = get_learned_response(message_text)
    
    if learned_resp:
        response = learned_resp
    else:
        # Default responses based on message
        msg_lower = message_text.lower()
        
        if any(word in msg_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            response = f"Namaste {user_name}! 🙏"
        elif 'how are you' in msg_lower:
            response = "I'm doing great! Thanks for asking 😊"
        elif 'who are you' in msg_lower:
            response = f"I'm {BOT_NAME}, your friendly group bot! I learn from conversations."
        elif '?' in message_text:
            response = "Good question! I'm still learning 😊"
        else:
            # Default echo with variation
            responses = [
                f"Interesting! Tell me more, {user_name}.",
                f"Oh! {message_text} - that's cool!",
                f"I see! Thanks for sharing, {user_name}.",
                f"Aur batao {user_name}! 😄"
            ]
            import random
            response = random.choice(responses)
    
    # Send response
    await update.message.reply_text(response)
    
    # Learn from this conversation
    learn_response(user_id, message_text, response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Update {update} caused error {context.error}")

def main():
    """Main function to run the bot"""
    print("Starting Telegram Bot with Data Storage...")
    print("Bot will learn from conversations and work in groups!")
    
    # Create the application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("learn", learn_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Add message handler - works for both groups and private
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()

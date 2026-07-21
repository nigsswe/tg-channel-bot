import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

scheduled_jobs = {}

TOPICS = [
    "AI и технологии",
    "Программирование",
    "Стартапы и бизнес",
    "Автоматизация",
    "Фриланс и заработок",
    "Нейросети",
    "Лайфхаки для разработчиков",
    "Обзоры инструментов",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для управления каналом.\n\n"
        "Команды:\n"
        "/post — сгенерировать и опубликовать пост\n"
        "/topic <тема> — пост на заданную тему\n"
        "/schedule <минуты> — автопостинг\n"
        "/stop — остановить автопостинг\n"
        "/topics — список тем"
    )

async def topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Доступные темы:\n\n"
    for i, t in enumerate(TOPICS, 1):
        text += f"{i}. {t}\n"
    text += "\nИспользуй /topic <название> для генерации поста"
    await update.message.reply_text(text)

async def generate_post(topic=None):
    if not client:
        return "⚠️ Не настроен OpenAI API ключ"

    prompt = f"""Напиши пост для Telegram-канала о технологиях и AI.

Тема: {topic or 'любая интересная тема из мира AI/tech'}

Требования:
- Объём 200-400 слов
- Интересный заголовок
- Польза для читателя
- Эмодзи для украшения
- В конце вопрос для вовлечения
- Хэштеги в конце

Пиши на русском. Стиль: дружелюбный, но профессиональный."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.8
    )

    return response.choices[0].message.content

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not CHANNEL_ID:
        await update.message.reply_text("⚠️ CHANNEL_ID не настроен в .env")
        return

    await update.message.reply_text("Генерирую пост...")

    content = await generate_post()

    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=content)
        await update.message.reply_text("✅ Пост опубликован!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи тему: /topic нейросети")
        return

    topic_text = " ".join(context.args)

    if not CHANNEL_ID:
        await update.message.reply_text("⚠️ CHANNEL_ID не настроен в .env")
        return

    await update.message.reply_text(f"Генерирую пост на тему: {topic_text}...")

    content = await generate_post(topic_text)

    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=content)
        await update.message.reply_text("✅ Пост опубликован!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи интервал: /schedule 60 (каждые 60 минут)")
        return

    try:
        minutes = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Укажи число минут")
        return

    if minutes < 5:
        await update.message.reply_text("Минимум 5 минут")
        return

    chat_id = update.effective_chat.id

    if chat_id in scheduled_jobs:
        scheduled_jobs[chat_id].cancel()

    async def auto_post(context_job):
        if not CHANNEL_ID:
            return
        content = await generate_post()
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=content)
            logging.info(f"Auto-posted to {CHANNEL_ID}")
        except Exception as e:
            logging.error(f"Auto-post error: {e}")

    job_queue = context.job_queue
    job = job_queue.run_repeating(auto_post, interval=minutes * 60, first=minutes * 60)
    scheduled_jobs[chat_id] = job

    await update.message.reply_text(f"✅ Автопостинг каждые {minutes} минут")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in scheduled_jobs:
        scheduled_jobs[chat_id].cancel()
        del scheduled_jobs[chat_id]
        await update.message.reply_text("⏹ Автопостинг остановлен")
    else:
        await update.message.reply_text("Автопостинг не запущен")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("topics", topics))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("topic", topic))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("stop", stop))

    logging.info("Channel bot started!")
    app.run_polling()

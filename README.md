# 📢 Telegram Channel Bot

Бот для автоматического управления Telegram-каналом. Генерирует контент через AI и публикует по расписанию.

## Возможности

- Автопостинг по расписанию
- AI-генерация постов
- Команда /post для ручной публикации
- Команда /schedule для настройки расписания
- Команда /topic для генерации поста по теме

## Быстрый старт

### 1. Установи зависимости

```bash
pip install -r requirements.txt
```

### 2. Создай .env

```bash
cp .env.example .env
```

### 3. Вставь токены

```
TELEGRAM_BOT_TOKEN=your_bot_token
CHANNEL_ID=@your_channel_name
OPENAI_API_KEY=your_key
```

### 4. Запусти

```bash
python bot.py
```

## Как настроить

1. Создай канал в Telegram
2. Добавь бота администратором
3. Узнай CHANNEL_ID (переслай сообщение в @userinfobot)
4. Вставь в .env

## Команды

- `/start` — приветствие
- `/post` — сгенерировать и опубликовать пост
- `/topic <тема>` — пост на заданную тему
- `/schedule <минуты>` — автопостинг каждые N минут
- `/stop` — остановить автопостинг

## Стек

- Python 3.10+
- python-telegram-bot
- openai

## Лицензия

MIT

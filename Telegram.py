from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import time

# Глобальная переменная для отслеживания количества слов
word_count = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение при старте бота."""
    await update.message.reply_text(
        "Привет! Я бот, который поможет тебе учить чешские слова! Каждое утро я буду напоминать о словах. "
        "Просто отправь их мне в чат, и я посчитаю."
    )


async def check_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает слова от пользователя."""
    global word_count
    words = update.message.text.split()
    word_count += len(words)
    remaining = 15 - word_count
    if word_count >= 15:
        await update.message.reply_text("Хорошего дня, чемпион! Ты отправил все слова 🎉")
        word_count = 0  # Сбрасываем счетчик после выполнения задачи
    else:
        await update.message.reply_text(f"Молодец! Осталось ещё {remaining} слов.")


async def morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Напоминание утром в 7:00."""
    chat_id = context.job.chat_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="Напоминание от телеграмм бота, созданного Марком Брагутой! 📚 "
             "Не забудь повторить чешские слова и отправить их в чат!"
    )


async def evening_check(context: ContextTypes.DEFAULT_TYPE):
    """Проверяет слова вечером в 20:00."""
    global word_count
    chat_id = context.job.chat_id
    if word_count == 0:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Эй! Уже 20:00, а ты не отправил ни одного слова. Так дела не делаются! 😡"
        )
    else:
        remaining = 15 - word_count
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Ты отправил {word_count} слов. Осталось ещё {remaining}. Не забывай, чемпион!"
        )


async def set_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Устанавливает напоминания на 7:00 и 20:00."""
    chat_id = update.message.chat_id
    scheduler = BackgroundScheduler()
    scheduler.start()

    # Утреннее напоминание
    scheduler.add_job(
        morning_reminder,
        'cron',
        hour=7,
        minute=0,
        args=(context,),
        id="morning_reminder"
    )
    # Вечерняя проверка
    scheduler.add_job(
        evening_check,
        'cron',
        hour=20,
        minute=0,
        args=(context,),
        id="evening_check"
    )
    await update.message.reply_text("Напоминания успешно установлены!")


def main():
    """Основная функция запуска бота."""
    app = Application.builder().token("7853472490:AAGDx1sj8yA38zmLACxl4iwl7Cl92YswpJw").build()

    # Хендлеры команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_reminders", set_reminders))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_words))

    print("Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()


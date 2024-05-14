from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, \
    CallbackContext
import logging
import time
from utils import setup_logger, valid_url
from datetime import datetime
from api_keys import TOKEN
from summarize import summarize
from get_news import get_news, get_text, collect_news
logger = setup_logger()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Мои команды здесь: /help')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('/summarize [текст] - Суммаризирует Ваш текст\n'
                                    '/scoop - Последние новости из РФ\n'
                                    '/link [ссылка] - Суммаризация новостей по вашей ссылке\n'
                                    '/news - Сбор новостей')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    response = 'Такой команды нет...'
    await update.message.reply_text(response)


async def on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'(!) Update {update} caused {context.error}')
    if update:
        if update.effective_message:
            chat_id = update.effective_message.chat_id
            await context.bot.send_message(chat_id=chat_id, text=f"Error! {context.error}")


async def scoop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = None
    await update.message.reply_text('Собираю новости...')

    if context.args:
        try:
            amount = int(context.args[0])
            if 0 < amount <= 15:
                news = get_news(amount)
            else:
                await update.message.reply_text(f'Incorrect argument! {amount} should be 1-15')
        except Exception as e:
            await update.message.reply_text(f'Incorrect argument! {e}')

    else:
        news = get_news()

    if news:
        response = ''
        for link, text in news:
            response += '\u26AA ' + f"{summarize(text).split('.')[0]}." + f' [Источник]({link})' + '\n'

        await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)

    else:
        await update.message.reply_text(f'Something went wrong getting news..')


async def summ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        message = ' '.join(context.args)
        response = summarize(message)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text('Incorrect entry!')


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:

        status, text = get_text(context.args[0])
        if status:
            response = summarize(text, mode='link')
            await update.message.reply_text(response)
        else:
            await update.message.reply_text('Неправильная ссылка!')

    else:
        await update.message.reply_text('Введите ссылку... /link ссылка')


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺", callback_data='Russia'),
            InlineKeyboardButton("🇧🇾", callback_data='Belarus'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    reply = f"Откуда собираем новости? \n" \
            f"🇷🇺 - Россия\n" \
            f"🇧🇾 - Беларусь"

    await update.message.reply_text(text=reply, reply_markup=reply_markup)


async def inline_button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'Russia':
        await query.edit_message_text(text='Собираю новости. Это займет время...')
        news = collect_news('ru')
        response = ''
        for link, text in news:
            response += '\u26AA ' + f"{summarize(text).split('.')[0]}." + f' [Источник]({link})' + '\n'
        await query.edit_message_text(text=response, parse_mode='Markdown', disable_web_page_preview=True)
    elif query.data == 'Belarus':
        await query.edit_message_text(text='Собираю новости. Это займет время...')
        news = collect_news('by')
        response = ''
        for link, text in news:
            response += '\u26AA ' + f"{summarize(text).split('.')[0]}." + f' [Источник]({link})' + '\n'
        await query.edit_message_text(text=response, parse_mode='Markdown', disable_web_page_preview=True)



if __name__ == '__main__':
    logging.info('Bot starting...')
    starting_time = datetime.now()
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('scoop', scoop))
    app.add_handler(CommandHandler('summarize', summ))
    app.add_handler(CommandHandler('link', link))
    app.add_handler(CommandHandler('news', news))
    app.add_handler(CallbackQueryHandler(inline_button_handler))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    # job_queue = app.job_queue

    # Errors
    app.add_error_handler(on_error)

    app.run_polling(poll_interval=3)

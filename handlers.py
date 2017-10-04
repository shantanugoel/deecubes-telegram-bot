import logging
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, JobQueue, Filters
from urllib.parse import urlparse

from config import BOT_TOKEN


def process_link(bot, update):
  for entry in update.message.entities:
    url = update.message.text[entry.offset:entry.offset + entry.length]
    bot.send_message(chat_id=update.message.chat_id, text="Detected link " + url)


def start(bot, update):
  bot.send_message(chat_id=update.message.chat_id, text="Hello. Send me a link or file")

def init():
  updater = Updater(token=BOT_TOKEN)
  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(
    MessageHandler(
      Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)),
      process_link
    )
  )

  updater.start_polling()
  updater.idle()

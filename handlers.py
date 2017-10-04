import logging
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, JobQueue, Filters

import config
from links import LinkProcessor


def start(bot, update):
  bot.send_message(chat_id=update.message.chat_id, text="Hello. Send me a link or file")

def init():
  link_processor = LinkProcessor()
  updater = Updater(token=config.BOT_TOKEN)
  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(
    MessageHandler(
      Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)),
      link_processor.process_links
    )
  )

  updater.start_polling()
  updater.idle()

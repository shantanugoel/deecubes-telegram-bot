import logging
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import config
from utils import restricted
from links import LinkProcessor

class Handlers():

  updater = None
  links_processor = None

  def __init__(self):
    self.updater = Updater(token=config.BOT_TOKEN)
    dispatcher = self.updater.dispatcher
    self.links_processor = LinkProcessor()

    dispatcher.add_handler(CommandHandler('start', self.start))
    dispatcher.add_handler(
      MessageHandler(
        Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)),
        self.process_links
      )
    )

    self.updater.start_polling()
    self.updater.idle()


  def start(self, bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hello. Send me a link or file")


  @restricted
  def process_links(self, bot, update):
    context = {
      'chat_id': update.message.chat_id,
      'text': update.message.text,
      'entities': update.message.entities
    }
    self.updater.job_queue.run_once(self.links_processor.process_links, 0, context=context)

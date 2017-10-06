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
      'message_id': update.message.message_id,
      'text': update.message.text,
      'entities': update.message.entities
    }
    update.message.reply_text('Processing', quote=True)
    self.updater.job_queue.run_once(self.process_links_queue, 0, context=context)


  def process_links_queue(self, bot, job):
    for entry in job.context['entities']:
      if entry.url:
        url = entry.url
      else:
        url = job.context['text'][entry.offset:entry.offset + entry.length]
      shorturl = self.links_processor.process_link(url)
      if shorturl:
        text = 'Shorturl ' + shorturl + ' created for ' + url
      else:
        text = 'Could not create shorturl for ' + url

      bot.send_message(
        chat_id=job.context['chat_id'],
        reply_to_message_id=job.context['message_id'],
        text=text
      )

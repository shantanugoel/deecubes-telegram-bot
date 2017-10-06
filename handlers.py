import logging
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import config
from utils import restricted
from links import LinkProcessor
from files import FileProcessor

class Handlers():

  updater = None
  links_processor = None
  files_processor = None

  def __init__(self):
    self.updater = Updater(token=config.BOT_TOKEN)
    dispatcher = self.updater.dispatcher
    self.links_processor = LinkProcessor()
    self.files_processor = FileProcessor()

    dispatcher.add_handler(CommandHandler('start', self.start))
    dispatcher.add_handler(
      MessageHandler(
        Filters.audio | Filters.video | Filters.photo | Filters.document | Filters.voice,
        self.process_files
      )
    )
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


  @restricted
  def process_files(self, bot, update):
    context = {
      'message': update.message,
    }
    update.message.reply_text('Processing', quote=True)
    self.updater.job_queue.run_once(self.process_files_queue, 0, context=context)


  def process_files_queue(self, bot, job):
    content = None
    message = job.context['message']
    try:
      content = message.document
    except AttributeError:
      try:
        content = message.photo
      except AttributeError:
        try:
          content = message.video
        except AttributeError:
          try:
            content = message.audio
          except AttributeError:
            try:
              content = message.voice
            except AttributeError:
              logging.warning('Unsupported file type')

    if content:
      file_id = content.file_id
      print(bot.get_file(file_id).file_path)
      print(content.file_name)
      try:
        file_name = content.file_name
      except AttributeError:
        file_name = None
      url = self.files_processor.process_file(content.file_id)
      if url:
        text = 'File uploaded to ' + url
        #TODO: Add url shortening as well
      else:
        text = 'Could not upload file'
    else:
      text = 'Unsupported file type'

    bot.send_message(
      chat_id=message.chat_id,
      reply_to_message_id=message.message_id,
      text=text
    )

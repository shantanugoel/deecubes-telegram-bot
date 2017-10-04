import logging
import os
from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, JobQueue, Filters
from urllib.parse import urlparse
from git import Repo

import config

def process_link_git(url):
  pass

def process_links(bot, update):
  for entry in update.message.entities:
    if entry.url:
      url = entry.url
    else:
      url = update.message.text[entry.offset:entry.offset + entry.length]
    bot.send_message(chat_id=update.message.chat_id, text="Detected link " + url)


def process_links_init():
  repo_path_local_base = ''
  if not config.LINKS_REPO_PATH_LOCAL_ABS:
    repo_path_local_base = os.path.expanduser('~')
  repo_path_local = os.path.join(repo_path_local_base, config.LINKS_REPO_PATH_LOCAL)
  repo = Repo.clone_from(config.LINKS_REPO_URL, repo_path_local)

def start(bot, update):
  bot.send_message(chat_id=update.message.chat_id, text="Hello. Send me a link or file")

def init():
  process_links_init()
  updater = Updater(token=config.BOT_TOKEN)
  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(
    MessageHandler(
      Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)),
      process_links
    )
  )

  updater.start_polling()
  updater.idle()

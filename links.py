import logging
import os
from urllib.parse import urlparse
from git import Repo
from telegram.error import TelegramError

import config


class LinkProcessor():

  def __init__(self):
    repo_path_local_base = ''
    if not config.LINKS_REPO_PATH_LOCAL_ABS:
      repo_path_local_base = os.path.expanduser('~')
    repo_path_local = os.path.join(repo_path_local_base, config.LINKS_REPO_PATH_LOCAL)
    repo = Repo.init(repo_path_local)
    try:
      repo.remotes.origin.exists()
      if repo.remotes.origin.url != config.LINKS_REPO_URL:
        raise TelegramError('Links repository path seems to be conflicting with another repo')
    except AttributeError:
      repo.create_remote('origin', config.LINKS_REPO_URL)
    repo.remotes.origin.pull(config.LINKS_REPO_BRANCH)


  def process_links(self, bot, update):
    for entry in update.message.entities:
      if entry.url:
        url = entry.url
      else:
        url = update.message.text[entry.offset:entry.offset + entry.length]
      bot.send_message(chat_id=update.message.chat_id, text="Detected link " + url)

  def process_link_git(self, url):
    pass

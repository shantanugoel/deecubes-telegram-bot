import logging
import os
from urllib.parse import urlparse
from git import Repo
from telegram.error import TelegramError
from deecubes.shortener import Shortener

import config


class LinkProcessor():

  repo = None
  repo_path_local = None
  shortener = None

  def __init__(self):
    repo_path_local_base = ''
    if not config.LINKS_REPO_PATH_LOCAL_ABS:
      repo_path_local_base = os.path.expanduser('~')
    self.repo_path_local = os.path.join(repo_path_local_base, config.LINKS_REPO_PATH_LOCAL)
    self.repo = Repo.init(self.repo_path_local)
    try:
      self.repo.remotes.origin.exists()
      if self.repo.remotes.origin.url != config.LINKS_REPO_URL:
        raise TelegramError('Links repository path seems to be conflicting with another repo')
    except AttributeError:
      self.repo.create_remote('origin', config.LINKS_REPO_URL)
    self.repo.remotes.origin.pull(config.LINKS_REPO_BRANCH)

    # Init Shortener
    raw_path = os.path.join(self.repo_path_local, 'raw')
    output_path = os.path.join(self.repo_path_local, 'output')
    self.shortener = Shortener(raw_path, output_path)


  def process_links(self, bot, update):
    for entry in update.message.entities:
      if entry.url:
        url = entry.url
      else:
        url = update.message.text[entry.offset:entry.offset + entry.length]
      bot.send_message(chat_id=update.message.chat_id, text="Started Processing link " + url)
      self.process_link_git(url)


  def process_link_git(self, url):
    #TODO: Add deploy key mechanism for servers
    #TODO: Need to get the generated url but need to update deecubes for that
    #TODO: Add link sanitiser either here or in deecubes to add missing scheme
    self.shortener.generate(url)

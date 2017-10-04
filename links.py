import logging
import os
from urllib.parse import urlparse
from git import Repo

import config


class LinkProcessor():

  def __init__(self):
    repo_path_local_base = ''
    if not config.LINKS_REPO_PATH_LOCAL_ABS:
      repo_path_local_base = os.path.expanduser('~')
    repo_path_local = os.path.join(repo_path_local_base, config.LINKS_REPO_PATH_LOCAL)
    #TODO: Error handling when repo already cloned
    repo = Repo.clone_from(config.LINKS_REPO_URL, repo_path_local)

  def process_links(self, bot, update):
    for entry in update.message.entities:
      if entry.url:
        url = entry.url
      else:
        url = update.message.text[entry.offset:entry.offset + entry.length]
      bot.send_message(chat_id=update.message.chat_id, text="Detected link " + url)

  def process_link_git(self, url):
    pass

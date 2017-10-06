import logging
import os
from urllib.parse import urlparse
from git import Repo, Actor
from telegram.error import TelegramError
from deecubes.shortener import Shortener

import config


class FileProcessor():

  repo = None
  repo_path_local = None
  files_path = None

  def __init__(self):
    repo_path_local_base = ''
    if not config.FILES_REPO_PATH_LOCAL_ABS:
      repo_path_local_base = os.path.expanduser('~')
    self.repo_path_local = os.path.join(repo_path_local_base, config.FILES_REPO_PATH_LOCAL)
    self.repo = Repo.init(self.repo_path_local)
    try:
      self.repo.remotes.origin.exists()
      if self.repo.remotes.origin.url != config.FILES_REPO_URL:
        raise TelegramError('Links repository path seems to be conflicting with another repo')
    except AttributeError:
      self.repo.create_remote('origin', config.FILES_REPO_URL)
    self.repo.remotes.origin.pull(config.FILES_REPO_BRANCH)
    self.repo.git.checkout(config.FILES_REPO_BRANCH)

    # Init Shortener
    self.files_path = os.path.join(self.repo_path_local, 'docs')


  def process_file(self):
    return
    #TODO: Add deploy key mechanism for servers
    self.repo.remotes.origin.pull(config.FILES_REPO_BRANCH)
    #TODO: Add file handling
    url = None

    self.repo.git.add(A=True)
    author = Actor(config.FILES_REPO_AUTHOR_NAME, config.FILES_REPO_AUTHOR_EMAIL)
    self.repo.index.commit('Added url through deecubes_bot', author=author)
    self.repo.remotes.origin.push(config.FILES_REPO_BRANCH)
    if url:
      url = config.FILES_BASE_URL + url
    return url

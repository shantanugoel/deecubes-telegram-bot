import os
from git import Repo, Actor
from telegram.error import TelegramError
from deecubes.shortener import Shortener

import config


class LinkProcessor:

  repo = None
  repo_path_local = None
  shortener = None
  ssh_cmd = 'ssh'

  def __init__(self):
    if config.LINKS_REPO_DEPLOY_KEY:
      self.ssh_cmd = 'ssh -i ' + config.LINKS_REPO_DEPLOY_KEY

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
    with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
      self.repo.remotes.origin.pull(config.LINKS_REPO_BRANCH)
    self.repo.git.checkout(config.LINKS_REPO_BRANCH)

    # Init Shortener
    raw_path = os.path.join(self.repo_path_local, 'raw')
    output_path = os.path.join(self.repo_path_local, 'output/docs')
    self.shortener = Shortener(raw_path, output_path)

  def process_link(self, url):
    with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
      self.repo.remotes.origin.pull(config.LINKS_REPO_BRANCH)
    shorturl = self.shortener.generate(url)
    self.repo.git.add(A=True)
    author = Actor(config.LINKS_REPO_AUTHOR_NAME, config.LINKS_REPO_AUTHOR_EMAIL)
    self.repo.index.commit('Added url through deecubes_bot', author=author)
    with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
      self.repo.remotes.origin.push(config.LINKS_REPO_BRANCH)
    if shorturl:
      shorturl = config.LINKS_BASE_URL + shorturl
    return shorturl

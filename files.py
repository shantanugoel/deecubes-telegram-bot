import os
from git import Repo, Actor
from telegram.error import TelegramError
from uuid import uuid4

import config


class FileProcessor:

  repo = None
  repo_path_local = None
  files_path = None
  ssh_cmd = 'ssh'

  def __init__(self):
    if config.LINKS_REPO_DEPLOY_KEY:
      self.ssh_cmd = 'ssh -i ' + config.FILES_REPO_DEPLOY_KEY

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
    with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
      self.repo.remotes.origin.pull(config.FILES_REPO_BRANCH)
    self.repo.git.checkout(config.FILES_REPO_BRANCH)

    # Init Shortener
    self.files_path = os.path.join(self.repo_path_local, 'docs')

  def process_file(self, file_obj, file_name):
    # TODO: Remove telegram download method from here
    with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
      self.repo.remotes.origin.pull(config.FILES_REPO_BRANCH)
    file_path = os.path.join(self.files_path, file_name)
    if os.path.exists(file_path):
      file_name = str(uuid4()) + '-' + file_name
      file_path = os.path.join(self.files_path, file_name)

    # TODO: Add error handling for file io exceptions
    with open(file_path, 'wb') as out:
      file_obj.download(out=out)
    self.repo.git.add(A=True)
    author = Actor(config.FILES_REPO_AUTHOR_NAME, config.FILES_REPO_AUTHOR_EMAIL)
    self.repo.index.commit('Added url through deecubes_bot', author=author)
    with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
      self.repo.remotes.origin.push(config.FILES_REPO_BRANCH)
    return config.FILES_BASE_URL + file_name

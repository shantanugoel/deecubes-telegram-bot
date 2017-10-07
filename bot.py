import logging
import argparse

from constants import VERSION
from handlers import Handlers


def main():
  parser = argparse.ArgumentParser(prog='deecubes-tg')
  parser.add_argument('-v', '--version', action='version', version='%(prog)s version ' + VERSION)
  parser.add_argument('-l', '--log', metavar='LOGLEVEL', type=int, action='store',
                      help='Set log level. 0=> Warning, 1=>Info, 2=>Debug', default=0)

  args = parser.parse_args()

  if args.log >= 2:
    log_level = logging.DEBUG
  elif args.log == 1:
    log_level = logging.INFO
  else:
    log_level = logging.WARNING
  logging.basicConfig(level=log_level, format='%(asctime)s: %(filename)s - %(message)s')

  Handlers()


if __name__ == "__main__":
  main()

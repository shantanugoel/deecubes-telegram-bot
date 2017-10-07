import logging
from functools import wraps
from PIL import Image, ImageFont, ImageDraw

from config import LIST_ALLOWED_USERS


def restricted(func):
  @wraps(func)
  def wrapped(_, bot, update, *args, **kwargs):
    user_id = update.effective_user.id
    if LIST_ALLOWED_USERS:
      if user_id not in LIST_ALLOWED_USERS:
        logging.error("Unauthorized access denied for {}.".format(user_id))
        return
    return func(_, bot, update, *args, **kwargs)

  return wrapped


def text2jpg(text, fullpath, color="#000", bgcolor="#FFF"):
  font = ImageFont.load_default()
  leftpadding = 3
  rightpadding = 3

  lines = text.split('\n')
  char_width, line_height = font.getsize(text)
  # TODO: Workaround. getsize is giving wrong width, so fix it to an approx number for now
  char_width = 6
  img_height = line_height * (len(lines) + 1)

  char_count = 0
  for line in lines:
    count = len(line)
    if count > char_count:
      char_count = count

  width = leftpadding + (char_width * char_count) + rightpadding

  img = Image.new("RGBA", (width, img_height), bgcolor)
  draw = ImageDraw.Draw(img)

  y = 0
  for line in lines:
    if line:
      draw.text((leftpadding, y), line, color, font=font)
    y += line_height

  img.save(fullpath)

import math
import random

import pygame as pg

from config import CURRENT_LANG
from data.constants import SPRITE_SIZE, BOAT_POINTS, DOCK_COLORS
from data.strings import LANGUAGES


def get_cell_size(r: int, c: int, w: int, h: int) -> int:
  """
  :param r: number of cells in row
  :param c: number of cells in column
  :param w: width of screen in pixels
  :param h: height of screen in pixels
  :return: edge length of square cell in pixels
  """
  return min(w // c, h // r)


def rc2xy(rc: tuple, cell_size: int, offset: bool = True) -> tuple:
  """
  :param rc: coordinates of cell in (row, column)
  :param cell_size: edge length of square cell in pixels
  :param offset: True: return center pixel of cell, False: return: top left pixel of cell
  :return: x, y on screen in pixels
  """
  return rc[1] * cell_size + offset * cell_size // 2, rc[0] * cell_size + offset * cell_size // 2


def toggle_zoom(zoom_in: bool) -> bool:
  return not zoom_in


def get_boat_spritesheet(size: tuple, color: str, rows: int, cols: int, width=0):

  X, Y = SPRITE_SIZE
  spritesheet = pg.Surface((X * cols, Y * rows), pg.SRCALPHA)
  image = pg.Surface(SPRITE_SIZE, pg.SRCALPHA)
  img_rect = image.get_rect()
  pg.draw.polygon(image, color, BOAT_POINTS[:5], not width)
  pg.draw.polygon(image, color, BOAT_POINTS[4:], width)
  for r in range(rows):
    for c in range(cols):
      img = pg.transform.rotate(image, c * -45)
      rect = img.get_rect(centerx=img_rect.centerx + c * X, centery=img_rect.centery + r * Y)
      spritesheet.blit(img, rect)
    image = pg.transform.flip(image, True, False)
    if r == 1:
      spi_rect = pg.Rect(8, 0, 24, 20)
      spi_rect.center = img_rect.center
      spi_rect.centery -= 5
      pg.draw.arc(image, color, spi_rect, math.pi / 12, 11 * math.pi / 12, 4)

  spritesheet = pg.transform.scale(spritesheet, (size[1]*cols, size[0]*rows))

  return spritesheet


def get_flag(name: str, size: tuple = (25, 25)) -> pg.Surface:
  flag = pg.Surface((25,25), pg.SRCALPHA)

  match name.lower():
    case "charlie":
      flag.fill('blue')
      pg.draw.rect(flag, "white", (0, 5, 25, 15), 0)
      pg.draw.rect(flag, "red", (0, 10, 25, 5), 0)
    case "juliet":
      flag.fill('blue')
      pg.draw.rect(flag, 'white', (0, 8, 25, 9), 0)
    case 'mike':
      flag.fill('royalblue4')
      pg.draw.polygon(flag, 'white', ((0,0), (2, 0), (25, 23), (25,25), (23, 25), (0,2)), 0)
      pg.draw.polygon(flag, 'white', ((25,0), (25, 2), (2, 25), (0,25), (0, 23), (23,0)), 0)
    case "oscar":
      flag.fill('yellow')
      pg.draw.polygon(flag, 'red', ((0,0), (25,0), (25,25)), 0)
    case 'romeo':
      flag.fill('red')
      pg.draw.rect(flag, 'yellow', (10, 0, 5, 25), 0)
      pg.draw.rect(flag, 'yellow', (0, 10, 25, 5), 0)
    case 'victor':
      flag.fill('white')
      pg.draw.polygon(flag, 'red', ((0, 0), (2, 0), (25, 23), (25, 25), (23, 25), (0, 2)), 0)
      pg.draw.polygon(flag, 'red', ((25, 0), (25, 2), (2, 25), (0, 25), (0, 23), (23, 0)), 0)

  flag = pg.transform.scale(flag, size)

  return flag


def get_dock(size: tuple) -> pg.Surface:
  n = 10
  x,y = size
  h = y/n
  dock = pg.Surface(size, pg.SRCALPHA)
  for board in range(n):
    pg.draw.rect(dock, random.choice(DOCK_COLORS), (0, board * h, x // 2, h), 0)
    if random.random() < 0.2:
      pg.draw.line(dock, "black", (0,board*h-1), (x//2, board*h-1))
  return dock


def gettext(key):
  """Helper function to fetch text in the current language"""
  return LANGUAGES[CURRENT_LANG].get(key, key)


if __name__ == '__main__':
    pass

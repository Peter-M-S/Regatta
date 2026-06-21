import pygame as pg

from classes.panels import IntroPanel
from data.constants import *


class MainMenu:

  def __init__(self):
    pg.init()
    self.window = pg.display.set_mode((WIDTH//2, HEIGHT//2))
    pg.display.set_caption(f'R E G A T T A')
    self.clock = pg.time.Clock()
    self.fps = FPS
    self.panel = IntroPanel(0,0, WIDTH//2, HEIGHT//2)

  def run(self) -> tuple:

    while True:
      for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE): quit()

      result = self.panel.update()
      if result is not None:
        if result == "start":
          return "start", (0,2), 0
        if result == "quit":
          return "quit", (0,0), 0

      self.window.blit(self.panel.surface, self.panel.rect.topleft)

      pg.display.update()




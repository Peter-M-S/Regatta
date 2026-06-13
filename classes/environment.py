import random
from dataclasses import dataclass

import pygame as pg

from config import *
from data.constants import *
from data.map_data import MAP_DATA
from aux.utils import rc2xy


class Wind:

  def __init__(self, map_name: str = ""):
    self.cell_size: int = MAP_DATA[map_name]["cell_size"]
    x, y = rc2xy(MAP_DATA[map_name]["windbag"], self.cell_size)
    self.position: tuple = x - self.cell_size, y - self.cell_size

    self.rose: list = DIRECTION_IDX
    spritesheet = pg.image.load("assets/windbag.png")
    h = spritesheet.get_height()
    self.spritesheet = pg.transform.scale_by(spritesheet, 2 * self.cell_size / h)
    self.set_wwd_idx(MAP_DATA[map_name]["windward_index"])

    spritesheet = pg.image.load("assets/clouds.png")
    h = spritesheet.get_height()
    self.cloud_spritesheet = pg.transform.scale_by(spritesheet, 2 * self.cell_size / h)
    self.clouds: list = []

  @property
  def lee_idx(self) -> int:
    # return opposite windward direction
    return (self.rose.index(0) + 4) % 8

  @property
  def wwd_idx(self) -> int:
    # return windward direction
    return self.rose.index(0)

  def rotate(self, rotation: str) -> None:
    match rotation:
      case 'CCW':
        self.rose = self.rose[1:] + self.rose[:1]
      case 'CW':
        self.rose = self.rose[-1:] + self.rose[:-1]
      case _:
        pass

  def set_wwd_idx(self, wwd_idx):
    wwd_idx %= 8
    self.rose = DIRECTION_IDX[-wwd_idx:] + DIRECTION_IDX[:-wwd_idx]

  def draw(self, surface: pg.Surface, legs: int = 1) -> None:
    if not SHOW_CLOUDS: return
    sr, sc = 0, self.cell_size * 2 * self.lee_idx
    sprite = pg.Surface((self.cell_size * 2, self.cell_size * 2), pg.SRCALPHA)
    sprite.blit(self.spritesheet, (-sc, -sr))
    surface.blit(sprite, self.position)
    self.update_clouds(legs)
    for c in self.clouds:
      surface.blit(c.sprite, (c.x, c.y))

  def update_clouds(self, legs: int) -> None:
    legs = max(legs, 1)
    w = WIDTH - PANEL_WIDTH
    h = HEIGHT
    dy, dx = DIRECTIONS[self.lee_idx]

    # keep only clouds visible inside panel
    self.clouds = [c for c in self.clouds if -10 <= c.x < w + 10 and -10 <= c.y < h + 10]

    if len(self.clouds) < 10 and random.random() * 5000 < (10 - len(self.clouds)) \
       or len(self.clouds) == 0:
      dw = random.randint(0, w // 4)
      dh = random.randint(0, h // 4)

      match self.wwd_idx:
        case 0:
          x, y = w // 4 + 2 * dw, 0
        case 1:
          x, y = random.choice([(3 * w // 4 + dw, 0), (w, dh)])
        case 2:
          x, y = w, h // 4 + 2 * dh
        case 3:
          x, y = random.choice([(w, 3 * h // 4 + 2 * dh), (3 * w // 4 + dw, h)])
        case 4:
          x, y = w // 4 + 2 * dw, h
        case 5:
          x, y = random.choice([(dw, h), (0, 3 * h // 4 + 2 * dh)])
        case 6:
          x, y = 0, h // 4 + 2 * dh
        case 7:
          x, y = random.choice([(dw, 0), (0, dh)])
        case _:
          x, y = w // 2, h // 2

      sprite = pg.Surface((2 * self.cell_size, 2 * self.cell_size), pg.SRCALPHA)
      sprite.blit(self.cloud_spritesheet, (-random.randint(0, 19) * 2 * self.cell_size, 0))
      v: float = random.random() + .5
      self.clouds.append(Cloud(x, y, sprite, v))

    for i, c in enumerate(self.clouds):
      self.clouds[i] = Cloud(c.x + dx * legs / 20 * c.speed, c.y + dy * legs / 20 * c.speed, c.sprite, c.speed)

  def terminal_display(self) -> None:
    print(" ".join(map(str, (self.rose[7], self.rose[0], self.rose[1]))))
    print(" ".join(map(str, (self.rose[6], "*", self.rose[2]))))
    print(" ".join(map(str, (self.rose[5], self.rose[4], self.rose[3]))))
    print()


@dataclass
class Cloud:
  x: int
  y: int
  sprite: pg.Surface
  speed: float


class Race:

  def __init__(self, map_name: str = ""):
    self.map: dict = MAP_DATA[map_name]
    self.position: tuple = self.map["race"]
    mark_line_endings = self.map["islands"].union(self.map["edges"], [self.position], self.map["dock"])
    self.marks: list = [Mark(data, mark_line_endings) for data in self.map["marks"]]
    self.cell_size: int = self.map["cell_size"]
    self.start_line = self.marks[0].first_to
    self.reverse_finish: bool = self.map["reverse_finish"]
    self.track_lines: list = self.get_track_lines()  # len(tracklines) = marks*2 + 2

    spritesheet = pg.image.load("assets/committee.png")
    h = spritesheet.get_height()
    spritesheet = pg.transform.scale_by(spritesheet, self.cell_size / h)
    self.boat = pg.Surface((self.cell_size, self.cell_size), pg.SRCALPHA)
    self.boat.blit(spritesheet, (-self.map["windward_index"] * self.cell_size, 0))

  def get_track_lines(self) -> list:
    # boat must reach positions in order of this list
    track = []
    for m in self.marks:
      track.append((m.first_from, m.first_to))
      track.append((m.second_from, m.second_to))
    if self.reverse_finish:
      track += [(self.marks[0].second_to, self.marks[0].second_from)]
      track += [(self.marks[0].first_to, self.marks[0].first_from)]
    else:
      track += [(self.marks[0].first_from, self.marks[0].first_to)]
      track += [(self.marks[0].second_from, self.marks[0].second_to)]
    return track

  def draw(self, surface: pg.Surface) -> None:

    surface.blit(self.boat, rc2xy(self.position, self.cell_size, False))
    for i, mark in enumerate(self.marks):
      mark.draw(surface, self.cell_size, show_lines=SHOW_LINES)
    if SHOW_LINES:
      line, c, w = self.start_line, "orange", 3
      points = [rc2xy(pos, self.cell_size) for pos in line]
      pg.draw.lines(surface, c, False, points, w)


class Mark:

  def __init__(self, data: tuple, mark_line_endings: set):
    self.position: tuple = data[0]
    self.first_direction: int = data[1]
    self.second_direction: int = data[2]
    r, c = self.position
    fdr, fdc = DIRECTIONS[self.first_direction]
    sdr, sdc = DIRECTIONS[self.second_direction]

    line_len = self.ray_cast_markline(mark_line_endings, self.first_direction)
    first_to: list = [(r+i*fdr, c+i*fdc) for i in range(line_len + 1)]
    dr, dc = DIRECTIONS[(self.first_direction + 2) % 8]  # 90 deg to right
    self.first_from: set = {(fr+dr, fc+dc) for fr, fc in first_to}
    self.first_to: set = set(first_to[1:-1])

    line_len = self.ray_cast_markline(mark_line_endings, self.second_direction)
    second_from: list = [(r+i*sdr, c+i*sdc) for i in range(line_len + 1)]
    dr, dc = DIRECTIONS[(self.second_direction - 2) % 8]   # 90 deg to left
    self.second_to: set = {(sr+dr, sc+dc) for sr, sc in second_from}
    self.second_from = set(second_from[1:-1])

  def draw(self, surface: pg.Surface, cell_size, show_lines: bool = SHOW_LINES) -> None:
    pg.draw.circle(surface, "darkred", rc2xy(self.position, cell_size), cell_size // 5, 0)
    pg.draw.circle(surface, "red", rc2xy(self.position, cell_size), cell_size // 6, 0)
    if show_lines:
      for line, c, w in ((self.first_from, "green", 1), (self.first_to, "red", 1),
                         (self.second_from, "green", 1), (self.second_to, "red", 1)):
        points = [rc2xy(pos, cell_size) for pos in line]
        pg.draw.lines(surface, c, False, points, w)

  def ray_cast_markline(self, targets, direction_idx) -> int:
    n, (r, c) = 0, self.position
    while (r,c) not in targets:
      r += DIRECTIONS[direction_idx][0]
      c += DIRECTIONS[direction_idx][1]
      n += 1
    return n


if __name__ == '__main__':
  pass

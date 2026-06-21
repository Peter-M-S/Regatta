import random
from collections import deque

import pygame as pg

from classes.boat import Boat
from classes.environment import Wind, Race

# from config import *
import config as cfg
from data.constants import *
from data.map_data import MAP_DATA
from aux.utils import rc2xy, get_dock, gettext

from aux.widgets import TextLabel, Button, ImageLabel

pg.init()


class Panel:

  def __init__(self, x: int, y: int, width: int, height: int):
    self.surface: pg.Surface = pg.Surface((width, height))
    self.rect: pg.Rect = self.surface.get_rect(topleft=(x, y))

  @property
  def mouse_pos(self) -> tuple:
    (mx, my), (off_x, off_y) = pg.mouse.get_pos(), self.rect.topleft
    return mx - off_x, my - off_y


class MapPanel(Panel):

  def __init__(self, x, y, width, height, map_name: str = "North Bay"):
    super().__init__(x, y, width, height)
    self.map: dict = MAP_DATA[map_name]
    self.cell_size: int = self.map["cell_size"]
    self.rows, self.cols = self.map["size"]
    self.blocked_positions: set = set()
    self.background: pg.Surface = self._draw_background()

  def _draw_background(self) -> pg.Surface:

    HALF = self.cell_size // 2
    spritesheet = pg.image.load("assets/lands.png")
    h = spritesheet.get_height()
    lands = pg.transform.scale_by(spritesheet, 2 * self.cell_size / h)

    land = pg.Surface((self.cell_size, self.cell_size), pg.SRCALPHA)
    background = pg.Surface(self.rect.size)
    background.fill('lightblue')
    pg.draw.rect(background, 'black', (0, 0, self.rect.w, self.rect.h), 1)

    # keep dock area cleared
    dr, dc = DIRECTIONS[self.map["dock offset"]]
    for r, c in self.map["dock"]:
      for i in range(1, 4):
        nr, nc = r + dr * i, c + dc * i
        if (nr, nc) in self.map["edges"]:
          self.map["edges"].remove((nr, nc))

    # draw depth and grid marks
    n = len(DEPTH_COLORS)
    depth_map: list = self.get_depth_map()
    for c in range(self.cols):
      for r in range(self.rows):
        depth = depth_map[r][c]
        if depth is None: continue
        if depth >= n: depth = n - 1
        x, y = rc2xy((r, c), self.cell_size)  # center of cell(r, c)
        pg.draw.rect(background, DEPTH_COLORS[depth], (x - HALF, y - HALF, self.cell_size, self.cell_size), 0)
        pg.draw.line(background, GRID_COLOR, (x - 3, y), (x + 3, y))
        pg.draw.line(background, GRID_COLOR, (x, y - 3), (x, y + 3))

    # draw lands
    for r, c in self.map["islands"] | self.map["edges"]:
      x, y = rc2xy((r, c), self.cell_size)
      self.blocked_positions.add((r, c))
      sc, sr = random.randint(0, 7), random.randint(0, 1)
      land.fill(pg.SRCALPHA)
      land.blit(lands, (-sc * self.cell_size, -sr * self.cell_size))
      background.blit(land, (x - HALF, y - HALF))

    # draw dock
    for r, c in self.map["dock"]:
      x, y = rc2xy((r, c), self.cell_size, False)  # topleft of cell (r,c)
      self.blocked_positions.add((r, c))

      dock: pg.Surface = get_dock((self.cell_size, self.cell_size))
      match self.map["dock offset"]:
        case 0:
          dock = pg.transform.rotate(dock, -90)
        case 2:
          dock = pg.transform.rotate(dock, 180)
        case 4:
          dock = pg.transform.rotate(dock, 90)
        case 6:
          pass
        case _:
          print("wrong orientation for dock")

      background.blit(dock, (x, y))

    return background

  def update(self, boats: deque, active_idx: int, wind: Wind,
             legs: int, race: Race, renderer: dict, zoom_in: bool, dist_maps=None):
    if cfg.DEBUG_DIST_MAPS and dist_maps is not None:
      for i, dist_map in enumerate(dist_maps):
        self.draw_dist_map(dist_map)
        pg.image.save(self.surface, f"assets/dist_map_{i:0>2}.png")
      return
    surface = self.background.copy()
    if race is not None:
      race.draw(surface)

    if boats is not None and renderer is not None:
      for b in boats: renderer[b.name].draw(surface, b, cfg.SHOW_PATH, cfg.SHOW_FLAG)

    if wind is not None and legs is not None:
      wind.draw(surface, legs, cfg.SHOW_CLOUDS)

    if zoom_in:
      if boats is not None and active_idx is not None:
        pos = boats[active_idx].position
      else:
        pos = (0, 0)
      x, y = rc2xy(pos, self.cell_size)
      zoomed_map = pg.transform.scale_by(surface, ZOOM_FACTOR)
      offset_x = self.rect.centerx - x * ZOOM_FACTOR
      offset_y = self.rect.centery - y * ZOOM_FACTOR
      self.surface.fill("Lightblue")
      self.surface.blit(zoomed_map, (offset_x, offset_y))
    else:
      self.surface.blit(surface, (0, 0))

  def get_depth_map(self):
    rows, cols = self.map["size"]
    depth_map: list = [[None] * cols for _ in range(rows)]
    blocks = self.map["edges"] | self.map["islands"]
    queue = deque()
    for r, c in blocks:
      queue.append((r, c, -1))
      depth_map[r][c] = -1

    while queue:
      r, c, d = queue.popleft()

      for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc

        # Check bounds and if it's not blocked
        if 0 <= nc < cols and 0 <= nr < rows:
          if (nr, nc) not in blocks and depth_map[nr][nc] is None:
            depth_map[nr][nc] = d + 1
            queue.append((nr, nc, d + 1))
    return depth_map

  def draw_dist_map(self, dist_map: list):
    for r in range(self.rows):
      for c in range(self.cols):
        x, y = rc2xy((r, c), self.cell_size, False)  # top left of cell(r, c)
        v = dist_map[r][c]
        if v == float("inf") or v >= 100:
          color = "black"
        else:
          color = f"grey{100 - 3 * int(v)}"
        pg.draw.rect(self.surface, color, (x, y, self.cell_size, self.cell_size), 0)


class InfoPanel(Panel):
  def __init__(self, x, y, width, height, boats=None, renderer=None):
    super().__init__(x, y, width, height)
    self.value_round: TextLabel = TextLabel((width // 4, 1 * height // 8), "-2", 25, "black")
    self.value_legs: TextLabel = TextLabel((3 * width // 4, 1 * height // 8), "0", 25, "black")
    self.label_round: TextLabel = TextLabel((width // 4, 3 * height // 8), "Round", 20, "black")
    self.label_legs: TextLabel = TextLabel((3 * width // 4, 3 * height // 8), "Legs", 20, "black")
    self.labels_order: list = self.get_labels_order(boats, renderer)

  def get_labels_order(self, boats: deque, renderer: dict) -> list:
    if boats is None: return []
    labels_order = []
    x = self.rect.w // (len(boats) + 1)
    y = 6 * self.rect.h // 8
    for i, boat in enumerate(boats):
      label = ImageLabel((x * (i + 1), y), renderer[boat.name].flag, (25, 25))
      label.update_image(new_size=(24, 16))
      labels_order.append(label)
    return labels_order

  def _draw_background(self):
    self.surface.fill(BG_COLOR_1)
    _rect = self.surface.get_rect()
    pg.draw.rect(self.surface, 'black', _rect, 1)
    pg.draw.line(self.surface, 'black', _rect.midtop, _rect.center, 1)
    pg.draw.line(self.surface, 'black', _rect.midleft, _rect.midright, 1)
    self.label_round.update(self.surface)
    self.label_legs.update(self.surface)

  def update(self, round_n: int, legs: int, boats: list, active_idx: int, renderer: dict):
    self._draw_background()
    self.value_round.update(self.surface, new_text=str(round_n))
    self.value_legs.update(self.surface, new_text=str(legs))
    if boats is not None and renderer is not None:
      for i, (label, boat) in enumerate(zip(self.labels_order, boats)):
        label.update(self.surface, new_img=renderer[boat.name].flag)
        if i == active_idx:
          x, y, w, h = label.rect
          pg.draw.rect(self.surface, boat.color, (x - 6, y - 6, w + 12, h + 12), 3)


class HUDPanel(Panel):
  def __init__(self, x, y, width, height):
    super().__init__(x, y, width, height)
    self.value_LEG: TextLabel = TextLabel((1 * width // 6, 1 * height // 8), "3", 16, "black")
    self.value_SPC: TextLabel = TextLabel((3 * width // 6, 1 * height // 8), "3", 16, "black")
    self.value_MRK: TextLabel = TextLabel((5 * width // 6, 1 * height // 8), "0/4", 16, "black")
    self.label_LEG: TextLabel = TextLabel((1 * width // 6, 3 * height // 8), "LEG", 16, "black")
    self.label_SPC: TextLabel = TextLabel((3 * width // 6, 3 * height // 8), "SPC", 16, "black")
    self.label_MRK: TextLabel = TextLabel((5 * width // 6, 3 * height // 8), "MRK", 16, "black")

    self.value_TCK: TextLabel = TextLabel((1 * width // 6, 5 * height // 8), "STB", 16, "black")
    self.value_SPI: TextLabel = TextLabel((3 * width // 6, 5 * height // 8), "NO", 16, "black")
    self.value_PUF: TextLabel = TextLabel((5 * width // 6, 5 * height // 8), "2", 16, "black")
    self.label_TCK: TextLabel = TextLabel((1 * width // 6, 7 * height // 8), "TCK", 16, "black")
    self.label_SPI: TextLabel = TextLabel((3 * width // 6, 7 * height // 8), "SPI", 16, "black")
    self.label_PUF: TextLabel = TextLabel((5 * width // 6, 7 * height // 8), "PUF", 16, "black")

  def _draw_background(self):
    self.surface.fill(BG_COLOR_1)
    _rect = self.surface.get_rect()
    pg.draw.rect(self.surface, 'black', (0, 0, self.rect.w, self.rect.h), 1)
    pg.draw.line(self.surface, 'black', (_rect.w // 3, 0), (_rect.w // 3, _rect.bottom), 1)
    pg.draw.line(self.surface, 'black', (2 * _rect.w // 3, 0), (2 * _rect.w // 3, _rect.bottom), 1)
    pg.draw.line(self.surface, 'black', _rect.midleft, _rect.midright, 1)
    self.label_LEG.update(self.surface)
    self.label_SPC.update(self.surface)
    self.label_MRK.update(self.surface)
    self.label_TCK.update(self.surface)
    self.label_SPI.update(self.surface)
    self.label_PUF.update(self.surface)

  def update(self, boat: Boat):
    self._draw_background()
    if boat is None:
      LEG_txt = "0"
      SPC_txt = "0"
      MRK_txt = f"0"
      TCK_txt = "STB"
      SPI_txt = "NO"
      PUF_txt = "2"
      color = "black"
    else:
      LEG_txt = f"{boat.legs}{"!" if boat.blanketed or boat.spinnaker_blanketed else ""}"
      SPC_txt = f"{boat.spaces}"
      MRK_txt = f"{boat.next_track_idx}/{len(boat.track_lines) - 1}"
      TCK_txt = f"{'STB' if boat.starboard_tack else "PRT"}{"!" if boat.shift_priority else ""}"
      SPI_txt = f"{"YES" if boat.spinnaker else "NO"}{"!" if boat.spinnaker_priority else ""}"
      PUF_txt = f"{boat.puffs}{"!" if boat.puff_active else ""}"
      color = boat.text_color
    self.value_LEG.update(self.surface, new_text=LEG_txt, new_color=color)
    self.value_SPC.update(self.surface, new_text=SPC_txt, new_color=color)
    self.value_MRK.update(self.surface, new_text=MRK_txt, new_color=color)
    self.value_TCK.update(self.surface, new_text=TCK_txt, new_color=color)
    self.value_SPI.update(self.surface, new_text=SPI_txt, new_color=color)
    self.value_PUF.update(self.surface, new_text=PUF_txt, new_color=color)


class SkipperPanel(Panel):
  def __init__(self, x, y, width, height):
    super().__init__(x, y, width, height)
    self.options: list = []
    self.buttons: dict = {
      s: Button((PANEL_WIDTH // 2, PANEL_HEIGHT // 2), f"Option {s}", 25, (PANEL_WIDTH, PANEL_HEIGHT),
                action=lambda s=s: s)
      for s in OPTIONS
    }

  def _draw_background(self):
    self.surface.fill('white')
    pg.draw.rect(self.surface, 'black', (0, 0, self.rect.w, self.rect.h), 1)

  def update(self, valid_options: set) -> str | None:
    self._draw_background()

    if valid_options is not None:
      self.options = sorted(valid_options, key=lambda val: OPTIONS.index(val))
    else:
      self.options = []

    for row, option in enumerate(self.options):
      self.buttons[option].y = row * PANEL_HEIGHT + PANEL_HEIGHT // 2
      selection = self.buttons[option].update(self.surface, point=self.mouse_pos, new_text=gettext(option))
      if selection is not None: return selection
    return None


class SettingsPanel(Panel):
  def __init__(self, x, y, width, height):
    super().__init__(x, y, width, height)
    self.buttons: list = [
      Button((PANEL_WIDTH // 4, PANEL_HEIGHT // 2), "Options", 25,
             (PANEL_WIDTH//2, PANEL_HEIGHT), action=lambda: "open_options"),
      Button((3 * PANEL_WIDTH // 4, PANEL_HEIGHT // 2), f"Zoom in", 25,
             (PANEL_WIDTH//2, PANEL_HEIGHT), action=lambda: "toggle_zoom")  # action= lambda s=s: s
    ]

  def _draw_background(self):
    self.surface.fill(BG_COLOR_1)
    _rect = self.surface.get_rect()
    pg.draw.rect(self.surface, 'black', _rect, 1)
    pg.draw.line(self.surface, 'black', _rect.midtop, _rect.midbottom, 1)

  def update(self, zoom_in: bool) -> tuple[bool, bool]:
    self._draw_background()
    # self.buttons[0].update(self.surface, self.mouse_pos)
    open_req = self.buttons[0].update(self.surface, self.mouse_pos) == "open_options"
    new_text = gettext("zoom out") if zoom_in else gettext("zoom in")
    result = self.buttons[1].update(self.surface, self.mouse_pos, new_text=new_text)
    new_zoom = not zoom_in if result == "toggle_zoom" else zoom_in
    return new_zoom, open_req


class FinalPanel(Panel):

  def __init__(self, x, y, width, height):
    super().__init__(x, y, width, height)
    self.ranking = []

  def update(self, ranking: dict, renderer: dict):
    ranking = [(k, *v) for k, v in ranking.items()]
    x, y = 120, 50
    h = 50
    self.surface.fill(BG_COLOR_1)
    for rank, (name, round_n, leg) in enumerate(ranking):
      label = TextLabel((x, y + (h * rank)), f"{rank + 1}. {name:<10} {round_n:3}.{leg}", 25, "royalblue4")
      label.update(self.surface)
      flag = ImageLabel((x + 120, y + (h * rank)), renderer[name].flag, (25, 25))
      flag.update_image(new_size=(24, 16))
      flag.update(self.surface)


class OptionsMenuPanel(Panel):
  """Modales Einstellungs-Menü. Wird über SettingsPanel.buttons[0] geöffnet."""

  ROW_H = 44  # Höhe einer Zeile
  PADDING = 20
  BTN_W = 100
  BTN_H = 36

  def __init__(self):
    n = len(cfg.SETTINGS_OPTIONS)

    w, h = 420, self.PADDING * 2 + n * self.ROW_H + 20 + self.BTN_H + self.PADDING
    x, y = (WIDTH - w) // 2, (HEIGHT - h) // 2

    super().__init__(x, y, w, h)

    self.keys: list[str] = cfg.SETTINGS_OPTIONS
    self.labels: list[str] = [gettext(key) for key in self.keys]

    self.values: dict[str, bool] = {}

    # Toggle-Buttons (True/False)
    self.toggles: dict[str, Button] = {}
    for i, key in enumerate(self.keys):
      cy = self.PADDING + i * self.ROW_H + self.ROW_H // 2
      cx = w - self.PADDING - self.BTN_W // 2
      self.toggles[key] = Button(
        center_pos=(cx, cy),
        text="",
        font_size=18,
        size=(self.BTN_W, 30),
        action=lambda k=key: k  # gibt den Key zurück
      )

    # OK / CANCEL
    mid = w // 2
    btn_y = self.PADDING + n * self.ROW_H + 20 + self.BTN_H // 2
    self.btn_ok = Button(
      (mid + self.BTN_W // 2 + 10, btn_y), gettext("OK"), 20,
      (self.BTN_W, self.BTN_H), action=lambda: "ok"
    )
    self.btn_cancel = Button(
      (mid - self.BTN_W // 2 - 10, btn_y), gettext("CANCEL"), 20,
      (self.BTN_W, self.BTN_H), action=lambda: "cancel"
    )

    self.font_label = pg.font.SysFont("Arial", 18)
    self.font_title = pg.font.SysFont("Arial", 22, bold=True)

  # get current states from config module
  def load(self) -> None:
    self.values = {k: getattr(cfg, k) for k in self.keys}

  # save current states to config module
  def apply(self) -> None:
    for k, v in self.values.items(): setattr(cfg, k, v)

  def _draw_background(self) -> None:
    self.surface.fill(BG_COLOR_1)
    pg.draw.rect(self.surface, "black", self.surface.get_rect(), 2)

    # Titel
    title = self.font_title.render(gettext("OPTIONS"), True, "black")
    self.surface.blit(title, title.get_rect(centerx=self.rect.w // 2, y=6))

  def update(self) -> str | None:
    """
        Zeichnet das Menü und verarbeitet Klicks.
        Gibt "ok", "cancel" oder None zurück.
        """
    self._draw_background()
    mp = self.mouse_pos

    for i, key in enumerate(self.keys):
      cy = self.PADDING + i * self.ROW_H + self.ROW_H // 2

      # Trennlinie
      pg.draw.line(self.surface, "grey70",
                   (self.PADDING, cy + self.ROW_H // 2 - 2),
                   (self.rect.w - self.PADDING, cy + self.ROW_H // 2 - 2))

      # Label
      label_surf = self.font_label.render(self.labels[i], True, "black")
      self.surface.blit(label_surf,
                        label_surf.get_rect(midleft=(self.PADDING, cy)))

      # Toggle-Button Text + Farbe je nach Wert
      val = self.values[key]
      btn = self.toggles[key]
      btn_text = gettext("ON") if val else gettext("OFF")
      btn_color = "green4" if val else "firebrick"
      result = btn.update(self.surface, point=mp,
                          new_text=btn_text, new_color=btn_color)
      if result is not None:  # Klick → Wert umschalten
        self.values[result] = not self.values[result]

    # OK / CANCEL
    if self.btn_ok.update(self.surface, point=mp) == "ok":
      return "ok"
    if self.btn_cancel.update(self.surface, point=mp) == "cancel":
      return "cancel"

    return None


class IntroPanel(Panel):

  def __init__(self, x, y, width, height):
    super().__init__(x, y, width, height)
    self.start_button = Button((width//2, height//4), "Start Regatta", 25, (100,30),
                               action=lambda k="start": k)
    self.quit_button = Button((width//2, height//4*3), "Quit", 25, (100,30),
                              action=lambda k="quit": k)

  def update(self) -> None | str:
    self.surface.fill(BG_COLOR_1)
    if self.start_button.update(self.surface, point=pg.mouse.get_pos()) == "start":
      return "start"
    elif self.quit_button.update(self.surface, point=pg.mouse.get_pos()) == "quit":
      return "quit"
    return None





if __name__ == '__main__':
  pass

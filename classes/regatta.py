import random

from collections import deque
import pygame as pg
import numpy as np

from classes.environment import Wind, Race, Cloud
from classes.panels import MapPanel, InfoPanel, HUDPanel, SkipperPanel, SettingsPanel, FinalPanel, SettingsMenuPanel
from classes.boat import Boat, BoatRenderer
from classes.agent import BoatAgent
from aux.widgets import Ticker

from config import *
from data.constants import *
from data.map_data import MAP_DATA
from aux.utils import rc2xy, gettext

SOUND_FINISHED = pg.USEREVENT + 1


class Regatta:
  def __init__(self, skippers: list, map_name: str):

    self.skippers: list = skippers
    self.map: dict = MAP_DATA[map_name]
    self.has_bots: bool = any(b.endswith("bot") for b in skippers)
    self.zoom_in: bool = False
    self.current_leg = None
    self.active_idx = None
    self.game_over = None
    self.blanket_turn = None
    self.blanket_leg = None
    self.can_roll = None
    self.active_boat = None
    self.legs_in_turn = None

    self._init_pygame(map_name)
    self._init_environment(map_name)
    self._init_boats()
    self._init_agents(map_name)
    self._init_game()
    self._init_panels()
    self._init_ticker(map_name)

  def _init_ticker(self, map_name: str):
    ticker_font = pg.font.SysFont("Arial", 24)
    ticker_rect = pg.Rect(0, 960, 500, 40)
    self.game_ticker = Ticker(ticker_rect, ticker_font,
                              initial_text=f"Welcome to the Regatta at {map_name}! Waiting for race start...",
                              speed=5.0)

  def _init_panels(self):
    self.info_panel: InfoPanel = InfoPanel(*PANEL_DATA["INFO"], boats=self.boats, renderer=self.renderer)
    self.hud_panel: HUDPanel = HUDPanel(*PANEL_DATA["HUD"])
    self.skipper_panel: SkipperPanel = SkipperPanel(*PANEL_DATA["SKIPPER"])
    self.settings_panel: SettingsPanel = SettingsPanel(*PANEL_DATA["SETTINGS"])
    self.panels: list = [
      self.map_panel,
      self.info_panel,
      self.hud_panel,
      self.skipper_panel,
      self.settings_panel
    ]
    self.final_panel: FinalPanel = FinalPanel(100, 100, 300, len(self.boats) * 50 + 50)
    self.settings_menu = SettingsMenuPanel()
    self.settings_menu_open: bool = False

  def _init_game(self):
    self.blocked_fix |= self.map_panel.blocked_positions
    self.blanket_turn: set = set()
    self.blanket_leg: set = set()
    self.active_idx: int = 0
    self.active_boat: Boat = self.boats[self.active_idx]
    self.ranking: dict = dict()
    self.round_n: int = self.map["countdown"]
    self.legs_in_turn: int = 0
    self.current_leg: int = 0
    self.can_roll: bool = True
    self.game_over: bool = False

  def _init_agents(self, map_name: str):
    self.dist_maps: list | None = None
    if self.has_bots:
      num_lines = len(self.race.track_lines)
      track_lines = list(range(num_lines))

      # Map each trackline index to its corresponding mark index
      # e.g., Line 0,1 -> Mark 0. Line 2,3 -> Mark 1.
      marks = [(i // 2) % len(self.map["marks"]) for i in range(num_lines)]

      self.dist_maps = [self.get_distance_map(t, m) for t, m in zip(track_lines, marks)]

    self.agents: dict = {
      boat.name: BoatAgent(boat, boat.skipper, map_name=map_name, distance_maps=self.dist_maps) for boat in self.boats
      if
      boat.skipper.endswith("bot")
    }

  def _init_boats(self):
    self.boats = deque(
      [Boat(skipper=sk, idx=i, position=position, wwd_idx=self.wind.wwd_idx, track_lines=self.race.track_lines)
       for sk, i, position, size in self.get_boat_data()]
    )
    self.renderer: dict = {
      boat.name: BoatRenderer(cell_size=self.cell_size, idx=i) for i, boat in enumerate(self.boats)
    }

  def _init_environment(self, map_name: str):

    self.cell_size: int = self.map["cell_size"]
    self.map_panel: MapPanel = MapPanel(*PANEL_DATA["MAP"], map_name=map_name)

    self.wind = Wind(map_name=map_name)
    self.race = Race(map_name=map_name)
    self.blocked_fix: set = {self.race.position} | {m.position for m in self.race.marks}
    self.sfx_start_gun = pg.mixer.Sound("assets/start_gun.wav")
    self.sfx_start_gun.set_volume(1.0)
    self.sfx_finish_horn = pg.mixer.Sound("assets/finish_horn.wav")
    self.sfx_finish_horn.set_volume(0.7)

  def _init_pygame(self, map_name: str):
    pg.init()
    pg.mixer.init()
    self.window = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption(f'R E G A T T A   AT   {map_name.upper()}')
    self.clock = pg.time.Clock()
    self.fps = 10 if "human" in self.skippers else FPS

  def get_distance_map(self, t_idx: int, m_idx: int) -> np.ndarray:

    _, first_direction, second_direction = self.map["marks"][m_idx]
    rows, cols = self.map["size"]

    blocks = []
    for s in ["islands", "dock", "edges"]:
      blocks.extend(self.map[s])
    blocks.append(self.map["race"])
    blocks.append(self.map["windbag"])
    blocks += [m[0] for m in self.map["marks"]]
    blocks = set(blocks)

    # --- CHECK-VALVE LOGIC ---
    # If aiming for an Entry line (even index), block the Exit line (t_idx + 1)
    # If aiming for an Exit line (odd index), block the Entry line (t_idx - 1)
    # This forces the BFS map to flow AROUND the buoy, not through the back door
    if t_idx % 2 == 0 and t_idx + 1 < len(self.race.track_lines):
      exit_from, exit_to = self.race.track_lines[t_idx + 1]
      blocks.update(exit_from)
      blocks.update(exit_to)
    elif t_idx % 2 == 1:
      entry_from, entry_to = self.race.track_lines[t_idx - 1]
      blocks.update(entry_from)
      blocks.update(entry_to)

    # # block positions downstream of second line, to avoid getting stuck
    # # for reverse_finish need to consider different block
    # block_direction = (second_direction - 2) % 8
    # if self.map["reverse_finish"] and t_idx == len(self.race.track_lines) - 1:
    #   block_direction = (second_direction + 2) % 8
    # dr, dc = DIRECTIONS[block_direction]
    #
    # # copy second_to_line x-times in second_line crossing direction to blocks
    # for i in range(3):
    #   for sr, sc in self.race.track_lines[t_idx][1]:
    #     r = sr + i * dr
    #     c = sc + i * dc
    #     blocks.add((r, c))

    # Initialize map with a very high cost (infinity)
    dist_map: list = [[float('inf')] * cols for _ in range(rows)]

    # Queue for BFS: (c, r, current_distance)
    queue = deque()

    # --- DYNAMIC BFS START ---
    # Start the heat map exactly on the 'to_line' we are currently aiming for
    target_to_line = self.race.track_lines[t_idx][1]
    for r, c in target_to_line:
      queue.append((r, c, 0))
      dist_map[r][c] = 0

    # # init 3 positions on first_to_line closest to mark with 0

    # fdr, fdc = DIRECTIONS[first_direction]
    # for i in range(1,4):
    #   r, c = tr+i*fdr, tc+i*fdc
    #   queue.append((r, c, 0))
    #   dist_map[r][c] = 0

    while queue:
      r, c, d = queue.popleft()

      for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc

        # Check bounds and if it's not blocked
        if 0 <= nc < cols and 0 <= nr < rows:
          if (nr, nc) not in blocks and dist_map[nr][nc] == float('inf'):
            dist_map[nr][nc] = d + 1
            queue.append((nr, nc, d + 1))

    return np.array(dist_map)

  @property
  def validation_parameters(self):
    others = [b for b in self.boats if b != self.active_boat]
    return self.blocked_fix | set(b.position for b in others), self.round_n, set(self.race.start_line), others

  def get_boat_data(self) -> list:  # skipper, color_idx, (row, col), size for scaling
    docks = self.map["dock"]
    dr, dc = DIRECTIONS[self.map["dock offset"]]
    return [(skipper, i, (r + dr, c + dc), self.cell_size) for i, (skipper, (r, c)) in
            enumerate(zip(self.skippers, docks))]

  def process_die(self) -> None:
    die = random.choice(DIE_SIDES)
    if die in ('CCW', 'CW', " "):
      self.change_wind(die)
    else:
      self.start_round(die)

  def change_wind(self, die: str):
    if KEEP_MAIN_WIND_DIRECTION and die in ("CW", "CCW"):
      if (die == "CW" and (self.wind.wwd_idx - 1) % 8 == self.map["windward_index"]) or \
        (die == "CCW" and (self.wind.wwd_idx + 1) % 8 == self.map["windward_index"]):
        die = " "
    self.wind.rotate(die)
    self.legs_in_turn = 0
    self.boats.rotate(-1)
    self.active_boat = self.boats[0]

  def start_round(self, die: int):
    self.legs_in_turn = die
    self.can_roll = False
    self.update_boats()  # evaluate blanketing at beginning of round for all boats
    self.update_initial_states()

  def update_boats(self):
    # collect all blanketing first
    self.blanket_turn = self.blanket_leg = set()
    for boat in self.boats:
      boat.update_course(self.wind)
      self.blanket_turn.add(boat.blanket_turn)
      self.blanket_leg.add(boat.blanket_leg)

    for boat in self.boats:
      boat.update_blanketing(self.blanket_turn, self.blanket_leg)
      boat.update_legs(self.legs_in_turn)

  def update_initial_states(self):
    for boat in self.boats:
      boat.initial_state = boat.state

  def get_selection(self) -> str | None:
    if self.can_roll:
      selection = self.skipper_panel.update({"roll"})
    else:
      selection = self.skipper_panel.update(self.active_boat.possible_options(*self.validation_parameters))
    return selection

  def update_panels(self) -> None:
    self.map_panel.update(self.boats, self.active_idx, self.wind,
                          self.legs_in_turn, self.race, self.renderer,
                          zoom_in=self.zoom_in,
                          dist_maps=self.dist_maps
                          )
    self.info_panel.update(self.round_n, self.legs_in_turn, list(self.boats), self.active_idx, self.renderer)
    self.hud_panel.update(self.active_boat)
    self.zoom_in, open_req = self.settings_panel.update(self.zoom_in)
    if open_req:
      self.settings_menu.load()
      self.settings_menu_open = True

  def blit_panels(self) -> None:
    for panel in self.panels: self.window.blit(panel.surface, panel.rect.topleft)

  def blit_final_panel(self) -> None:
    self.window.blit(self.final_panel.surface, self.final_panel.rect.topleft)

  def run(self) -> None:
    paused = False
    all_humans_home: int = 0
    race_started = False
    first_at_mark = 0
    selection_sequence: list = []
    while True:
      for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE): quit()
        if event.type == pg.KEYDOWN and event.key == pg.K_p:
          paused = not paused
        if event.type == SOUND_FINISHED and not any(b.finished for b in self.boats) and SHOW_CLOUDS:
          x, y = rc2xy(self.map["race"], self.cell_size)
          sprite = self.wind.clouds[0].sprite
          self.wind.clouds.append(Cloud(x, y, sprite, 2))

      if self.round_n == 0 and not race_started:
        race_started = True
        self.game_ticker.add_text(gettext("start_gun_fired") + " --- Good luck Skippers!", 1)

      # if self.game_over:
      #   self.blit_final_panel()
      #   pg.display.flip()
      #   self.clock.tick(self.fps)
      #   continue

      if paused:
        continue

      if not self.game_over and len(self.boats) == len(self.ranking):
        self.final_panel.update(self.ranking, self.renderer)
        self.game_over = True

      if not selection_sequence:
        if self.can_roll:
          selection_sequence = ["roll"]
          if self.active_boat.skipper == "human" and not AUTO_DICE:
            selection_sequence = [self.get_selection()]

        elif self.active_boat.skipper == "human":
          if all_humans_home == self.skippers.count("human"):
            selection_sequence = ["forfeit"]
          else:
            selection_sequence = [self.get_selection()]

        else:  # self.active_boat.skipper != "human":
          selection_sequence = self.agents[self.active_boat.name].selection(*self.validation_parameters)

      selection = selection_sequence.pop(0)

      if selection == "roll":
        self.process_die()
      elif selection is not None:
        self.active_boat.do_action(selection)

      # shout-out for first boat at mark
      for boat in self.boats:
        if boat.finished: continue
        if boat.next_track_idx >= first_at_mark*2 + 1:
          if first_at_mark:
            message = f"{boat.name} {gettext("first at Mark")} {gettext("mark")} {first_at_mark}"
          else:
            message = f"{boat.name} {gettext("first at Mark")} {gettext("start")}"
          self.game_ticker.add_text(message,1)
          first_at_mark += 1
          break

      if selection in ("sail", "tack", "luff", "port", "star", "unspin"):
        self.current_leg += 1

      # check for finishing of active boat
      if self.active_boat.name not in self.ranking and self.active_boat.finished:
        message: str = f"{self.active_boat.name} {gettext("finishes in")} " \
                       f"{gettext("round")} {self.round_n}.{self.current_leg}"
        self.game_ticker.add_text(message,1)
        self.ranking[self.active_boat.name] = (self.round_n, self.current_leg)
        all_humans_home += self.active_boat.skipper == "human"
        self.sfx_finish_horn.play(maxtime=800)

      # finalize or forfeit turn
      if selection in ("forfeit", "finalize"):
        # when last skipper -> round + 1, start next round with process_die
        if self.active_idx == len(self.boats) - 1:
          self.round_n += 1
          if self.round_n == 0:
            channel = self.sfx_start_gun.play()
            if channel:
              channel.set_endevent(SOUND_FINISHED)

          self.can_roll = True
        # next skipper
        self.active_idx = (self.active_idx + 1) % len(self.boats)
        self.current_leg = 0
        self.active_boat = self.boats[self.active_idx]
        # blanketing at end of turn does not affect boats in the same round

      self.update_panels()

      self.blit_panels()

      # ── SETTINGS-MENÜ (modal, Spiel pausiert) ──────────────────────────
      if self.settings_menu_open:
        result = self.settings_menu.update()
        self.window.blit(self.settings_menu.surface,
                         self.settings_menu.rect.topleft)
        if result == "ok":
          self.settings_menu.apply()
          self.settings_menu_open = False
          # FPS ggf. neu setzen, falls AUTO_DICE/Bots-Status sich ändert
          # self.fps = 10 if "human" in self.skippers else FPS
        elif result == "cancel":
          self.settings_menu_open = False

      if SHOW_TICKER:
        self.game_ticker.update()
        self.game_ticker.draw(self.window)

      if self.game_over:
        self.blit_final_panel()
        # pg.display.flip()
        # self.clock.tick(self.fps)

      pg.display.update()

      self.clock.tick(self.fps)


if __name__ == '__main__':
    pass

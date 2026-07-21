import itertools
import pygame as pg

from classes.environment import Wind

from config import *
from data.constants import *
from aux.utils import rc2xy, get_boat_spritesheet, get_flag

pg.init()


class Boat:

  OPTIONS: dict = {}

  def __init__(self, skipper: str, idx: int, position: tuple, wwd_idx: int, track_lines: list | None = None):
    self.skipper: str = skipper
    self.color: str = BOAT_COLORS[idx]
    self.text_color: str = TEXT_COLORS[idx]
    self.name: str = BOAT_NAMES[idx]
    self.position: tuple = position  # row, col
    self.after_race_position: tuple = self.position
    self.heading: int = wwd_idx  # windward_idx : init in luffing
    self.track_lines: list = [] if track_lines is None else track_lines

    self.legs: int = 0
    self.puffs: int = 2

    self.course: int = 0  # init in luffing
    self.starboard_tack: bool = True  # False: port tack (starboard is in lee), True: starboard tack (port is in lee)
    self.spinnaker: bool = False
    self.spinnaker_down_in_turn: bool = False
    self.puff_active: bool = False
    self.puff_in_turn: bool = False

    self.blanketed: bool = False  # -> lose turn
    self.spinnaker_blanketed: bool = False  # -> lose 1 leg

    self.path: list = [self.position]
    self.action_sequence: list = []
    self.next_track_idx: int = 0  # index of track_lines to cross
    self.start_idx: int = 0  # idx of path when statline was crossed (to distinguish start and finish)

    self.show_laylines: bool = False
    self.initial_state: dict = self.state

  # # # # PROPERTIES

  @property
  def state(self) -> dict:
    # state includes only modified attributes, defined by not in STATE_EXCLUSIONS
    return {k: v for k, v in self.__dict__.items() if k not in STATE_EXCLUSIONS}

  def copy_state(self) -> dict:
      state = {k: v for k, v in self.state.items()}
      state["path"] = list(self.path)
      state["action_sequence"] = list(self.action_sequence)  # ← fehlt aktuell
      return state

  def restore_state(self, state: dict) -> None:
      for k, v in state.items(): setattr(self, k, v)

  @property
  def next_positions(self) -> list:
    r, c = self.position
    dr, dc = DIRECTIONS[self.heading]
    return [(r + (i + 1) * dr, c + (i + 1) * dc) for i in range(self.spaces)]

  @property
  def spaces(self) -> int:
    if self.spinnaker_priority or self.shift_priority or self.legs == 0: return 0
    return SPACES[self.course] + self.spinnaker + self.puff_active

  @property
  def initial_position(self) -> tuple:
    return self.initial_state["position"]

  @property
  def wwd_idx(self):
    return (self.heading - self.course) % 8

  @property
  def blanket_turn(self) -> tuple:
    r, c = self.position
    dr, dc = DIRECTIONS[(self.wwd_idx + 4) % 8]
    return r + dr, c + dc

  @property
  def blanket_leg(self) -> tuple:
    if not self.spinnaker: return tuple()
    r, c = self.position
    dr, dc = DIRECTIONS[(self.wwd_idx + 4) % 8]
    return r + 2 * dr, c + 2 * dc

  @property
  def shift_priority(self) -> bool:
    # must shift tack according to course
    return (self.starboard_tack and self.course in (1, 2, 3)) or (not self.starboard_tack and self.course in (7, 6, 5))

  @property
  def spinnaker_priority(self) -> bool:
    # must take down spinnaker or go to leeward
    return self.spinnaker and self.course not in (3, 4, 5)

  @property
  def finished(self):
    return self.next_track_idx >= len(self.track_lines)-1  # no need for second line of finish mark

  # # # # UPDATES

  @staticmethod
  def has_crossed_trackline(path: list[tuple], trackline: tuple[list, list]) -> bool:
    if len(path) < 2: return False
    from_line, to_line = trackline
    # check if any of first is directly followed by any of second
    for p1, p2 in itertools.pairwise(path):
      if p1 in from_line and p2 in to_line:
        return True
    return False

  def update_legs(self, legs: int) -> None:
    self.legs = 0 if self.blanketed else legs - self.spinnaker_blanketed
    self.initial_state["legs"] = self.legs

  def update_course(self, compass: Wind) -> None:
    self.course = compass.rose[self.heading]

  def update_blanketing(self, blanketed: set, spinnaker_blanketed: set) -> None:
    self.blanketed = self.position in blanketed
    self.spinnaker_blanketed = self.position in spinnaker_blanketed

  # # # # OPTIONS

  def can_sail(self, blocked_positions: set, round_n: int, start_line: set, other_boats: list) -> bool:
    path = [self.position] + self.next_positions
    path_set = set(path)
    next_set = set(self.next_positions)

    # avoid sailing into blocked position
    if next_set & blocked_positions:
      return False

    # avoid premature start
    if round_n < 0 and next_set & start_line:
      return False

    # avoid sailing any trackline the wrong way
    # need to include current position (path, path_set)
    if len(path) >= 2 and self.next_track_idx > 0:
      # look only for next 2 tracklines
      for from_line, to_line in self.track_lines[self.next_track_idx-1:self.next_track_idx + 2]:
        if not (path_set & from_line or path_set & to_line): continue
        # check if any of to_line is directly followed by any of from_line -> wrong direction
        for p1, p2 in itertools.pairwise(path):
          if p1 in to_line and p2 in from_line:
            return False

    if not ADVANCED_RULES: return True

    # # # # Advanced rules
    # A port-tack boat shall keep clear of a starboard-tack boat.
    if not self.starboard_tack and \
       any(other.starboard_tack and next_set & set(other.next_positions) for other in other_boats):
      # print("lee has right of way")
      return False

    # A windward boat shall keep clear of a leeward boat
    WIND = pg.Vector2(DIRECTIONS[(self.wwd_idx+4) % 8])  # vector to leeward
    SELF = pg.Vector2(self.position)
    STARBOARD = pg.Vector2(DIRECTIONS[(self.heading + 2) % 8])
    for other in other_boats:
      if not next_set.intersection(other.next_positions): continue
      OTHER = pg.Vector2(other.position)
      DELTA = OTHER - SELF  # vector from SELF to OTHER
      dot_product = WIND.dot(DELTA)   # if >0: OTHER is leeward, if <0: OTHER is windward if ==0: look for tack
      if dot_product > 0:
        # print("lee has right of way 1")
        return False
      elif dot_product == 0 and self.starboard_tack:  # other is also starboard_tack see above and on same windward line
        dot_product = STARBOARD.dot(DELTA)  # if >0: OTHER on star (--> windward) if <0: OTHER on port (--> leeward)
        if dot_product < 0:
          # print("lee has right of way 2")
          return False
      elif dot_product == 0 and not self.starboard_tack:
        dot_product = STARBOARD.dot(DELTA)  # if >0: OTHER on star (--> leeward) if <0: OTHER on port (--> windward)
        if dot_product > 0:
          # print("lee has right of way 3")
          return False

    return True

  def possible_options(self, blocked_positions: set, round_n: int, start_line: set, other_boats: list) -> set:
    possibles = set()
    can_sail: bool = self.can_sail(blocked_positions, round_n, start_line, other_boats)

    # sail leg 1
    if (self.legs > 0) and can_sail and self.spaces and self.course and \
       not self.shift_priority and not self.spinnaker_priority:
      possibles.add("sail")

    # leeward 2
    if self.course not in (0, 4) and not self.shift_priority:
      possibles.add("leeward")

    # windward 3
    if self.course not in (7, 0, 1) and not self.shift_priority and \
       not self.spinnaker_priority and not (self.spinnaker and self.course in (3, 5)):
      possibles.add("windward")

    # shift tack 4
    if self.legs > 0 and (self.course in (7, 1, 4) or self.shift_priority):
      possibles.add("tack")

    # luffing 5
    if self.legs > 0 and self.course in (7, 1) and not self.shift_priority and not self.spinnaker_priority:
      possibles.add("luff")

    # beat port / beat starboard 6 7
    if self.legs > 0 and self.course == 0:
      possibles.add("port")
      possibles.add("star")

    # spinnaker up 8
    if not self.spinnaker and self.course in (3, 4, 5):
      possibles.add("spin")

    # spinnaker down 9
    if self.legs > 0 and self.spinnaker and not self.spinnaker_down_in_turn:
      possibles.add("unspin")

    # activate puff 10
    if self.legs > 0 and self.spaces and self.puffs and not self.puff_active and \
       not self.shift_priority and not self.spinnaker_priority and not self.puff_in_turn:
      possibles.add("puff")

    # deactivate puff 11
    if self.puff_active:
      possibles.add("unpuff")

    # laylines, reset, forfeit are always possible 12 13 14
    possibles |= {"lines", "reset", "forfeit"}

    # finalize 15
    if self.legs == 0:
      possibles.add("finalize")

    return possibles

  # # # # ACTIONS

  def do_action(self, option: str | None):
    self.action_sequence.append(option)
    return self.OPTIONS[option](self)

  # 1
  def sail_leg(self) -> None:
    self.path += self.next_positions
    path = self.path

    self.position = self.path[-1]

    if not self.finished:
      if self.has_crossed_trackline(path[self.start_idx:], self.track_lines[self.next_track_idx]):
        # print(f"{self.name} has reached checkpoint {self.next_track_idx}")
        self.next_track_idx += 1
      
      if not self.start_idx and self.next_track_idx == 2:  # crossed startline, ignore from now startline
        self.start_idx = len(path)
        # print(f"{self.color} starts at {self.start_idx}")

      # check if a second checkpoint crossed in the same leg
      if self.next_track_idx < len(self.track_lines)-1:
        if self.has_crossed_trackline(path[self.start_idx:], self.track_lines[self.next_track_idx]):
          # print(f"{self.name} has reached checkpoint {self.next_track_idx} in same leg")
          self.next_track_idx += 1
        # self.checkpoints += self.has_crossed_trackline(path, self.track_lines[self.checkpoints])

    if self.puff_active:
      self.puff_in_turn = True
      self.puff_active = False

    self.legs -= 1

  # 2
  def rotate_leeward(self) -> None:
    # beat->beam->broad->running
    h, c = self.heading, self.course
    d = -1 if self.starboard_tack else 1
    self.heading, self.course = (h + d) % 8, (c + d) % 8

  # 3
  def rotate_windward(self) -> None:
    # beat<-beam<-broad<-running
    h, c = self.heading, self.course
    d = 1 if self.starboard_tack else -1
    self.heading, self.course = (h + d) % 8, (c + d) % 8

  # 4
  def shift_tack(self) -> None:
    # Heading move
    if self.course in (1, 7) and not self.shift_priority:
      self.rotate_windward()  # luffing
      self.rotate_windward()  # opposite beating
    self.starboard_tack = not self.starboard_tack
    self.legs -= 1

  # 5
  def to_luffing(self) -> None:
    wwd_idx = self.wwd_idx
    self.course = 0
    self.heading = wwd_idx
    self.legs -= 1

  # 6
  def to_beat_port(self) -> None:
    self.course = 1
    self.heading = (self.heading + 1) % 8
    self.starboard_tack = False
    self.legs -= 1

  # 7
  def to_beat_star(self) -> None:
    self.course = 7
    self.heading = (self.heading - 1) % 8
    self.starboard_tack = True
    self.legs -= 1

  # 8
  def spinnaker_up(self) -> None:
    if self.course in (3, 4, 5): self.spinnaker = True

  # 9
  def spinnaker_down(self) -> None:
    self.spinnaker = False
    self.spinnaker_down_in_turn = True
    self.legs -= 1

  # 10
  def activate_puff(self) -> None:
    self.puff_active = True
    self.puffs -= 1

  # 11
  def deactivate_puff(self) -> None:
    self.puff_active = False
    self.puffs += 1

  # 12
  def toggle_laylines(self) -> None:
    self.show_laylines = not self.show_laylines

  # 13
  def reset_turn(self, state: dict | None = None) -> None:
    if state is None:
      state = self.initial_state
      state["action_sequence"] = []
    for k, v in state.items():
      setattr(self,k, v)

  # 14
  def forfeit_turn(self) -> None:
    self.reset_turn()
    self.legs = 0

  # 15
  def finalize_turn(self) -> None:
    self.puff_in_turn = False
    self.spinnaker_down_in_turn = False
    self.show_laylines = False
    self.action_sequence = []


Boat.OPTIONS = {
      "sail": Boat.sail_leg,
      "leeward": Boat.rotate_leeward,
      "windward": Boat.rotate_windward,
      "tack": Boat.shift_tack,
      "luff": Boat.to_luffing,
      "port": Boat.to_beat_port,
      "star": Boat.to_beat_star,
      "spin": Boat.spinnaker_up,
      "unspin": Boat.spinnaker_down,
      "puff": Boat.activate_puff,
      "unpuff": Boat.deactivate_puff,
      "lines": Boat.toggle_laylines,
      "reset": Boat.reset_turn,
      "forfeit": Boat.forfeit_turn,
      "finalize": Boat.finalize_turn
    }


class BoatRenderer:

  def __init__(self, cell_size: int, idx: int):
    self.cell_size: int = cell_size
    self.color: str = BOAT_COLORS[idx]
    self.spritesheet = get_boat_spritesheet((cell_size, cell_size), self.color, 4, 8, 0)
    self.sprite = pg.Surface((self.cell_size, self.cell_size), pg.SRCALPHA)
    self.flag = get_flag(BOAT_NAMES[idx])

  def draw(self, surface: pg.Surface, boat: Boat, show_path: bool = False, show_flag: bool = False) -> None:
    sr, sc = (boat.starboard_tack + 2 * boat.spinnaker) * self.cell_size, self.cell_size * boat.heading
    self.sprite.fill(pg.SRCALPHA)
    self.sprite.blit(self.spritesheet, (-sc, -sr))
    r, c = boat.position
    surface.blit(self.sprite, (c * self.cell_size, r * self.cell_size))
    pg.draw.circle(surface, "grey50", rc2xy(boat.blanket_turn, self.cell_size), self.cell_size // 4, 2)

    if boat.spaces:

      for pos in boat.next_positions:
        pg.draw.circle(surface, self.color, rc2xy(pos, self.cell_size), self.cell_size // 5, 2)

    if boat.spinnaker:
      pg.draw.circle(surface, "grey50", rc2xy(boat.blanket_leg, self.cell_size), self.cell_size // 5, 2)

    if show_path and len(boat.path) >= 2:

      pg.draw.lines(surface, self.color, False, [rc2xy(pos, self.cell_size) for pos in boat.path[::-1]], 1)

    if show_flag:
      surface.blit(pg.transform.scale(self.flag, (12, 8)), ((c + 0.8) * self.cell_size, r * self.cell_size))
      pg.draw.line(surface, "black", ((c + 0.5) * self.cell_size, (r + 0.5) * self.cell_size),
                   ((c + 0.8) * self.cell_size, r * self.cell_size + 8), 1)

    if boat.show_laylines:
      x, y = rc2xy(boat.position, self.cell_size)
      sdx, sdy = rc2xy(DIRECTIONS[(boat.wwd_idx + 1) % 8], self.cell_size, offset=False)
      pdx, pdy = rc2xy(DIRECTIONS[(boat.wwd_idx - 1) % 8], self.cell_size, offset=False)
      hdx, hdy = rc2xy(DIRECTIONS[boat.heading], self.cell_size, offset=False)
      pg.draw.line(surface, "green", (x, y), (x + sdx * 10, y + sdy * 10), 2)
      pg.draw.line(surface, "red", (x, y), (x + pdx * 10, y + pdy * 10), 2)
      pg.draw.line(surface, BG_COLOR_1, (x, y), (x + hdx * 10, y + hdy * 10), 2)


if __name__ == '__main__':
  pass

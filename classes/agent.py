from classes.boat import Boat

from data.map_data import MAP_DATA


class BoatAgent:

  def __init__(self, boat: Boat, bot_type: str, map_name: str, distance_maps: list | None):
    self.boat: Boat = boat
    self.last_positions: dict = dict()
    self.stuck_rounds: int = 3
    SELECTIONS: dict = {
      "simplebot": self.simple_selection,
      "smartbot": self.smart_selection}
    self.selection: object = SELECTIONS[bot_type]
    self.at_final_position: bool = False
    self.map: dict = MAP_DATA[map_name]
    self.distance_maps: list | None = distance_maps

  @property
  def is_stuck(self) -> bool:
    last_round = max(self.last_positions)
    last_position = self.last_positions[last_round]
    for r in range(last_round, last_round - self.stuck_rounds, -1):
      if self.last_positions.get(r, (None, None)) != last_position: return False
    return True

  @staticmethod
  def get_best_heading(pos1: tuple, pos2: tuple) -> int:
    r1, c1 = pos1
    r2, c2 = pos2
    dr, dc = (r2 - r1), (c2 - c1)
    if dr <= 0 and dr / 2 <= dc <= -dr / 2: return 0
    if dc > 0 and -dc / 2 <= dr <= dc / 2: return 2
    if dr > 0 and -dr / 2 <= dc <= dr / 2: return 4
    if dc <= 0 and dc / 2 <= dr <= -dc / 2: return 6
    if dr < 0 < dc: return 1
    if 0 < dr and 0 < dc: return 3
    if dc < 0 < dr: return 5
    if dr < 0 and dc < 0: return 7
    print(pos1, pos2, dr, dc)
    raise ValueError("no best heading found")

  @staticmethod
  def get_distance(pos1: tuple, pos2: tuple, manhattan_method: bool = True) -> float:
    (r1, c1), (r2, c2) = pos1, pos2
    return abs(r2 - r1) + abs(c2 - c1) if manhattan_method else ((r2 - r1) ** 2 + (c2 - c1) ** 2) ** 0.5

  @staticmethod
  def get_seen_state(boat) -> tuple:
    return (
      boat.position,
      boat.heading,
      boat.course,
      int(boat.starboard_tack),
      int(boat.spinnaker),
      boat.puffs,
      int(boat.puff_active),
      int(boat.puff_in_turn),
      boat.legs
    )

  @staticmethod
  def avoid_reversals(last: str, options: set) -> set:
    if last in ("tack", "port", "star"): return options - {"tack"}  # no double tacking
    if last == "leeward": return options - {"windward"}  # no windward after leeward
    if last == "windward": return options - {"leeward"}  # no leeward after windward
    if last == "unpuff": return options - {"puff"}  # no activation after puff deactivation
    if last == "puff": return options - {"unpuff"}  # no deactivation after puff activation
    return options

  @staticmethod
  def simple_selection(*args) -> list[str]:
    return ["forfeit"]

    # # returns a selection_sequence with only one (quite reasonable or random) option
    #
    # if self.at_final_position: return ["forfeit"]
    # if self.boat.finished: self.check_final_position()
    #
    # self.last_positions[round_n] = self.boat.position
    #
    # to_line, targets = self.get_targets()  # targets include next from_line and to_line
    #
    # options: set = set(self.boat.possible_options(blocked_positions, round_n, startline, other_boats))
    #
    # options -= {"luff", "lines", "reset", "forfeit"}  # do not use luffing ,laylines, reset, forfeit by random
    #
    # if self.boat.action_sequence:
    #   options = self.avoid_reversals(self.boat.action_sequence, options)
    #
    # if self.boat.legs == 0 and "finalize" in options:
    #   # print(f"finalized turn {self.sequence}")
    #   return ["finalize"]  # finalize
    #
    # if "sail" in options:  # and self.boat.next_positions:
    #
    #   if set(targets) & set(self.boat.next_positions):
    #     # self.total_options += 1
    #     return ["sail"]
    #
    #   # keep course if it is the best
    #   for target in targets:
    #     if self.boat.heading == self.get_best_heading(self.boat.position, target):
    #       # print("sailed best course")
    #       # self.total_options += 1
    #       return ["sail"]
    #
    #   if to_line:
    #     dist = min([self.get_distance(self.boat.position, pos) for pos in to_line])
    #     next_dist = min([self.get_distance(self.boat.next_positions[-1], pos) for pos in to_line])
    #     if next_dist < dist:
    #       # print("reduced distance")
    #       # self.total_options += 1
    #       return ["sail"]  # sail leg only if towards next to_line track line
    #
    # # if any(s in options for s in ("lines", "reset", "forfeit", "finalize")):
    # #   print("exclusion needed")
    # if "sail" in options and not self.is_stuck:
    #   options -= {"sail"}
    #
    # if not options:
    #   # print(f"{self.at_place=}")
    #   # print("no options")
    #   return ["forfeit"]  # forfeit if no other option
    # option = random.choice(list(options))
    # # self.total_options += 1
    # # self.random_options += 1
    # # print(f"randomly choose {option}")
    # return [option]

  def smart_selection(self, blocked_positions, round_n, startline, other_boats) -> list[str]:

    if self.at_final_position: return ["forfeit"]
    if self.boat.finished: self.check_final_position()

    self.last_positions[round_n] = self.boat.position

    targets: set = self.get_targets()  # targets include next from_line and to_line

    seen = set()
    saved = self.boat.copy_state()

    best_sequence, _, _ = self._find_best_sequence(targets, blocked_positions, round_n, startline,
                                                   other_boats, seen, sequence=[])
    self.boat.restore_state(saved)

    return best_sequence + ["finalize"] if best_sequence else ["forfeit"]

  def _find_best_sequence(self, targets: set, blocked_positions: set, round_n: int, startline: set,
                          other_boats: list, seen: set, sequence: list) -> tuple:
    """recursive dfs over all options. returns (sequence, final_pos, score)"""

    # terminate recursion
    if self.boat.legs == 0:
      score = self.get_score(self.boat, self.boat.position, targets)
      return sequence, self.boat.position, score

    # find and minimize next neighbors
    options: set = set(self.boat.possible_options(blocked_positions, round_n, startline, other_boats))
    # do not use luffing, Spinnaker or Puff for now
    options -= {"luff", "lines", "reset", "forfeit"}

    if self.boat.action_sequence:
      options = self.avoid_reversals(self.boat.action_sequence[-1], options)
      # if self.boat.position == (8,23) and "sail" not in options:
      #   print("sail not an option")

    best_sequence, best_final_pos, best_score = [], self.boat.position, 0
    last_state: dict = {k: v for k, v in self.boat.state.items()}

    for option in options:

      self.boat.do_action(option)

      seen_state = self.get_seen_state(self.boat)
      if seen_state in seen:
        # print(f"state {seen_state} seen")
        self.boat.reset_turn(last_state)
        continue
      seen.add(seen_state)

      new_sequence, final_pos, score = self._find_best_sequence(
        targets, blocked_positions, round_n, startline, other_boats, seen, sequence + [option])

      if score > best_score:
        best_sequence, best_final_pos, best_score = new_sequence, final_pos, score

      self.boat.restore_state(last_state)

    return best_sequence, best_final_pos, best_score

  def get_score(self, boat: Boat, pos: tuple, targets: set) -> int:
    r, c = pos
    score = 50 + 1000 * boat.next_track_idx
    score -= 2 - boat.puffs  # disadvantage of fewer puffs
    score += boat.legs * 2  # advantage if more legs
    if pos in targets or self.boat.finished:
      score -= min(self.get_distance(pos, t) for t in targets)  #
    elif self.distance_maps:
      # Protect against index out of bounds at the finish line
      safe_idx = min(boat.next_track_idx, len(self.distance_maps) - 1)
      score -= self.distance_maps[safe_idx][r,c]

    return score

  def check_final_position(self) -> None:
    self.at_final_position = self.get_distance(self.boat.position, self.boat.after_race_position) < 3

  def get_targets(self) -> set:
    # return to_line and attractive targets
    if self.boat.finished: return {self.boat.after_race_position}
    else:
      from_line, to_line = self.boat.track_lines[self.boat.next_track_idx]
      return to_line | from_line


if __name__ == '__main__':
    pass
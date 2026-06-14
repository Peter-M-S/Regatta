
from screeninfo import get_monitors

FPS = 60
WIDTH, HEIGHT = [(m.width - 25, m.height - 75) for m in get_monitors() if m.is_primary][0]
ZOOM_FACTOR: float = 2.0

BG_COLOR_1 = "grey90"
DEPTH_COLORS = [
  "#80dfff",
  "#66d9ff",
  "#4dd2ff",
  "#33ccff",
  "#1ac6ff",
  "#00bfff",
  "#00ace6",
  "#0099cc",
  "#0086b3"
]
GRID_COLOR = "lightblue3"

PANEL_SIZE = PANEL_WIDTH, PANEL_HEIGHT = 240, 60
MAP_RIGHT = WIDTH - PANEL_WIDTH

PANEL_DATA: dict = {  # x, y, width, height
  "MAP": (0, 0, MAP_RIGHT, HEIGHT),
  "INFO": (MAP_RIGHT, 0, PANEL_WIDTH, 2 * PANEL_HEIGHT),
  "HUD": (MAP_RIGHT, 2 * PANEL_HEIGHT, PANEL_WIDTH, 2 * PANEL_HEIGHT),
  "SKIPPER": (MAP_RIGHT, 4 * PANEL_HEIGHT, PANEL_WIDTH, HEIGHT - 5 * PANEL_HEIGHT),
  "SETTINGS": (MAP_RIGHT, HEIGHT - PANEL_HEIGHT, PANEL_WIDTH, PANEL_HEIGHT)
}

# direction index:
# 7 0 1
# 6   2
# 5 4 3
DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
DIRECTION_IDX = list(range(8))
SPACES = [0, 1, 2, 3, 2, 3, 2, 1]
DIE_SIDES: list = [1, 2, 2, 3, 'CW', 'CCW']  # original die
# DIE_SIDES: list = [1, 2, 2, 3]  # no wind change
# DIE_SIDES: list = [3, 3]  # no wind change, max legs
# DIE_SIDES: list =[1, 1, 2, 2, 2, 2, 3, 3, 'CW', 'CCW', ' ', ' ']   # less volatile wind change

BOAT_NAMES = ['Juliet', 'Romeo', 'Mike', 'Oscar', 'Charlie', 'Victor']
BOAT_COLORS = ['blue', 'red', 'royalblue4', 'yellow', 'purple', 'white']
BOAT_POINTS = [(20, 0), (20, 35), (15, 35), (15, 15), (20, 0), (20, 35), (25, 35), (25, 15), (20, 0)]   # 40 px * 40 px
DOCK_COLORS = ["burlywood3", "burlywood4", "grey30"]

TEXT_COLORS = ['blue', 'red', 'royalblue4', 'orange3', 'purple', 'black']
OPTIONS = ["sail", "leeward", "windward", "tack", "luff", "port", "star", "spin", "unspin", "puff",
           "unpuff", "lines", "reset", "forfeit", "finalize", "roll"]
STATE_EXCLUSIONS = ['skipper', 'color', 'initial_state', 'after_race_position', 'OPTIONS', 'track_lines',
                    'name', "show_laylines", 'text_color']
SPRITE_SIZE = 40, 40


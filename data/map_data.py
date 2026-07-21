import random

from data.constants import WIDTH, HEIGHT
from aux.utils import get_cell_size


def _get_map_edges(size: tuple) -> set:
  edges = list()
  rows, cols = size
  for r in range(rows):
    for c in range(cols):
      if 0 < c < cols - 1 and 0 < r < rows - 1: continue
      edges.append((r, c))
      if random.random() < 0.15:
        if r == 0: edges.append((1,c))
        if c == 0: edges.append((r, 1))
        if r == rows-1: edges.append((rows-2, c))
        if c == cols-1: edges.append((r, cols-2))
  return set(edges)


MAP_DATA = {
  "North Bay": {
    "size": (25, 41),  # rows, cols
    "cell_size": get_cell_size(25, 41, WIDTH, HEIGHT),
    "islands": {
      (12, 14), (12, 15), (12, 16), (12, 17), (11, 16), (11, 17), (13, 14), (13, 15), (13, 16), (13, 17), (14, 15)
    },
    "edges": _get_map_edges((25, 41)),
    "race": (2, 20),
    "windbag": (2, 20),
    "marks": [
      ((10, 20), 0, 0),
      ((18, 8), 6, 4),
      ((18, 32), 4, 2),
      ((5, 32), 2, 0)
    ],
    "reverse_finish": False,
    "countdown": -5,
    "windward_index": 6,
    "dock": [(17 - i, 18) for i in range(6)],
    "dock offset": 2
  },
  "South Bay": {
    "size": (42, 69),  # rows, cols
    "cell_size": get_cell_size(41, 67, WIDTH, HEIGHT),
    "islands": set([(13, 13)] +
    [(r + 1, c) for r in range(12) for c in range(11 + random.randint(-1, 1), 17 + random.randint(-1, 1))] +
    [(r + 1, c) for r in range(12) for c in range(34 + random.randint(-1, 1), 40 + random.randint(-1, 1))] +
    [(r + 28, c) for r in range(12) for c in range(32 + random.randint(-1, 1), 38 + random.randint(-1, 1))]),
    "edges": _get_map_edges((42, 69)),
    "race": (30, 8),
    "windbag": (30, 8),
    "marks": [
      ((20, 8), 4, 4),
      ((32, 56), 4, 2),
      ((9, 47), 0, 6),
      ((8, 24), 0, 6)
    ],
    "reverse_finish": True,
    "countdown": -3,
    "windward_index": 2,
    "dock": [(1 + i, 9) for i in range(6)],
    "dock offset": 6
  },
  "Lake Lab": {
    "size": (25, 41),  # rows, cols
    "cell_size": get_cell_size(25, 40, WIDTH, HEIGHT),
    "islands": set(),
    "edges": _get_map_edges((25, 41)),
    "race": (2, 20),
    "windbag": (2, 20),
    "marks": [
      ((10, 20), 0, 0),
      ((18, 8), 6, 4),
      ((18, 32), 4, 2),
      ((5, 32), 2, 0)
    ],
    "reverse_finish": False,
    "countdown": -1,
    "windward_index": 6,
    "dock": [(11, 28-i) for i in range(6)],
    "dock offset": 0
  }

}

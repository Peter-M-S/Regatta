# ⛵ Regatta

A turn-based sailing strategy game built with **Python** and **Pygame**, inspired by classic dice-driven sailboat racing board games. Race against friends or AI skippers across different maps, navigate wind shifts, manage your spinnaker and puffs, and be the first across the finish line!

[Deutsch](README.de.md) | English

## Features

- 🎲 **Dice-driven movement** – roll the die to determine how many "legs" you can sail and whether the wind shifts.
- 🌬️ **Dynamic wind system** – wind direction rotates over time and affects your course relative to heading.
- 🧭 **Right-of-way rules** – advanced sailing rules determine which boats must keep clear.
- 🤖 **AI Skippers** – play against `smartbot` opponents that use a recursive search over possible action sequences combined with BFS-based distance maps to choose optimal moves.
- 🗺️ **Multiple maps** – race on "North Bay" or "South Bay".
- 🏁 **Full race track** – sail around marks, cross start/finish lines, and manage spinnaker/puff bonuses.
- 🌍 **Multi-language UI** – supports English, German, French, and Spanish.
- 📊 **Live HUD & info panels** – track legs, spaces, marks, tack, spinnaker status, puffs, round number, and final rankings.

## Requirements

- Python 3.10+
- [pygame](https://www.pygame.org/)
- [numpy](https://numpy.org/)
- [screeninfo](https://pypi.org/project/screeninfo/)

Install dependencies:

```bash
pip install pygame numpy screeninfo
```

## Getting Started

Clone the repository and run the main script:

```bash
git clone <repository-url>
cd <repository-folder>
python main.py
```

By default, `main.py` starts a race on the **South Bay** map with 6 `smartbot` opponents. You can adjust the number of human vs. bot skippers and the chosen map directly in `main.py`:

```python
n = (0, 6)  # (number of humans, number of bots)
map_name = "South Bay"
```

## Controls

- During your turn, select an action from the **Skipper Panel** on the right side of the screen (e.g., sail, tack, leeward/windward, raise/lower spinnaker, activate puff, etc.).
- Press **Roll** to throw the die at the start of a round.
- Toggle **Zoom In/Out** via the Settings Panel to focus on your boat.
- Press **ESC** or close the window to quit.

## Configuration

Game behavior can be tweaked in `config.py`:

| Setting | Description                                  |
|---|----------------------------------------------|
| `AUTO_DICE` | Automatically roll the die for human players |
| `SHOW_PATH` | Draw the trail of each boat's movement       |
| `SHOW_FLAG` | Display identifier flags above boats         |
| `SHOW_LINES` | Show start/finish/track lines and laylines   |
| `SHOW_TICKER` | Show scrolling news ticker at the bottom     |
| `SHOW_CLOUDS` | Animate clouds drifting with the wind        |
| `KEEP_MAIN_WIND_DIRECTION` | Prevent the wind from rotating fully|
| `ADVANCED_RULES` | Enable right-of-way rules between boats      |
| `DIE_SIDES` | Customize the die faces (legs, wind shifts)  |
| `ZOOM_FACTOR` | Magnification level when zoomed in           |
| `CURRENT_LANG` | UI language (`EN`, `DE`, `FR`, `ES`)         |

## Project Structure

```
.
├── main.py                 # Entry point – configure skippers and map
├── config.py               # Global game configuration / feature flags
├── classes/
│   ├── regatta.py          # Main game loop and rules engine
│   ├── boat.py              # Boat state, actions, options, rendering
│   ├── agent.py             # AI skipper logic (simplebot / smartbot)
│   ├── environment.py       # Wind, race course, marks and track lines
│   └── panels.py             # UI panels (map, info, HUD, skipper, settings)
├── aux/
│   ├── widgets.py            # Buttons, labels, ticker widgets
│   └── utils.py               # Helper functions (drawing, coordinates, etc.)
├── data/
│   ├── constants.py           # Game constants (directions, colors, panel layout)
│   ├── map_data.py             # Map definitions (size, marks, islands, docks)
│   └── strings.py               # Localized UI strings
└── assets/                       # Sprites and sound effects
```

## How the Game Works

Each round, players roll a die that either:
- Grants a number of **legs** (moves) to spend on actions such as sailing, tacking, jibing, raising the spinnaker, or activating a puff, or
- **Shifts the wind** clockwise or counter-clockwise.

Boats must navigate around islands, the dock, and other boats while following right-of-way rules. The goal is to sail through the marks in the correct order and cross the finish line first.

## AI Skippers

- **simplebot**: a placeholder bot that simply forfeits its turn.
- **smartbot**: performs a recursive depth-first search over all possible action sequences for the current turn, scoring each resulting position using precomputed BFS distance maps to the next mark, and picks the sequence with the highest score.

## License

This project is provided as-is for educational and recreational purposes. 
This project is licensed under MIT – see [LICENSE](LICENSE) for details.
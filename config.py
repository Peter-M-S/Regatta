
# AUTO_DICE: bool = True
AUTO_DICE: bool = False

# SHOW_PATH = True
SHOW_PATH = False

# SHOW_FLAG = True
SHOW_FLAG = False

# SHOW_LINES = True
SHOW_LINES = False

SHOW_TICKER = True
# SHOW_TICKER = False

# SHOW_CLOUDS = True
SHOW_CLOUDS = False

KEEP_MAIN_WIND_DIRECTION: bool = True
# KEEP_MAIN_WIND_DIRECTION: bool = False

ADVANCED_RULES: bool = True
# ADVANCED_RULES: bool = False

DIE_SIDES: list = [1, 2, 2, 3, 'CW', 'CCW']  # original die
# DIE_SIDES: list = [1, 2, 2, 3]  # no wind change
# DIE_SIDES: list = [3, 3]  # no wind change, max legs
# DIE_SIDES: list =[1, 1, 2, 2, 2, 2, 3, 3, 'CW', 'CCW', ' ', ' ']   # less volatile wind change

ZOOM_FACTOR: float = 2.0

CURRENT_LANG = "DE"
# CURRENT_LANG = "EN"
# CURRENT_LANG = "FR"
# CURRENT_LANG = "ES"

# DEBUG_DIST_MAPS = True
DEBUG_DIST_MAPS = False

# Zentrales Dict für das Settings-Menü (nur toggle-bare bool-Einstellungen)
SETTINGS_OPTIONS: dict = {
    "AUTO_DICE":                 "Auto-Würfeln",
    "SHOW_PATH":                 "Pfad anzeigen",
    "SHOW_FLAG":                 "Flaggen anzeigen",
    "SHOW_LINES":                "Linien anzeigen",
    "SHOW_TICKER":               "Ticker anzeigen",
    "SHOW_CLOUDS":               "Wolken anzeigen",
    "KEEP_MAIN_WIND_DIRECTION":  "Windrichtung halten",
    "ADVANCED_RULES":            "Erweiterte Regeln",
}

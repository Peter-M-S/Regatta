# AUTO_DICE: bool = True
AUTO_DICE: bool = False

# SHOW_PATH = True
SHOW_PATH: bool = False

# SHOW_FLAG = True
SHOW_FLAG: bool = False

# SHOW_LINES = True
SHOW_LINES: bool = False

SHOW_TICKER: bool = True
# SHOW_TICKER = False

# SHOW_CLOUDS = True
SHOW_CLOUDS: bool = False

KEEP_MAIN_WIND_DIRECTION: bool = True
# KEEP_MAIN_WIND_DIRECTION: bool = False

ADVANCED_RULES: bool = True
# ADVANCED_RULES: bool = False

CURRENT_LANG = "DE"
# CURRENT_LANG = "EN"
# CURRENT_LANG = "FR"
# CURRENT_LANG = "ES"

# DEBUG_DIST_MAPS = True
DEBUG_DIST_MAPS = False

# Zentrales Dict für das Settings-Menü (nur toggle-bare bool-Einstellungen)
# todo move texts to strings for each language
# todo include selection of langauge (radio button or list selection)
SETTINGS_OPTIONS: list = ["AUTO_DICE", "SHOW_PATH", "SHOW_FLAG", "SHOW_LINES", "SHOW_TICKER",
                          "SHOW_CLOUDS", "KEEP_MAIN_WIND_DIRECTION", "ADVANCED_RULES"]

# SETTINGS_OPTIONS: dict = {
#   "AUTO_DICE": "Auto-Würfeln",
#   "SHOW_PATH": "Pfad anzeigen",
#   "SHOW_FLAG": "Flaggen anzeigen",
#   "SHOW_LINES": "Linien anzeigen",
#   "SHOW_TICKER": "Ticker anzeigen",
#   "SHOW_CLOUDS": "Wolken anzeigen",
#   "KEEP_MAIN_WIND_DIRECTION": "Windrichtung halten",
#   "ADVANCED_RULES": "Erweiterte Regeln",
# }

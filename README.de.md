[English](README.md) | Deutsch

# ⛵ Regatta

Ein rundenbasiertes Segel-Strategiespiel mit **Python** und **Pygame**, inspiriert von klassischen würfelbasierten Segelboot-Brettspielen. Tritt gegen Freunde oder KI-Skipper auf verschiedenen Karten an, navigiere durch Windwechsel, setze Spinnaker und Böen geschickt ein und überquere als Erster die Ziellinie!

## Features

- 🎲 **Würfelbasierte Bewegung** – würfle, um zu bestimmen, wie viele "Etappen" (Legs) du segeln kannst und ob sich der Wind dreht.
- 🌬️ **Dynamisches Windsystem** – die Windrichtung dreht sich im Spielverlauf und beeinflusst deinen Kurs relativ zur Steuerrichtung.
- 🧭 **Vorfahrtsregeln** – erweiterte Segelregeln bestimmen, welches Boot ausweichen muss.
- 🤖 **KI-Skipper** – spiele gegen `smartbot`-Gegner, die eine rekursive Suche über mögliche Aktionsfolgen kombiniert mit BFS-basierten Distanzkarten nutzen, um optimale Züge zu wählen.
- 🗺️ **Mehrere Karten** – segle auf "North Bay" or "South Bay".
- 🏁 **Vollständige Regattabahn** – segle um die Bojen, überquere Start- und Ziellinie und nutze Spinnaker-/Böen-Boni.
- 🌍 **Mehrsprachige UI** – Unterstützung für Deutsch, Englisch, Französisch und Spanisch.
- 📊 **Live-HUD & Info-Anzeigen** – behalte Etappen, freie Felder, Bug, Spinnaker-Status, Böen, Rundenzahl und Endplatzierung im Blick.

## Voraussetzungen

- Python 3.10+
- [pygame](https://www.pygame.org/)
- [numpy](https://numpy.org/)
- [screeninfo](https://pypi.org/project/screeninfo/)

Abhängigkeiten installieren:

```bash
pip install pygame numpy screeninfo
```

## Erste Schritte

Repository klonen und das Hauptskript ausführen:

```bash
git clone <repository-url>
cd <repository-folder>
python main.py
```

Standardmäßig startet `main.py` ein Rennen auf der Karte **South Bay** mit 6 `smartbot`-Gegnern. Du kannst die Anzahl von Menschen vs. Bots sowie die Karte direkt in `main.py` anpassen:

```python
n = (0, 6)  # (Anzahl Menschen, Anzahl Bots)
map_name = "South Bay"
```

## Steuerung

- Wähle während deines Zuges eine Aktion im **Skipper-Panel** auf der rechten Seite des Bildschirms (z. B. segeln, wenden, abfallen/anluven, Spinnaker setzen/einholen, Bö aktivieren usw.).
- Drücke **Würfeln**, um zu Beginn einer Runde den Würfel zu werfen.
- Wechsle über das Einstellungs-Panel zwischen **Hinein-/Herauszoomen**, um dein Boot zu fokussieren.
- Drücke **ESC** oder schließe das Fenster, um das Spiel zu beenden.

## Konfiguration

Das Spielverhalten kann in `config.py` angepasst werden:

| Einstellung | Beschreibung                                               |
|---|------------------------------------------------------------|
| `AUTO_DICE` | Würfel für menschliche Spieler automatisch werfen          |
| `SHOW_PATH` | Zeigt die Bewegungsspur jedes Boots an                     |
| `SHOW_FLAG` | Zeigt Identifikationsflaggen über den Booten an            |
| `SHOW_LINES` | Zeigt Start-/Ziel-/Streckenlinien und Laylinien an         |
| `SHOW_TICKER` | Zeigt den Laufband-Ticker am unteren Bildschirmrand        |
| `SHOW_CLOUDS` | Animiert mit dem Wind ziehende Wolken                      |
| `KEEP_MAIN_WIND_DIRECTION` | Verhindert, dass sich der Wind aus der Hauptrichtung dreht |
| `ADVANCED_RULES` | Aktiviert Vorfahrtsregeln zwischen Booten                  |
| `DIE_SIDES` | Würfelseiten anpassen (Etappen, Windwechsel)               |
| `ZOOM_FACTOR` | Vergrößerungsstufe im Zoom-Modus                           |
| `CURRENT_LANG` | UI-Sprache (`EN`, `DE`, `FR`, `ES`)                        |

## Projektstruktur

```
.
├── main.py                 # Einstiegspunkt – Skipper und Karte konfigurieren
├── config.py               # Globale Spielkonfiguration / Feature-Flags
├── classes/
│   ├── regatta.py          # Haupt-Spielschleife und Regelwerk
│   ├── boat.py              # Bootszustand, Aktionen, Optionen, Darstellung
│   ├── agent.py             # KI-Skipper-Logik (simplebot / smartbot)
│   ├── environment.py       # Wind, Regattabahn, Bojen und Streckenlinien
│   └── panels.py             # UI-Panels (Karte, Info, HUD, Skipper, Einstellungen)
├── aux/
│   ├── widgets.py            # Buttons, Labels, Ticker-Widgets
│   └── utils.py               # Hilfsfunktionen (Zeichnen, Koordinaten, etc.)
├── data/
│   ├── constants.py           # Spielkonstanten (Richtungen, Farben, Panel-Layout)
│   ├── map_data.py             # Kartendefinitionen (Größe, Bojen, Inseln, Steg)
│   └── strings.py               # Lokalisierte UI-Texte
└── assets/                       # Sprites und Soundeffekte
```

## Spielablauf

Jede Runde würfelt jeder Spieler. Der Würfel gewährt entweder:
- eine Anzahl von **Etappen** (Zügen), die für Aktionen wie Segeln, Wenden, Halsen, Spinnaker setzen oder Bö aktivieren genutzt werden können, oder
- führt zu einem **Windwechsel** im oder gegen den Uhrzeigersinn.

Die Boote müssen um Inseln, den Steg und andere Boote navigieren und dabei die Vorfahrtsregeln beachten. Ziel ist es, die Bojen in der richtigen Reihenfolge zu umsegeln und als Erster die Ziellinie zu überqueren.

## KI-Skipper

- **smartbot**: führt eine rekursive Tiefensuche über alle möglichen Aktionsfolgen des aktuellen Zuges durch, bewertet jede resultierende Position anhand vorberechneter BFS-Distanzkarten zur nächsten Boje und wählt die Folge mit der höchsten Punktzahl.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz – siehe die Datei [LICENSE](LICENSE) für Details.

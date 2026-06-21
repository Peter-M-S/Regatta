import random

from classes.regatta import Regatta
from classes.main_menu import MainMenu

# todo human boat is reset to last position when crossing finish !?
# todo start with a main menu to select skippers and map, then (re-)open regatta window.
# todo after game over enable button to return to main menu


def main(n: tuple | None, m: int | None):
  # n = (3, 0)
  # n = (1, 1)
  # n = (1, 3)
  # n = (0, 3)
  # n = (0, 6)

  # m = 0
  # m = 1
  map_names = ["North Bay", "South Bay"]

  skippers = (
      ['human'] * n[0]
      + ['smartbot'] * n[1]
  )
  random.shuffle(skippers)
  R = Regatta(skippers, map_names[m])
  R.run()


if __name__ == '__main__':
  menu = MainMenu()
  resume_main_menu = True
  while resume_main_menu:
    result = menu.run()
    if result[0] == "start":
      main(result[1], result[2])
    elif result[0] == "quit":
      resume_main_menu = False


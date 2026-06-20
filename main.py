import random

from classes.regatta import Regatta

# todo human boat is reset to last position when crossing finish !?
# todo start with a main menu to select skippers and map, then (re-)open regatta window.
# todo after game over enable button to return to main menu


def main():
  # n = (3, 0)
  n = (1, 1)
  # n = (1, 3)
  # n = (0, 3)
  # n = (0, 6)

  map_name = "North Bay"
  # map_name = "South Bay"

  skippers = (
      ['human'] * n[0]
      + ['smartbot'] * n[1]
  )
  random.shuffle(skippers)
  R = Regatta(skippers, map_name)
  R.run()


if __name__ == '__main__':
    main()

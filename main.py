import random

from classes.regatta import Regatta


def main():
  # n = (3, 0)
  # n = (1, 0)
  # n = (1, 2)
  # n = (0, 3)
  n = (0, 6)

  # map_name = "North Bay"
  map_name = "South Bay"

  skippers = (
      ['human'] * n[0]
      + ['smartbot'] * n[1]
  )
  random.shuffle(skippers)
  R = Regatta(skippers, map_name)
  R.run()


if __name__ == '__main__':
    main()

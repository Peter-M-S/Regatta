from collections import deque

import pygame as pg

from data.constants import BG_COLOR_1

TEXT_COLOR, BASE_COLOR, HOVERING_COLOR = "grey", "black", "green3"
FONT_TYPE = "Arial"

pg.init()


def get_font(size):  # Returns FONT in the desired size
  return pg.font.SysFont(FONT_TYPE, size)


class Button:
  def __init__(self, center_pos, text, font_size, size: tuple, action=None,
               base_color=BASE_COLOR, hovering_color=HOVERING_COLOR) -> None:
    self.x, self.y = center_pos
    self.text = text
    self.font = get_font(font_size)
    self.action = action
    self.base_color, self.hovering_color = base_color, hovering_color
    self.click_area: pg.Rect = pg.Rect(0,0,size[0], size[1])
    self.click_area.center = self.x, self.y
    self.text_surface = self.font.render(self.text, True, self.base_color)
    self.text_rect = self.text_surface.get_rect(center=(self.x, self.y))
    self.active = True
    self.clicked = False

  def update(self, surface: pg.Surface, point: tuple | None = None,
             new_text: str | None = None, new_color: str | None = None) -> int | None:
    if not self.active: return None

    self.update_text(new_text=new_text, new_color=new_color)
    if point is not None: self.changeColor(point)
    self.text_rect = self.text_surface.get_rect(center=(self.x, self.y))
    surface.blit(self.text_surface, self.text_rect)
    self.click_area.center = self.x, self.y

    is_hovering = self.click_area.collidepoint(point) if point is not None else False

    if self.action is not None:
      if is_hovering and pg.mouse.get_pressed()[0]: self.clicked = True
      elif self.clicked and not pg.mouse.get_pressed()[0]:
        self.clicked = False
        if is_hovering:  # Only trigger if the release happens over the button
          return self.action()

    return None

  def changeColor(self, point) -> None:
    if self.click_area.collidepoint(point):
      self.text_surface = self.font.render(self.text, True, self.hovering_color)
    else:
      self.text_surface = self.font.render(self.text, True, self.base_color)

  def update_text(self, new_text: str | None = None, new_color: str | None = None) -> None:
    if not new_text and not new_color: return
    if new_text is None: new_text = self.text
    if new_color is None: new_color = self.base_color
    self.text = new_text
    self.base_color = new_color
    self.text_surface = self.font.render(self.text, True, self.base_color)
    self.text_rect = self.text_surface.get_rect(center=(self.x, self.y))


class TextLabel:
  def __init__(self, center_pos, text, font_size, text_color=TEXT_COLOR):
    self.x, self.y = center_pos
    self.text = str(text)
    self.font = get_font(font_size)
    self.text_color = text_color
    self.text_surface = self.font.render(self.text, True, self.text_color)
    self.text_rect = self.text_surface.get_rect(center=(self.x, self.y))
    self.active = True

  def update_text(self, new_text: str | None = None, new_color: str | None = None) -> None:
    if not new_text and not new_color: return
    if new_text is None: new_text = self.text
    if new_color is None: new_color = self.text_color
    self.text = new_text
    self.text_color = new_color
    self.text_surface = self.font.render(new_text, True, new_color)
    self.text_rect = self.text_surface.get_rect(center=(self.x, self.y))

  def update(self, surface, new_text: str | None = None, new_color: str | None = None) -> None:
    if not self.active: return
    self.update_text(new_text=new_text, new_color=new_color)
    surface.blit(self.text_surface, self.text_rect)


class ImageLabel:
  def __init__(self, center_pos, image: pg.Surface, size: tuple[int, int] | None = None):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.center = center_pos
    if size is not None: self.rect.size = size
    self.active = True

  def update_image(self, new_img: pg.Surface | None = None, new_size: tuple[int, int] | None = None) -> None:
    if new_img is None and new_size is None: return
    if new_img is not None:
      self.image = new_img
    if new_size is not None:
      center = self.rect.center
      self.rect.size = new_size
      self.rect.center = center
    self.image = pg.transform.scale(self.image, self.rect.size)

  def update(self, surface, new_img: pg.Surface | None = None, new_size: tuple[int, int] | None = None) -> None:
    if not self.active: return
    self.update_image(new_img=new_img, new_size=new_size)
    surface.blit(self.image, self.rect)


class Ticker:
  def __init__(self, rect, font, initial_text="", speed:float = 5.0):
    """
    rect: pg.Rect defining the position and size of the ticker on the screen.
    font: a preloaded pg.font.Font object.
    speed: pixels to move per frame (higher = faster).
    """
    self.rect = pg.Rect(rect)
    self.font = font
    self.speed: float = speed
    self.text_color = BG_COLOR_1
    self.bg_color = "black"

    # Local drawing surface matching the frame size
    self.surface = pg.Surface((self.rect.width, self.rect.height))

    self.text_queue: deque = deque()  # list of tuples with text_surface, loops
    self.has_new_text: bool = False
    self.add_text(initial_text, 1)

    self.text_surface, self.loops = self.text_queue.popleft()
    self.loop_count: int = 0
    self.text_x: int = 0

  def must_change_text(self) -> bool:
    return (self.loops != 0 and self.loop_count >= self.loops) or (self.loops == 0 and self.has_new_text)

  def add_text(self, new_text: str, loops: int = 0) -> None:
    """Pre-renders the text message and resets the scrolling position."""
    # Add padding spaces at the beginning so it starts off-screen to the right
    padded_text = " " * 5 + new_text + " " * 5
    text_surface = self.font.render(padded_text, True, self.text_color)
    self.text_queue.append((text_surface, loops))
    self.has_new_text = True

  def update(self):

    self.text_x -= self.speed

    if self.must_change_text():
      if not self.text_queue:
        self.add_text("", 0)
      self.text_surface, self.loops = self.text_queue.popleft()
      self.loop_count = 0
      self.text_x = self.rect.width

    # Loop check: If the text has scrolled completely out of view to the left, reset it
    if self.text_x < -self.text_surface.get_width():
      self.text_x = self.rect.width
      self.loop_count += 1
      if self.loop_count == 1: self.has_new_text = False

  def draw(self, destination_surface: pg.Surface):

    self.surface.fill(self.bg_color)

    if self.text_surface:
      # Vertically center the text inside the ticker bar
      text_y = (self.rect.height - self.text_surface.get_height()) // 2
      self.surface.blit(self.text_surface, (self.text_x, text_y))

    destination_surface.blit(self.surface, self.rect.topleft)


if __name__ == '__main__':
    pass

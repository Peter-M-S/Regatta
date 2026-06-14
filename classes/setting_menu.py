from panels import Panel
from aux.widgets import TextLabel, Button


class SettingMenu(Panel):

  def __init__(self,x: int, y: int, width: int, height: int):
    super().__init__(x, y, width, height)
    self.back_up: dict = dict()

    self.title = TextLabel((width//2, 10), "Settings", 20)
    self.map_skipper_panel = MapSkipperPanel(0, 40, width//2, height-80)
    self.config_panel = ConfigPanel(width//2, 40, width//2, height-80)
    self.restart_button: Button = Button((width//4, height - 20), "Restart", 20, (width//4, 40))
    self.resume_button: Button = Button((width * 3//4, height - 20),"Restart", 20, (width//4, 40))

  def update(self):
    self.surface.fill("black")
    self.title.update(self.surface)
    self.map_skipper_panel.update(self.surface, self.mouse_pos)
    self.config_panel.update(self.surface, self. mouse_pos)
    self.restart_button.update(self.surface, self.mouse_pos)
    self.resume_button.update(self.surface, self.mouse_pos)


class MapSkipperPanel(Panel):

  def __init__(self, x: int, y: int, width: int, height: int):
    super().__init__(x, y, width, height)
    self.surface.fill("red")

  def update(self, surface, mouse_pos):
    ...


class ConfigPanel(Panel):

  def __init__(self, x: int, y: int, width: int, height: int):
    super().__init__(x, y, width, height)
    self.surface.fill("green")

  def update(self, surface, mouse_pos):
    ...


def open_setting_menu():
  # get input for back-up (current state)
  # display SettingMenu Panel
  pass

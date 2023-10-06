from enum import Enum

class Signal:
    # TODO: Define the types of x_vec, y_vec
    def __init__(self, x_vec, y_vec) -> None:
        self.title = "untitled signal"
        self.color = SignalColor.DEFAULT
        self.x_vec = x_vec
        self.y_vec = y_vec


class SignalColor(Enum):
    DEFAULT = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    ORAGNE = 5
    PURPLE = 6

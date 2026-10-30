import re
from dataclasses import dataclass


@dataclass
class StepRepeat:
    x_repeat: int
    y_repeat: int
    x_step: float
    y_step: float


def _parse_step_repeat(self, value: str):
    # value es: "SRX2Y3I10.0J5.0*"
    body = value[2:-1]  # togli "SR" e "*"

    # regex per catturare i valori
    m = re.match(r"X(\d+)Y(\d+)I([\d\.]+)J([\d\.]+)", body)
    if not m:
        raise ValueError(f"Unrecognized StepRepeat: {value}")

    x_repeat = int(m.group(1))
    y_repeat = int(m.group(2))
    x_step = float(m.group(3))
    y_step = float(m.group(4))

    self.step_repeat = StepRepeat(x_repeat, y_repeat, x_step, y_step)

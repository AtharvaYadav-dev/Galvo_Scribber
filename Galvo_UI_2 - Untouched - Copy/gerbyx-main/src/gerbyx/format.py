import re
from dataclasses import dataclass


@dataclass
class FormatSpec:
    zero_omission: str   # "L" (leading) o "T" (trailing)
    coord_mode: str      # "A" (absolute) o "I" (incremental)
    x_int: int
    x_dec: int
    y_int: int
    y_dec: int


def parse_format_spec(value: str) -> FormatSpec:
    # value es: "FSLAX24Y24*"
    body = value[2:-1]  # togli "FS" e "*"
    # es: "LAX24Y24"
    zero_omission = body[0]   # L o T
    coord_mode = body[1]      # A o I

    # regex per X e Y
    m = re.search(r"X(\d)(\d)Y(\d)(\d)", body)
    if not m:
        raise ValueError(f"FormatSpec malformato: {value}")

    x_int, x_dec, y_int, y_dec = map(int, m.groups())

    return FormatSpec(
        zero_omission=zero_omission,
        coord_mode=coord_mode,
        x_int=x_int,
        x_dec=x_dec,
        y_int=y_int,
        y_dec=y_dec
    )

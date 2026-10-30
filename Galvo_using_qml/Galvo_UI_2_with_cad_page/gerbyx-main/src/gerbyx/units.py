from dataclasses import dataclass


@dataclass
class Units:
    code: str   # "IN" o "MM"


def parse_units(value: str) -> Units:
    # value es: "MOIN*" oppure "MOMM*"
    body = value[2:-1]  # togli "MO" e "*"
    if body == "IN":
        return Units("IN")
    elif body == "MM":
        return Units("MM")
    else:
        raise ValueError(f"Units not supported: {body}")

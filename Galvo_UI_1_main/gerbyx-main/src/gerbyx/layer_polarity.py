from dataclasses import dataclass


@dataclass
class LayerPolarity:
    mode: str   # "DARK" o "CLEAR"


def parse_layer_polarity(value: str) -> LayerPolarity:
    # value es: "LPD*" oppure "LPC*"
    body = value[2:-1]  # togli "LP" e "*"
    if body == "D":
        return LayerPolarity("DARK")
    elif body == "C":
        return LayerPolarity("CLEAR")
    else:
        raise ValueError(f"Polarity not supported: {body}")

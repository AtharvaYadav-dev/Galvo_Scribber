import re
from dataclasses import dataclass
from typing import List


@dataclass
class Aperture:
    id: str
    type: str
    params: List[float]


def parse_aperture_def(value: str) -> Aperture:
    # value es: "ADD10R,1.100000X1.000000*"
    # Rimuovi "AD" iniziale e "*" finale
    if value.startswith("AD"):
        body = value[2:-1]
    else:
        body = value.strip('*')

    # Cerca D<digits> all'inizio
    match = re.match(r"(D\d+)(.*)", body)
    if not match:
        raise ValueError(f"Invalid aperture definition: {value}")

    aperture_id = match.group(1) # Es: "D10"
    rest = match.group(2) # Es: "R,1.0X1.0" o "C,1.0"

    # Rimuovi virgola iniziale se presente (alcuni formati la mettono, altri no?)
    # Standard: ADDnn<template>[,<modifiers>]
    # In realtà la virgola separa template da modifiers, ma spesso è attaccata.
    # Esempio: ADD10C,1.0 -> Template=C, Modifiers=1.0

    # Analizziamo 'rest'. Deve iniziare con il codice template (C, R, O, P) o nome macro.
    if not rest:
        raise ValueError(f"Empty aperture definition body: {value}")

    # Il tipo è tutto ciò che c'è prima della prima virgola o cifra?
    # Standard: The aperture type is a name... standard templates are C, R, O, P.
    # Esempio: ADD10C,0.5* -> Type C
    # Esempio: ADD10Circle,0.5* -> Type Circle (Macro?)

    # Prendiamo il primo carattere come tipo se è C, R, O, P E seguito da virgola o fine
    first_char = rest[0]

    # Controlla se è un template standard (singolo carattere C, R, O, P)
    if first_char in ['C', 'R', 'O', 'P'] and (len(rest) == 1 or rest[1] in [',', '*']):
        ap_type = first_char
        params_str = rest[1:]
    else:
        # Macro o nome lungo
        # Cerca la virgola
        if ',' in rest:
            ap_type, params_str = rest.split(',', 1)
        else:
            ap_type = rest
            params_str = ""

    # Pulisci params_str
    if params_str.startswith(','):
        params_str = params_str[1:]

    params = []
    if params_str:
        # I parametri sono separati da X
        parts = params_str.split('X')
        try:
            params = [float(p) for p in parts]
        except ValueError:
            pass

    return Aperture(aperture_id, ap_type, params)

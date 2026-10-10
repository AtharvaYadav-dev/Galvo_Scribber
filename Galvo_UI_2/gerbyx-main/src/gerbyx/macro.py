from dataclasses import dataclass
from typing import List

@dataclass
class Macro:
    name: str
    body: List[str]   # lista di primitive

def parse_macro_start(value: str) -> str:
    """
    Estrae il nome della macro dall'inizio della definizione.
    value es: "AMRECT*"
    """
    # Rimuovi "AM" iniziale e "*" finale
    if value.startswith("AM") and value.endswith("*"):
        return value[2:-1]
    raise ValueError(f"Invalid macro start: {value}")

def parse_macro_body(value: str) -> str:
    """
    Restituisce la primitiva della macro pulita.
    value es: "0 Rectangle,1.0X2.0,0,0*"
    """
    # Rimuovi "*" finale se presente
    if value.endswith("*"):
        return value[:-1]
    return value

from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ApertureBlock:
    id: str
    tokens: List[Tuple[str, str]] # Lista di (kind, value)

def parse_ab_start(value: str) -> str:
    """
    Estrae l'ID del blocco dall'inizio della definizione.
    value es: "AB10*"
    """
    # Rimuovi "AB" iniziale e "*" finale
    if value.startswith("AB") and value.endswith("*"):
        block_id = value[2:-1]
        if not block_id:
            raise ValueError("Aperture Block ID missing")
        return block_id
    raise ValueError(f"Invalid aperture block start: {value}")

def is_ab_end(value: str) -> bool:
    """Controlla se il valore è la fine di un blocco (ABEND*)."""
    return value == "ABEND*"

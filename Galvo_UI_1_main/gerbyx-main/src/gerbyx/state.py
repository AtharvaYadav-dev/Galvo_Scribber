from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from .format import FormatSpec
from .units import Units
from .aperture import Aperture
from .layer_polarity import LayerPolarity
from .step_repeat import StepRepeat

@dataclass
class PlotState:
    """
    Rappresenta lo stato completo del plotter Gerber in un dato momento.
    """
    # Configurazione
    units: Optional[Units] = None
    format_spec: Optional[FormatSpec] = None
    layer_polarity: LayerPolarity = field(default_factory=lambda: LayerPolarity("DARK"))

    # Definizioni
    apertures: Dict[str, Aperture] = field(default_factory=dict)
    macros: Dict[str, list] = field(default_factory=dict) # Nome macro -> lista primitive

    # Stato Plotter
    current_point: Tuple[float, float] = (0.0, 0.0)
    current_aperture_id: Optional[str] = None
    interpolation_mode: str = 'Linear' # 'Linear' (G01), 'ClockwiseCircular' (G02), 'CounterClockwiseCircular' (G03)
    quadrant_mode: str = 'Multi' # 'Multi' (G75), 'Single' (G74)
    region_mode: bool = False # G36/G37

    step_repeat: Optional[StepRepeat] = None

    # Attributi (TF, TA, TO, TCMP)
    file_attributes: Dict[str, list] = field(default_factory=dict)
    aperture_attributes: Dict[str, list] = field(default_factory=dict)
    object_attributes: Dict[str, list] = field(default_factory=dict)

    def get_current_aperture(self) -> Optional[Aperture]:
        if self.current_aperture_id:
            return self.apertures.get(self.current_aperture_id)
        return None

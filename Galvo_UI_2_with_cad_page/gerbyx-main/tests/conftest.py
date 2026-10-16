"""Pytest configuration and shared fixtures"""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_gerber():
    """Simple valid Gerber X3 file"""
    return """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
D10*
X10000Y10000D03*
M02*
"""


@pytest.fixture
def gerber_with_macro():
    """Gerber with macro aperture (using polygon primitive instead of circle)"""
    return """
%FSLAX24Y24*%
%MOMM*%
%AMHEXAGON*
5,1,6,2.0,0,0,0*
%AM*%
%ADD10HEXAGON*%
D10*
X10000Y10000D03*
M02*
"""


@pytest.fixture
def gerber_with_attributes():
    """Gerber with X3 attributes"""
    return """
%FSLAX24Y24*%
%MOMM*%
%TF.FileFunction,Copper,L1,Top*%
%ADD10C,1.0*%
%TO.C,R1*%
%TO.CVal,10K*%
D10*
X10000Y10000D03*
M02*
"""


@pytest.fixture
def gerber_with_region():
    """Gerber with region"""
    return """
%FSLAX24Y24*%
%MOMM*%
G36*
X0Y0D02*
X10000Y0D01*
X10000Y10000D01*
X0Y10000D01*
X0Y0D01*
G37*
M02*
"""


@pytest.fixture
def gerber_with_aperture_block():
    """Gerber with aperture block"""
    return """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
%ABD20*%
D10*
X0Y0D03*
X5000Y0D03*
%ABEND*%
D20*
X10000Y10000D03*
M02*
"""


@pytest.fixture
def invalid_gerber_no_m02():
    """Invalid Gerber - missing M02"""
    return """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
D10*
X10000Y10000D03*
"""


@pytest.fixture
def excellon_metric_simple():
    """Simple METRIC Excellon file — LZ suppression, 3.3 format."""
    return """M48
METRIC,LZ
T1C0.800
T2C1.000
%
;PTH
T1
X062400Y060750
X062400Y077600
T2
X100000Y075000
M30
"""


@pytest.fixture
def excellon_inch_simple():
    """Simple INCH Excellon file — LZ suppression, 2.4 format."""
    return """M48
INCH,LZ
T1C0.031
T2C0.039
%
;PTH
T1
X02457Y02392
X02457Y03055
T2
X03937Y02953
M30
"""


@pytest.fixture
def excellon_with_slots():
    """Excellon file containing G85 canned slots."""
    return """M48
METRIC,LZ
T1C0.800
T2C1.000
%
T1
X050000Y050000
X150000Y050000
T2
X050000Y100000G85X150000Y100000
M30
"""


@pytest.fixture
def excellon_with_routing():
    """Excellon file containing G00/G01/G02 routing commands."""
    return """M48
METRIC,LZ
T1C2.000
%
T1
G00X010000Y010000
G01X090000Y010000
G01X090000Y040000
G02X040000Y040000A025000
G01X010000Y040000
G05
M30
"""


@pytest.fixture
def excellon_ambiguous_units():
    """Excellon file without unit declaration (ambiguous)."""
    return """M48
FMAT,2
T1C0.800
T2C1.000
%
T1
X062400Y060750
T2
X100000Y075000
M30
"""


@pytest.fixture
def invalid_gerber_no_fs():
    """Invalid Gerber - missing FS"""
    return """
%MOMM*%
%ADD10C,1.0*%
D10*
X10000Y10000D03*
M02*
"""

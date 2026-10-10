"""Test Step & Repeat functionality"""
import pytest
from gerbyx.tokenizer import tokenize_gerber
from gerbyx.parser import GerberParser
from gerbyx.processor import GerberProcessor


def test_step_repeat_basic():
    """Test basic Step & Repeat with 2x2 grid"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX2Y2I5.0J5.0*
D10*
X0Y0D03*
SR*
M02*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    # Check shapes before union
    shapes = processor.layers[0]['shapes']
    assert len(shapes) == 4  # 2x2 grid


def test_step_repeat_3x2():
    """Test Step & Repeat with 3x2 grid"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX3Y2I10.0J5.0*
D10*
X0Y0D03*
SR*
M02*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    shapes = processor.layers[0]['shapes']
    assert len(shapes) == 6  # 3x2 grid


def test_step_repeat_disable():
    """Test Step & Repeat enable and disable"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX2Y2I5.0J5.0*
D10*
X0Y0D03*
SR*
X10000Y0D03*
M02*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    shapes = processor.layers[0]['shapes']
    assert len(shapes) == 5  # 4 from SR + 1 after SR disabled


def test_step_repeat_multiple_shapes():
    """Test Step & Repeat with multiple shapes"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX2Y1I10.0J0*
D10*
X0Y0D03*
X1000Y0D03*
SR*
M02*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    shapes = processor.layers[0]['shapes']
    assert len(shapes) == 4  # 2 shapes × 2 repeats


def test_step_repeat_with_line():
    """Test Step & Repeat with line drawing"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.5*%
SRX2Y1I10.0J0*
G01*
D10*
X0Y0D02*
X5000Y0D01*
SR*
M02*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    shapes = processor.layers[0]['shapes']
    assert len(shapes) == 2  # 1 line × 2 repeats


def test_step_repeat_state():
    """Test Step & Repeat state management"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX2Y2I5.0J5.0*
D10*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    # Check SR state is set
    assert processor.step_repeat is not None
    assert processor.step_repeat.x_repeat == 2
    assert processor.step_repeat.y_repeat == 2
    assert processor.step_repeat.x_step == 5.0
    assert processor.step_repeat.y_step == 5.0


def test_step_repeat_disable_state():
    """Test Step & Repeat disable clears state"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
SRX2Y2I5.0J5.0*
SR*
D10*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    # Check SR state is cleared
    assert processor.step_repeat is None


def test_step_repeat_no_sr():
    """Test normal operation without Step & Repeat"""
    gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
D10*
X0Y0D03*
X5000Y0D03*
M02*
"""
    processor = GerberProcessor()
    parser = GerberParser(processor)
    tokens = tokenize_gerber(gerber)
    parser.parse(tokens)
    
    shapes = processor.layers[0]['shapes']
    assert len(shapes) == 2  # 2 circles, no repetition
    assert processor.step_repeat is None

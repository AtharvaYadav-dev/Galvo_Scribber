"""Tests for parser module"""

import pytest
from gerbyx.parser import GerberParser
from gerbyx.processor import GerberProcessor
from gerbyx.tokenizer import tokenize_gerber


class TestParser:
    """Test suite for Gerber parser"""
    
    def test_parse_format_spec(self):
        """Test parsing of format specification"""
        gerber = "%FSLAX24Y24*%"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        assert processor.state.format_spec is not None
        assert processor.state.format_spec.x_int == 2
        assert processor.state.format_spec.x_dec == 4
    
    def test_parse_units(self):
        """Test parsing of units"""
        gerber = "%MOMM*%"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        assert processor.state.units is not None
        assert processor.state.units.code == "MM"
    
    def test_parse_aperture_definition(self):
        """Test parsing of aperture definition"""
        gerber = "%ADD10C,1.5*%"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        assert 'D10' in processor.state.apertures
        assert processor.state.apertures['D10'].type == 'C'
        assert processor.state.apertures['D10'].params == [1.5]
    
    def test_parse_aperture_selection(self):
        """Test parsing of aperture selection"""
        gerber = "%ADD10C,1.0*%\nD10*"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        assert processor.state.current_aperture_id == 'D10'
    
    def test_parse_macro_definition(self, gerber_with_macro):
        """Test parsing of macro definition"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber_with_macro)
        parser.parse(tokens)
        
        assert 'HEXAGON' in processor.macros
        assert len(processor.macros['HEXAGON'].body) > 0
    
    def test_parse_macro_closing_with_am(self):
        """Test parsing of macro closing with %AM*% (X3)"""
        gerber = """
%AMTEST*
1,1,1.0,0,0,0*
%AM*%
"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        assert 'TEST' in processor.macros
    
    def test_parse_file_attributes(self):
        """Test parsing of file attributes"""
        gerber = "%TF.FileFunction,Copper,L1,Top*%"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        assert 'FileFunction' in processor.file_attributes
    
    def test_parse_object_attributes(self, gerber_with_attributes):
        """Test parsing of object attributes (X3)"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber_with_attributes)
        parser.parse(tokens)
        
        assert 'C' in processor.state.object_attributes
        assert 'CVal' in processor.state.object_attributes
    
    def test_parse_delete_attribute(self):
        """Test parsing of delete attribute (X3)"""
        gerber = """
%FSLAX24Y24*%
%MOMM*%
%TO.C,R1*%
%TD.C*%
"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        # Attribute should be deleted
        assert 'C' not in processor.state.object_attributes
    
    def test_parse_delete_all_attributes(self):
        """Test parsing of delete all attributes (X3)"""
        gerber = """
%FSLAX24Y24*%
%MOMM*%
%TO.C,R1*%
%TO.CVal,10K*%
%TD*%
"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        # All attributes should be deleted
        assert len(processor.state.object_attributes) == 0
    
    def test_parse_region_start_end(self):
        """Test parsing of region start/end"""
        gerber = "G36*\nG37*"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        # Region mode should be off after G37
        assert processor.state.region_mode is False
    
    def test_parse_interpolation_modes(self):
        """Test parsing of interpolation modes"""
        gerber = "G01*\nG02*\nG03*"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        
        for kind, value in tokenize_gerber(gerber):
            if kind == 'stmt':
                parser._parse_stmt(value)
        
        # Last mode should be CounterClockwiseCircular
        assert processor.state.interpolation_mode == 'CounterClockwiseCircular'
    
    def test_parse_m02_command(self):
        """Test parsing of M02 command (X3)"""
        gerber = "M02*"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        # Should not raise error
        parser.parse(tokens)
    
    def test_parse_aperture_block(self, gerber_with_aperture_block):
        """Test parsing of aperture block"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber_with_aperture_block)
        parser.parse(tokens)
        
        assert 'D20' in processor.aperture_blocks
        assert len(processor.aperture_blocks['D20'].tokens) > 0
    
    def test_parse_with_validation(self, simple_gerber):
        """Test parsing with X3 validation enabled"""
        processor = GerberProcessor()
        parser = GerberParser(processor, validate_x3=True)
        
        tokens = tokenize_gerber(simple_gerber)
        # Should not raise error
        parser.parse(tokens)
    
    def test_parse_inline_comment(self):
        """Test parsing of inline comment (X3)"""
        gerber = "G75*G04 comment*"
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        # Should not raise error
        parser.parse(tokens)
        
        assert processor.state.quadrant_mode == 'Multi'

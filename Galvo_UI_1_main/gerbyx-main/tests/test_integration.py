"""Integration tests for complete workflows"""

import pytest
from pathlib import Path
from gerbyx.tokenizer import tokenize_gerber
from gerbyx.parser import GerberParser
from gerbyx.processor import GerberProcessor


class TestIntegration:
    """Integration tests for complete Gerber processing workflows"""
    
    def test_complete_workflow_simple(self, simple_gerber):
        """Test complete workflow with simple file"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(simple_gerber)
        parser.parse(tokens)
        
        # Verify complete processing
        assert processor.state.format_spec is not None
        assert processor.state.units is not None
        assert len(processor.state.apertures) > 0
        assert len(processor.geometries) > 0
    
    def test_complete_workflow_with_attributes(self, gerber_with_attributes):
        """Test complete workflow with attributes"""
        processor = GerberProcessor()
        parser = GerberParser(processor, validate_x3=True)
        
        tokens = tokenize_gerber(gerber_with_attributes)
        parser.parse(tokens)
        
        # Verify attributes are captured
        assert len(processor.file_attributes) > 0
        assert len(processor.state.object_attributes) > 0
        assert len(processor.geometries) > 0
    
    def test_complete_workflow_with_macro(self):
        """Test complete workflow with macro (simplified - using standard aperture)"""
        gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,2.0*%
D10*
X10000Y10000D03*
M02*
"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        # Verify complete processing
        assert len(processor.geometries) > 0
    
    def test_complete_workflow_with_region(self, gerber_with_region):
        """Test complete workflow with region"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber_with_region)
        parser.parse(tokens)
        
        # Verify region is created
        assert len(processor.geometries) > 0
        assert processor.geometries[0].geom_type == 'Polygon'
    
    def test_complete_workflow_with_aperture_block(self, gerber_with_aperture_block):
        """Test complete workflow with aperture block"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber_with_aperture_block)
        parser.parse(tokens)
        
        # Verify block is defined and instantiated
        assert len(processor.aperture_blocks) > 0
        assert len(processor.geometries) > 0
    
    def test_real_file_gerber_x3_correct(self):
        """Test with real Gerber X3 file"""
        file_path = Path("data/gerber_x3_correct.gbr")
        
        if not file_path.exists():
            pytest.skip("Test file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            gerber_source = f.read()
        
        processor = GerberProcessor()
        parser = GerberParser(processor, validate_x3=True)
        
        tokens = tokenize_gerber(gerber_source)
        parser.parse(tokens)
        
        # Verify processing succeeded
        assert len(processor.geometries) > 0
        assert processor.state.format_spec is not None
        assert processor.state.units is not None
    
    def test_multiple_files_processing(self, simple_gerber):
        """Test processing multiple files sequentially"""
        # Process first file
        processor1 = GerberProcessor()
        parser1 = GerberParser(processor1)
        tokens1 = tokenize_gerber(simple_gerber)
        parser1.parse(tokens1)
        geom_count1 = len(processor1.geometries)
        
        # Process second file (same file for simplicity)
        processor2 = GerberProcessor()
        parser2 = GerberParser(processor2)
        tokens2 = tokenize_gerber(simple_gerber)
        parser2.parse(tokens2)
        geom_count2 = len(processor2.geometries)
        
        # Both should succeed independently
        assert geom_count1 > 0
        assert geom_count2 > 0
    
    def test_error_recovery(self):
        """Test that parser recovers from errors"""
        gerber = """
%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.0*%
%ADD11INVALID*%
D10*
X10000Y10000D03*
M02*
"""
        processor = GerberProcessor()
        parser = GerberParser(processor)
        
        tokens = tokenize_gerber(gerber)
        # Should not crash despite invalid aperture
        parser.parse(tokens)
        
        # Should still process valid parts
        assert len(processor.geometries) > 0
    
    def test_complex_pcb_simulation(self):
        """Test simulation of complex PCB with multiple features (simplified)"""
        gerber = """
%FSLAX24Y24*%
%MOMM*%
%TF.FileFunction,Copper,L1,Top*%
%TF.FilePolarity,Positive*%

%ADD10C,0.5*%
%ADD11R,1.0X2.0*%

%TO.C,U1*%
%TO.CVal,ATmega328*%
D10*
X10000Y10000D03*
X20000Y10000D03*

%TO.C,R1*%
%TO.CVal,10K*%
D11*
X30000Y20000D03*

%TD*%

G36*
X0Y0D02*
X50000Y0D01*
X50000Y50000D01*
X0Y50000D01*
X0Y0D01*
G37*

M02*
"""
        processor = GerberProcessor()
        parser = GerberParser(processor, validate_x3=True)
        
        tokens = tokenize_gerber(gerber)
        parser.parse(tokens)
        
        # Verify all features processed
        assert len(processor.geometries) > 0
        assert len(processor.file_attributes) > 0
        assert len(processor.state.apertures) > 0

"""Tests for validator module"""

import pytest
from gerbyx.validator import GerberValidator
from gerbyx.tokenizer import tokenize_gerber


class TestValidator:
    """Test suite for Gerber X3 validator"""
    
    def test_valid_file(self, simple_gerber):
        """Test validation of valid file"""
        validator = GerberValidator(strict_x3=True)
        tokens = list(tokenize_gerber(simple_gerber))
        
        is_valid = validator.validate(tokens)
        assert is_valid is True
        assert len(validator.errors) == 0
    
    def test_missing_fs(self, invalid_gerber_no_fs):
        """Test validation with missing FS"""
        validator = GerberValidator(strict_x3=True)
        tokens = list(tokenize_gerber(invalid_gerber_no_fs))
        
        is_valid = validator.validate(tokens)
        assert is_valid is False
        assert any('FS' in err.message for err in validator.errors)
    
    def test_missing_m02(self, invalid_gerber_no_m02):
        """Test validation with missing M02"""
        validator = GerberValidator(strict_x3=True)
        tokens = list(tokenize_gerber(invalid_gerber_no_m02))
        
        is_valid = validator.validate(tokens)
        assert is_valid is False
        assert any('M02' in err.message for err in validator.errors)
    
    def test_missing_mo(self):
        """Test validation with missing MO"""
        gerber = """
%FSLAX24Y24*%
%ADD10C,1.0*%
D10*
X10000Y10000D03*
M02*
"""
        validator = GerberValidator(strict_x3=True)
        tokens = list(tokenize_gerber(gerber))
        
        is_valid = validator.validate(tokens)
        assert is_valid is False
        assert any('MO' in err.message or 'Units' in err.message for err in validator.errors)
    
    def test_non_strict_mode(self, invalid_gerber_no_m02):
        """Test validation in non-strict mode"""
        validator = GerberValidator(strict_x3=False)
        tokens = list(tokenize_gerber(invalid_gerber_no_m02))
        
        is_valid = validator.validate(tokens)
        # Should have warnings but not errors for M02
        assert len(validator.warnings) > 0
    
    def test_get_report_with_errors(self, invalid_gerber_no_fs):
        """Test error report generation"""
        validator = GerberValidator(strict_x3=True)
        tokens = list(tokenize_gerber(invalid_gerber_no_fs))
        
        validator.validate(tokens)
        report = validator.get_report()
        
        assert '❌' in report or 'ERROR' in report
        assert 'FS' in report or 'Format' in report
    
    def test_get_report_no_issues(self, simple_gerber):
        """Test report with no issues"""
        validator = GerberValidator(strict_x3=True)
        tokens = list(tokenize_gerber(simple_gerber))
        
        validator.validate(tokens)
        report = validator.get_report()
        
        assert '✅' in report or 'No validation issues' in report
    
    def test_multiple_errors(self):
        """Test validation with multiple errors"""
        gerber = """
%ADD10C,1.0*%
D10*
X10000Y10000D03*
"""
        validator = GerberValidator(strict_x3=True)
        tokens = list(tokenize_gerber(gerber))
        
        is_valid = validator.validate(tokens)
        assert is_valid is False
        # Should have errors for missing FS, MO, and M02
        assert len(validator.errors) >= 2
    
    def test_validation_clears_previous_results(self, simple_gerber, invalid_gerber_no_fs):
        """Test that validation clears previous results"""
        validator = GerberValidator(strict_x3=True)
        
        # First validation - valid
        tokens1 = list(tokenize_gerber(simple_gerber))
        validator.validate(tokens1)
        assert len(validator.errors) == 0
        
        # Second validation - invalid
        tokens2 = list(tokenize_gerber(invalid_gerber_no_fs))
        validator.validate(tokens2)
        assert len(validator.errors) > 0

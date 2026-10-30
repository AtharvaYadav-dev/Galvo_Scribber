import pytest
from gerbyx.tokenizer import tokenize_gerber

class TestTokenizer:
    def test_tokenize_simple_param(self):
        """Test tokenization of a simple parameter"""
        gerber = "%FSLAX24Y24*%"
        tokens = list(tokenize_gerber(gerber))

        assert len(tokens) == 1
        assert tokens[0] == ('param', 'FSLAX24Y24*')

    def test_tokenize_multiple_params(self):
        """Test tokenization of multiple parameters"""
        gerber = "%FSLAX24Y24*MOMM*%"
        tokens = list(tokenize_gerber(gerber))

        assert len(tokens) == 2
        assert tokens[0] == ('param', 'FSLAX24Y24*')
        assert tokens[1] == ('param', 'MOMM*')

    def test_tokenize_statement(self):
        """Test tokenization of statements"""
        gerber = "D10*X0Y0D03*"
        tokens = list(tokenize_gerber(gerber))

        assert len(tokens) == 2
        # Statements retain the asterisk
        assert tokens[0] == ('stmt', 'D10*')
        assert tokens[1] == ('stmt', 'X0Y0D03*')

    def test_tokenize_comment_g04(self):
        """Test tokenization of G04 comments"""
        gerber = "G04 This is a comment*"
        tokens = list(tokenize_gerber(gerber))

        assert len(tokens) == 1
        # Comments retain the asterisk
        assert tokens[0] == ('comment', 'G04 This is a comment*')

    def test_tokenize_hash_comment(self):
        """Test tokenization with # comments (X3) at start of line"""
        gerber = """
%FSLAX24Y24*%
# This is a comment
%MOMM*%
"""
        tokens = list(tokenize_gerber(gerber))

        # Comment line should be removed completely
        assert len(tokens) == 2
        assert tokens[0] == ('param', 'FSLAX24Y24*')
        assert tokens[1] == ('param', 'MOMM*')

    def test_tokenize_mixed_content(self):
        """Test mixed parameters and statements"""
        gerber = "%FSLAX24Y24*%D10*%MOMM*%"
        tokens = list(tokenize_gerber(gerber))

        assert len(tokens) == 3
        assert tokens[0] == ('param', 'FSLAX24Y24*')
        assert tokens[1] == ('stmt', 'D10*')
        assert tokens[2] == ('param', 'MOMM*')

    def test_tokenize_multiline_statement(self):
        """Test multiline statement"""
        gerber = """
        X0
        Y0
        D03*
        """
        tokens = list(tokenize_gerber(gerber))

        assert len(tokens) == 1
        # Tokenizer removes newlines but keeps spaces
        # Input has spaces before X0, Y0, D03
        # Expected: spaces are preserved
        token_val = tokens[0][1]
        assert 'X0' in token_val
        assert 'Y0' in token_val
        assert 'D03*' in token_val
        assert token_val.endswith('*')

    def test_tokenize_empty_string(self):
        """Test empty string"""
        gerber = ""
        tokens = list(tokenize_gerber(gerber))
        assert len(tokens) == 0

    def test_tokenize_whitespace_only(self):
        """Test whitespace only"""
        gerber = "   \n  \t  "
        tokens = list(tokenize_gerber(gerber))
        assert len(tokens) == 0

    def test_tokenize_unclosed_param_block(self):
        """Test unclosed parameter block (robustness)"""
        gerber = "%FSLAX24Y24*"
        tokens = list(tokenize_gerber(gerber))

        # Should parse what it can
        assert len(tokens) == 1
        assert tokens[0] == ('param', 'FSLAX24Y24*')

    def test_tokenize_macro_definition(self):
        """Test macro definition tokenization"""
        gerber = """
        %AMRECT*
        21,1,1.0,1.0,0,0,0*
        %
        """
        tokens = list(tokenize_gerber(gerber))

        # AMRECT is a param command inside %...%
        # The body is part of the param block content
        # It should yield params
        assert len(tokens) >= 1
        assert tokens[0][0] == 'param'
        assert 'AMRECT' in tokens[0][1]

    def test_tokenize_preserves_asterisks(self):
        """Test that asterisks are preserved in params"""
        gerber = "%FSLAX24Y24*%"
        tokens = list(tokenize_gerber(gerber))

        assert tokens[0][1].endswith('*')

    def test_tokenize_inline_comment_after_command(self):
        """Test inline comment handling (not removed by pre-processor but parsed later)"""
        # Note: # comments are only removed at start of line now to protect G04
        gerber = "D10* # Comment"
        tokens = list(tokenize_gerber(gerber))

        # Should contain stmt 'D10*' and then maybe junk '# Comment'
        assert tokens[0] == ('stmt', 'D10*')

        # The '# Comment' might be yielded as stmt or ignored if no *
        # If it doesn't end with *, tokenizer might yield it as stmt at EOF
        if len(tokens) > 1:
            assert tokens[1][0] == 'stmt'
            assert '#' in tokens[1][1]

"""Validatore per Gerber X3"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationError:
    """Rappresenta un errore di validazione"""
    severity: str  # 'error', 'warning'
    message: str
    line: Optional[int] = None


class GerberValidator:
    """Valida file Gerber secondo lo standard X3"""
    
    def __init__(self, strict_x3: bool = False):
        self.strict_x3 = strict_x3
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        
    def validate(self, tokens: List[tuple]) -> bool:
        """
        Valida una lista di token Gerber.
        Ritorna True se valido, False altrimenti.
        """
        self.errors.clear()
        self.warnings.clear()
        
        has_fs = False
        has_mo = False
        has_m02 = False
        first_command_seen = False
        
        for i, (kind, value) in enumerate(tokens):
            # Ignora commenti
            if kind == 'comment':
                continue
            
            # Verifica che FS e MO siano all'inizio
            if not first_command_seen:
                if kind == 'param':
                    if value.startswith('FS'):
                        has_fs = True
                    elif value.startswith('MO'):
                        has_mo = True
                    elif not value.startswith('TF'):
                        # Primo comando che non è FS, MO o TF
                        if not has_fs:
                            self._add_error(f"FS (Format Specification) must be defined before other commands", i)
                        if not has_mo:
                            self._add_error(f"MO (Units) must be defined before other commands", i)
                        first_command_seen = True
            
            # Verifica M02 alla fine
            if kind == 'param' or kind == 'stmt':
                if 'M02' in value:
                    has_m02 = True
        
        # Validazioni finali
        if not has_fs:
            self._add_error("Missing FS (Format Specification) - required in X3")
        
        if not has_mo:
            self._add_error("Missing MO (Units) - required in X3")
        
        if self.strict_x3 and not has_m02:
            self._add_error("Missing M02 (End of File) - mandatory in X3")
        elif not has_m02:
            self._add_warning("Missing M02 (End of File) - recommended in X3")
        
        return len(self.errors) == 0
    
    def _add_error(self, message: str, line: Optional[int] = None):
        """Aggiunge un errore"""
        self.errors.append(ValidationError('error', message, line))
    
    def _add_warning(self, message: str, line: Optional[int] = None):
        """Aggiunge un warning"""
        self.warnings.append(ValidationError('warning', message, line))
    
    def get_report(self) -> str:
        """Genera un report testuale degli errori e warning"""
        lines = []
        
        if self.errors:
            lines.append("❌ ERRORS:")
            for err in self.errors:
                if err.line is not None:
                    lines.append(f"  Line {err.line}: {err.message}")
                else:
                    lines.append(f"  {err.message}")
        
        if self.warnings:
            lines.append("\n⚠️  WARNINGS:")
            for warn in self.warnings:
                if warn.line is not None:
                    lines.append(f"  Line {warn.line}: {warn.message}")
                else:
                    lines.append(f"  {warn.message}")
        
        if not self.errors and not self.warnings:
            lines.append("✅ No validation issues found")
        
        return "\n".join(lines)

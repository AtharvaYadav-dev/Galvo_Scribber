from typing import Generator, Tuple
from .logger import debug, is_debug_enabled


def tokenize_gerber(text: str) -> Generator[Tuple[str, str], None, None]:
    """
    Tokenizza un file Gerber in modo robusto.

    Itera attraverso il testo cercando i delimitatori di comando ('*' e '%').

    Restituisce un generatore di tuple (tipo, valore) dove:
    - 'param': Un comando all'interno di un blocco di parametri estesi (es. 'FSLAX24Y24*').
    - 'stmt': Un comando standard del corpo del file (es. 'G01*', 'X100Y100D02*').
    - 'comment': Un commento G04 (es. 'G04 Questo è un commento*').
    """
    debug(lambda: f"Tokenizing Gerber file ({len(text)} bytes)")
    # Pre-processing: rimuovi commenti # (X3)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # X3: Le righe che iniziano con # sono commenti.
        # Rimuoviamole interamente.
        if line.lstrip().startswith('#'):
            line = ""
        # NOTA: Non rimuoviamo commenti inline con # (es. "X100#comment") in questo modo grezzo
        # perché romperebbe i comandi G04 di KiCad (es. "G04 #@! TF...*") rimuovendo l'asterisco finale.

        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    pos = 0
    text_len = len(text)

    while pos < text_len:
        # Salta whitespace
        while pos < text_len and text[pos].isspace():
            pos += 1

        if pos >= text_len:
            break

        # Controlla se siamo all'inizio di un blocco di parametri
        if text[pos] == '%':
            # Trovato un blocco di parametri. Cerca la fine del blocco.
            end_percent_pos = text.find('%', pos + 1)
            if end_percent_pos == -1:
                # Blocco non chiuso, errore. Per robustezza, lo trattiamo come un blocco fino alla fine.
                end_percent_pos = text_len

            # Il contenuto del blocco è tra i due '%'
            param_content = text[pos + 1 : end_percent_pos]

            # All'interno del blocco, i comandi sono separati da '*'
            # Li emettiamo come token 'param'
            # Attenzione: le macro (AM) possono avere più comandi interni.
            # Lo standard dice che i comandi estesi terminano con *.
            # Quindi splittiamo per * e ignoriamo le parti vuote.

            # Nota: split('*') rimuove i delimitatori, ma noi vogliamo mantenerli per coerenza
            # con il resto del parser che si aspetta comandi terminati da *.

            # Esempio: "FSLAX24Y24*MOMM*" -> ["FSLAX24Y24", "MOMM", ""]
            parts = param_content.split('*')
            for part in parts:
                cmd = part.strip()
                if cmd:
                    # Aggiungiamo l'asterisco che è stato rimosso dallo split
                    yield ('param', cmd + '*')

            # Avanza il puntatore principale alla fine del blocco %...%
            pos = end_percent_pos + 1

        else:
            # Non è un blocco di parametri, quindi è uno statement normale che finisce con '*'
            star_pos = text.find('*', pos)
            if star_pos == -1:
                # Statement non terminato, prendiamo il resto del file
                stmt = text[pos:].strip()
                if stmt:
                    # Potrebbe essere un G04
                    if stmt.startswith('G04'):
                        yield ('comment', stmt)
                    else:
                        yield ('stmt', stmt)
                break # Finito
            else:
                stmt = text[pos : star_pos + 1].strip()

                # Rimuoviamo newline interni che possono spezzare comandi lunghi
                stmt = stmt.replace('\n', '').replace('\r', '')

                if stmt:
                    if stmt.startswith('G04'):
                        yield ('comment', stmt)
                    else:
                        yield ('stmt', stmt)

                # Avanza il puntatore principale alla fine dello statement
                pos = star_pos + 1

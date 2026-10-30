import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PySide6.QtGui import QFontDatabase, QGuiApplication

app = QGuiApplication.instance() or QGuiApplication(sys.argv)
fams = QFontDatabase.families()
marathi_like = [f for f in fams if any(k in f.lower() for k in ["marathi", "mangal", "dev", "nirmala", "shree", "kruti", "shivaji", "apsara", "kiran", "chanakya", "kokila", "aparajita", "utsaah"])]
print("Marathi-related fonts found:", marathi_like)


# core/styles.py
# Centralized stylesheet constants for UI elements

VIDEO_LABEL_STYLE = "background-color: black; color: white; font-size: 20px;"

CENTER_MENU_BTN_ACTIVE = "background-color: rgb(16, 42, 131);"

BTN_DANGER = """
QPushButton {
    color: rgb(255, 255, 255);
    background-color: rgb(200, 0, 0);
    border-color: transparent;
    border-style: outset;
    border-radius: 20px;
    border-width: 2px;
    padding: 6px;
}
"""

BTN_PRIMARY = """
QPushButton {
    color: rgb(255, 255, 255);
    background-color: rgb(16, 42, 131);
    border-color: transparent;
    border-style: outset;
    border-radius: 20px;
    border-width: 2px;
    padding: 6px;
}
"""

REDDOT_BTN_ACTIVE = """
background-color: rgb(200, 0, 0);
color: rgb(255, 255, 255);
border-color: transparent;
border-style: outset;
border-radius: 15px;
border-width: 2px;
padding: 6px;
"""

REDDOT_BTN_INACTIVE = """
background-color: rgb(16, 42, 131);
color: rgb(255, 255, 255);
border-color: transparent;
border-style: outset;
border-radius: 15px;
border-width: 2px;
padding: 6px;
"""

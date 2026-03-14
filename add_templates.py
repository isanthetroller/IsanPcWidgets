import re
with open("pickers.py", "r", encoding="utf-8") as f:
    text = f.read()

# I want to add some rainmeter specific templates
NEW_TEMPLATES = """
    "rainmeter_modern": {
        "name": "Modern Rain",
        "desc": "Sleek combination of numbers and text",
        "day_fmt": "dddd",
        "date_fmt": "MMM d",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "time_top",
    },
    "rainmeter_sidebar": {
        "name": "Sidebar Stack",
        "desc": "All elements stacked neatly",
        "day_fmt": "ddd",
        "date_fmt": "d / M / yyyy",
        "time_fmt": "h:mm:ss a",
        "day_transform": "none",
        "date_transform": "none",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": True,
        "show_ampm": False,
        "layout": "vertical",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "desc": "Glitchy styled dense data",
        "day_fmt": "ddd",
        "date_fmt": "yyyy-MM-dd",
        "time_fmt": "HH:mm:ss",
        "day_transform": "upper",
        "date_transform": "none",
        "time_prefix": "[ ",
        "time_suffix": " ]",
        "show_seconds": True,
        "show_ampm": False,
        "layout": "time_top",
    },
"""

# Insert right after "compact" / or at the beginning of DATETIME_TEMPLATES
text = text.replace('DATETIME_TEMPLATES = {', 'DATETIME_TEMPLATES = {\n' + NEW_TEMPLATES)

with open("pickers.py", "w", encoding="utf-8") as f:
    f.write(text)

import re
with open("themes.py", "r", encoding="utf-8") as f:
    text = f.read()

# Make the standard padding wider, make backgrounds softer, make shadows natural
text = text.replace("rgba(0, 105, 62, 235)", "rgba(0, 105, 62, 160)")
text = text.replace("rgba(12, 12, 40, 240)", "rgba(12, 12, 40, 180)")
text = text.replace("rgba(10, 10, 15, 240)", "rgba(10, 10, 15, 180)")
text = text.replace("rgba(60, 20, 40, 235)", "rgba(60, 20, 40, 180)")
text = text.replace("rgba(0, 0, 0, 245)", "rgba(0, 0, 0, 150)")
text = text.replace("rgba(255, 255, 255, 30)", "rgba(255, 255, 255, 20)")

# Make border generally transparent to look like modern borderless or 1px subtle edges
text = re.sub(r'border: 1px solid \{t\[\'border\'\]\};', r'''border: 1px solid {t['border']};
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['bg']}, stop:1 rgba(0,0,0,80));''', text)

with open("themes.py", "w", encoding="utf-8") as f:
    f.write(text)

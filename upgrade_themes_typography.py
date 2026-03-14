import re
with open("themes.py", "r", encoding="utf-8") as f:
    text = f.read()

# Make sure day stands out more, like Rainmeter style headers.
# I'll update the font weights and sizes in the stylesheet.
text = text.replace('font-size: {s(42)}px;\n            font-weight: bold;\n            color: {t[\'fg\']};', 
                    '''font-size: {s(48)}px;
            font-weight: 800; /* Extra bold */
            letter-spacing: {sp(2)}px;
            color: {t['fg']};''')

# Date
text = text.replace('font-size: {s(18)}px;\n            color: {t[\'dim\']};',
                    '''font-size: {s(16)}px;
            font-weight: 300; /* Light */
            letter-spacing: {sp(4)}px;
            text-transform: uppercase;
            color: {t['dim']};''')

# Time
text = text.replace('font-size: {s(20)}px;\n            color: {t[\'accent\']};',
                    '''font-size: {s(24)}px;
            font-weight: 600;
            color: {t['accent']};''')

# Clock Sec
text = text.replace('font-size: {s(22)}px;\n            color: {t[\'accent\']};\n            letter-spacing: {sp(2)}px;', 
                    '''font-size: {s(22)}px;
            font-weight: 300;
            color: {t['accent']};
            letter-spacing: {sp(2)}px;''')

with open("themes.py", "w", encoding="utf-8") as f:
    f.write(text)

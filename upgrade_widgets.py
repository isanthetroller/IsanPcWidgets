import re
with open("widgets.py", "r", encoding="utf-8") as f:
    text = f.read()


# Step 1: dynamic reorder in DateTimeWidget _update
update_method_old = """        if m != self._cached_minute:
            self._cached_minute = m
            # Day string"""

update_method_new = """        if m != self._cached_minute:
            self._cached_minute = m

            # Re-order widgets dynamically to create completely different vibes
            for i in reversed(range(self.content_layout.count())): 
                self.content_layout.itemAt(i).widget().setParent(None)
            
            if t.get("layout") == "time_top":
                self.content_layout.addWidget(self.time_label)
                self.content_layout.addWidget(self.day_label)
                self.content_layout.addWidget(self.date_label)
            else:
                self.content_layout.addWidget(self.day_label)
                self.content_layout.addWidget(self.date_label)
                self.content_layout.addWidget(self.time_label)

            # Day string"""

text = text.replace(update_method_old, update_method_new)

# Step 2: Ensure the margins scale better in BaseWidget
text = text.replace('self.content_layout.setContentsMargins(24, 18, 24, 18)', 'self.content_layout.setContentsMargins(35, 25, 35, 25)')


with open("widgets.py", "w", encoding="utf-8") as f:
    f.write(text)

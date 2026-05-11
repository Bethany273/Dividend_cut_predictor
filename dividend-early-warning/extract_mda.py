# simplest_extract.py
import re

with open("disney_10q_2020-08-04.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Find where Item 2 is
item2_pos = text.lower().find("item 2:")
print(f"'Item 2:' found at position: {item2_pos}")

# Find where Item 3 is (end of MD&A)
item3_pos = text.lower().find("item 3.", item2_pos + 100)
print(f"'Item 3.' found at position: {item3_pos}")

# Go back 200 characters from Item 2 to catch the full header
start = max(0, item2_pos - 200)
end = item3_pos if item3_pos > 0 else item2_pos + 50000

mda = text[start:end]

# Save it
with open("disney_10q_2020-08-04_MDA.txt", "w", encoding="utf-8") as f:
    f.write(mda)

print(f"\n✓ Extracted {len(mda):,} characters")
print(f"  From position {start} to {end}")

print("\n--- FIRST 400 CHARACTERS ---")
print(mda[:400])
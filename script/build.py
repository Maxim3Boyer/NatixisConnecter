import json
import os
import csv

INPUT_FILE = "data/funds.json"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for instrument in data:
    label = instrument["label"].replace(" ", "_").replace("/", "_")
    history = instrument.get("history", [])

    filename = f"{OUTPUT_DIR}/{label}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Close"])

        for h in history:
            date = h["date"]
            value = h["amount"]["value"]
            writer.writerow([date, value])

    print(f"Generated {filename}")

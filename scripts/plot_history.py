import sys

import json
import pandas as pd
# from pathlib import Path
import matplotlib.pyplot as plt

if len(sys.argv) == 1:
    history_file = "history.json"
    out_file = "history.pdf"
elif len(sys.argv) == 2:
    history_file = sys.argv[1]
    out_file = history_file.replace(".json", ".pdf")
elif len(sys.argv) == 3:
    history_file = sys.argv[1]
    out_file = sys.arvg[2]

# Load the historical data
df = pd.read_json(history_file)

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Optional: sort by timestamp
df = df.sort_values("timestamp")

# Create figure
plt.figure(figsize=(10,6))

# Plot MIPS vs timestamp for each program
for prog, group in df.groupby("prog"):
    plt.plot(group["timestamp"], group["mips"], marker="o", label=prog)

# Labels, title, legend, grid
plt.xlabel("Time")
plt.ylabel("MIPS")
plt.title("Performance Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save to PDF
plt.savefig(out_file)

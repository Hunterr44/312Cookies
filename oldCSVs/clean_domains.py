import pandas as pd

# Step 1: Read raw text and clean it
with open("download.csv", "r", encoding="utf-8") as f:
    raw_lines = f.readlines()

# Step 2: Remove leading/trailing quotes and fix internal quotes
cleaned_lines = []
for line in raw_lines:
    line = line.strip()
    if line.startswith('""') and line.endswith('""'):
        line = line[2:-2]  # remove outer double-double quotes
    line = line.replace('""', '"')  # reduce escaped quotes
    cleaned_lines.append(line)

# Step 3: Write to a new temporary CSV
with open("cleaned.csv", "w", encoding="utf-8") as f:
    f.write("\n".join(cleaned_lines))

# Step 4: Load with pandas
df = pd.read_csv("cleaned.csv")

# Show and extract domains
print(df.columns)
print(df.head())
domains = df["Root Domain"].dropna().tolist()
print(domains[:10])

import pandas as pd
from pathlib import Path

# =========================================================
# AGRILINK AI - HISTORICAL MARKET DATA ANALYSIS
# =========================================================

file_path = Path("data/2023/lucknowdata3.csv")

print("=" * 70)
print("AGRILINK AI - HISTORICAL MARKET DATA ANALYSIS")
print("=" * 70)

# Read dataset
df = pd.read_csv(file_path)

print("\nDataset found:")
print(file_path)

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\n" + "=" * 70)
print("FIRST 10 ROWS")
print("=" * 70)
print(df.head(10).to_string())

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)
print(df.isnull().sum())

print("\n" + "=" * 70)
print("ROWS WITH ACTUAL PRICE DATA")
print("=" * 70)

# Remove rows where Modal Price is missing
clean_df = df.dropna(subset=["Modal Price"]).copy()

print("\nValid rows:", len(clean_df))

print("\nFirst 10 valid rows:")
print(clean_df.head(10).to_string())

print("\n" + "=" * 70)
print("LAST 10 VALID ROWS")
print("=" * 70)
print(clean_df.tail(10).to_string())

print("\n" + "=" * 70)
print("PRICE STATISTICS")
print("=" * 70)

print(clean_df[
    ["Retail Prices", "Min Price", "Max Price", "Modal Price"]
].describe())

print("\n" + "=" * 70)
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 70)
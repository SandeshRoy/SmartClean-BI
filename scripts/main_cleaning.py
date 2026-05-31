import pandas as pd
import numpy as np
import os

# Folder containing raw CSV files
raw_folder = "../data/raw"

# Store all dataframes
all_data = []

# Read all CSV files
for file in os.listdir(raw_folder):

    if file.endswith(".csv"):

        file_path = os.path.join(raw_folder, file)

        try:
            df = pd.read_csv(file_path)

            # Add category column from filename
            category_name = file.replace(".csv", "")
            df["Category"] = category_name

            all_data.append(df)

            print(f"Loaded: {file}")

        except Exception as e:
            print(f"Error loading {file}: {e}")

# Combine datasets
combined_df = pd.concat(all_data, ignore_index=True)

print("\nTotal Rows Before Cleaning:", len(combined_df))

# Remove duplicates
combined_df.drop_duplicates(inplace=True)

print("Rows After Removing Duplicates:", len(combined_df))

# -------------------------
# CLEAN PRICE COLUMNS
# -------------------------

price_columns = ["actual_price", "discount_price"]

for col in price_columns:

    if col in combined_df.columns:

        combined_df[col] = (
            combined_df[col]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        combined_df[col] = pd.to_numeric(
            combined_df[col],
            errors="coerce"
        )

# -------------------------
# CLEAN RATINGS
# -------------------------

if "ratings" in combined_df.columns:

    combined_df["ratings"] = pd.to_numeric(
        combined_df["ratings"],
        errors="coerce"
    )

# -------------------------
# CLEAN NUMBER OF RATINGS
# -------------------------

if "no_of_ratings" in combined_df.columns:

    combined_df["no_of_ratings"] = (
        combined_df["no_of_ratings"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)")[0]
    )

    combined_df["no_of_ratings"] = pd.to_numeric(
        combined_df["no_of_ratings"],
        errors="coerce"
    )

# -------------------------
# HANDLE MISSING VALUES
# -------------------------

for col in combined_df.columns:

    if combined_df[col].dtype == "object":

        combined_df[col] = combined_df[col].fillna("Unknown")

        combined_df[col] = (
            combined_df[col]
            .astype(str)
            .str.strip()
            .str.title()
        )

    else:

        combined_df[col] = combined_df[col].fillna(
            combined_df[col].mean()
        )

# -------------------------
# SAMPLE FOR POWER BI
# -------------------------

if len(combined_df) > 100000:

    combined_df = combined_df.sample(
        100000,
        random_state=42
    )

print("Rows After Sampling:", len(combined_df))

# -------------------------
# CREATE OUTPUT FOLDERS
# -------------------------

os.makedirs("../data/cleaned", exist_ok=True)
os.makedirs("../reports", exist_ok=True)

# -------------------------
# SAVE CLEANED DATASET
# -------------------------

output_path = "../data/cleaned/amazon_cleaned_data.csv"

combined_df.to_csv(
    output_path,
    index=False
)

# -------------------------
# GENERATE REPORT
# -------------------------

report = f"""
DATA CLEANING REPORT
========================

Files Processed : {len(all_data)}
Final Rows      : {len(combined_df)}
Total Columns   : {len(combined_df.columns)}

Cleaning Steps:
- Merged multiple CSV files
- Removed duplicates
- Cleaned actual_price
- Cleaned discount_price
- Cleaned ratings
- Cleaned no_of_ratings
- Filled missing values
- Standardized text fields
- Sampled 100000 rows for Power BI

Output File:
{output_path}
"""

with open("../reports/report.txt", "w") as file:
    file.write(report)

print("\nCleaning Completed Successfully!")
print(report)
print(f"Dataset saved to: {output_path}")
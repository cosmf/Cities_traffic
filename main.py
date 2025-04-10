import pandas as pd

# 1. Load the CSV file (make sure it's in the same folder as this script)
df = pd.read_csv("futuristic_city_traffic.csv")

# 2. Check for missing values
missing = df.isnull().sum()
print("Missing values per column:\n", missing)

# 3. Drop rows with any missing value
df_clean = df.dropna()
print(f"\nAfter dropping rows with missing values: {df.shape[0]} → {df_clean.shape[0]} rows")

# 4. Remove unrealistic vehicle types (e.g., 'Flying Car')
initial_count = df_clean.shape[0]
df_clean = df_clean[df_clean["Vehicle Type"] != "Flying Car"]
print(f"After removing 'Flying Car' entries: {initial_count} → {df_clean.shape[0]} rows")

# 5. (Optional) Save the cleaned dataset for further analysis
df_clean.to_csv("traffic_data_cleaned.csv", index=False)
print("Cleaned data saved as 'traffic_data_cleaned.csv'")

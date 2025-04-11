import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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

# 5. Define correct order for days of the week
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df_clean["Day Of Week"] = pd.Categorical(df_clean["Day Of Week"], categories=days_order, ordered=True)

# 6. Sort by day of the week and hour
df_clean = df_clean.sort_values(by=["Day Of Week", "Hour Of Day"]).reset_index(drop=True)

# 7. Create a new column: DayHour (e.g., Monday_08)
df_clean["DayHour"] = df_clean["Day Of Week"].astype(str) + "_" + df_clean["Hour Of Day"].apply(lambda x: f"{x:02d}")

# 8. Save cleaned and sorted data
df_clean.to_csv("traffic_data_cleaned.csv", index=False)
print("Cleaned and sorted data with 'DayHour' column saved as 'traffic_data_cleaned.csv'")

# -----------------------
# AGGREGATIONS / ANALYSIS
# -----------------------

# Aggregation by Day Of Week
if 'Day Of Week' in df_clean.columns:
    day_summary = df_clean.groupby('Day Of Week').agg({
        'Speed': ['mean', 'max', 'min'],
        'Traffic Density': ['mean', 'sum']
    })
    print("\nDay Of Week Summary (Speed and Traffic Density):")
    print(day_summary)

# Aggregation by Is Peak Hour
if 'Is Peak Hour' in df_clean.columns:
    peak_summary = df_clean.groupby('Is Peak Hour').agg({
        'Speed': ['mean', 'max', 'min'],
        'Energy Consumption': 'mean',
        'Traffic Density': 'mean'
    })
    print("\nPeak Hour Summary (Speed, Energy Consumption, Traffic Density):")
    print(peak_summary)

# Aggregation by Weather
if 'Weather' in df_clean.columns and 'Speed' in df_clean.columns:
    weather_summary = df_clean.groupby('Weather').agg({
        'Speed': ['mean', 'max', 'min'],
        'Traffic Density': 'mean'
    })
    print("\nWeather Summary (Speed and Traffic Density):")
    print(weather_summary)

# Aggregation by Economic Condition
if 'Economic Condition' in df_clean.columns:
    econ_summary = df_clean.groupby('Economic Condition').agg({
        'Speed': ['mean', 'max', 'min'],
        'Traffic Density': 'mean',
        'Energy Consumption': 'mean'
    })
    print("\nEconomic Condition Summary (Speed, Traffic Density, Energy Consumption):")
    print(econ_summary)

avg_speed_by_hour = df_clean.groupby('DayHour')['Speed'].mean().reset_index()
print(avg_speed_by_hour)

# -----------------------
# Bar Plot with Custom Labels (Only Days)
# -----------------------

plt.figure(figsize=(10, 6))
ax = sns.barplot(data=avg_speed_by_hour, x='DayHour', y='Speed', palette='viridis')
plt.title('Average Traffic Speed by Hour')
plt.xlabel('Hour of Day')
plt.ylabel('Average Speed (km/h)')

# Create a new column with only the day extracted from 'DayHour'
avg_speed_by_hour['Day'] = avg_speed_by_hour['DayHour'].apply(lambda x: x.split('_')[0])

# Generate custom tick labels:
# For each row, only the first occurrence of a day gets a label.
custom_labels = []
seen_days = set()
for day in avg_speed_by_hour['Day']:
    if day not in seen_days:
        custom_labels.append(day)
        seen_days.add(day)
    else:
        custom_labels.append('')

# Set the x-ticks manually. Since the x-axis is categorical,
# we use a range equal to the number of entries in avg_speed_by_hour.
plt.xticks(ticks=range(len(avg_speed_by_hour)), labels=custom_labels, rotation=45)
plt.ylim(55,65)
plt.grid(True)
plt.tight_layout()
plt.show()


coefficients = np.polyfit(df_clean['Energy Consumption'], df_clean['Speed'], 1)
polynomial = np.poly1d(coefficients)
x_values = np.linspace(df_clean['Energy Consumption'].min(), df_clean['Energy Consumption'].max(), 100)
y_values = polynomial(x_values)
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_clean, x='Speed', y='Energy Consumption', hue='Vehicle Type', alpha=0.7)
plt.plot(x_values, y_values, color='red', linestyle='--', linewidth=2)
plt.title('Speed vs Energy Consumption')

plt.xlabel('Speed (km/h)')
plt.ylabel('Energy Consumption (e.g., kWh/100km)')
plt.grid(True)
plt.show()

# sns.lmplot(
#     data=df_clean,
#     x='Speed',
#     y='Energy Consumption',
#     hue='Vehicle Type',
#     height=6,
#     aspect=1.5,
#     scatter_kws={'alpha': 0.6}
# )

# plt.title('Speed vs Energy Consumption by Vehicle')
# plt.xlabel('Speed (km/h)')
# plt.ylabel('Energy Consumption')
# plt.grid(True)
# plt.tight_layout()
# plt.show()

custom_palette = sns.color_palette("tab10", n_colors=df_clean['Vehicle Type'].nunique())

# Map the palette to vehicle types
vehicle_order = df_clean['Vehicle Type'].unique()
palette_dict = dict(zip(vehicle_order, custom_palette))

# Create lmplot
sns.lmplot(
    data=df_clean,
    x='Speed',
    y='Energy Consumption',
    hue='Vehicle Type',
    palette=palette_dict,              # Custom colors for each vehicle type
    height=6,
    aspect=1.5,
    markers='o',
    scatter_kws={'alpha': 0.6, 's': 40},  # Optional: smaller dots
    line_kws={'linestyle': '--', 'linewidth': 2}  # Dashed lines
)

plt.title('Speed vs Energy Consumption by Vehicle')
plt.xlabel('Speed (km/h)')
plt.ylabel('Energy Consumption')
plt.grid(True)
plt.tight_layout()
plt.show()
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a backend that doesn't need a display
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the CSV file
df = pd.read_csv("archive/futuristic_city_traffic.csv")

# Check for missing values
missing = df.isnull().sum()
print("Missing values per column:\n", missing)

# Drop rows with any missing value
df_clean = df.dropna()
print(f"\nAfter dropping rows with missing values: {df.shape[0]} → {df_clean.shape[0]} rows")

# Remove unrealistic vehicle types (e.g., 'Flying Car')
initial_count = df_clean.shape[0]
df_clean = df_clean[df_clean["Vehicle Type"] != "Flying Car"]
print(f"After removing 'Flying Car' entries: {initial_count} → {df_clean.shape[0]} rows")

# Define correct order for days of the week
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df_clean["Day Of Week"] = pd.Categorical(df_clean["Day Of Week"], categories=days_order, ordered=True)

# Sort by day of the week and hour
df_clean = df_clean.sort_values(by=["Day Of Week", "Hour Of Day"]).reset_index(drop=True)

# Create a new column: DayHour (e.g., Monday_08)
df_clean["DayHour"] = df_clean["Day Of Week"].astype(str) + "_" + df_clean["Hour Of Day"].apply(lambda x: f"{x:02d}")

# Save cleaned and sorted data
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


# Define proper day order
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# # Create a new column with only the day extracted from 'DayHour'
# avg_speed_by_hour['Day'] = avg_speed_by_hour['DayHour'].apply(lambda x: x.split('_')[0])

# Ensure 'Day' column is a categorical type with defined order
avg_speed_by_hour['Day'] = pd.Categorical(avg_speed_by_hour['Day'], categories=day_order, ordered=True)

# Sort by Day and then Hour (optional if you want hourly trend too)
avg_speed_by_hour_sorted = avg_speed_by_hour.sort_values(by=['Day', 'Hour']).reset_index(drop=True)


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



plt.figure(figsize=(12, 6))
plt.plot(avg_speed_by_hour_sorted['Speed'], marker='o')  # Assuming you want a line plot of Speed
plt.xticks(ticks=range(len(avg_speed_by_hour_sorted)), labels=custom_labels, rotation=45)
plt.ylim(55, 65)
plt.xlabel("Day of Week")
plt.ylabel("Average Speed (km/h)")
plt.title("Average Traffic Speed by Hour (Sorted by Day)")
plt.grid(True)
plt.tight_layout()
plt.show()

# -----------------------
# Set the x-ticks manually. Since the x-axis is categorical,
# we use a range equal to the number of entries in avg_speed_by_hour.
# plt.xticks(ticks=range(len(avg_speed_by_hour)), labels=custom_labels, rotation=45)
# plt.ylim(55,65)
# plt.grid(True)
# plt.tight_layout()
# plt.show()
# -----------------------

coefficients = np.polyfit(df['Energy Consumption'], df['Speed'], 1)
polynomial = np.poly1d(coefficients)
x_values = np.linspace(df['Energy Consumption'].min(), df['Energy Consumption'].max(), 100)
y_values = polynomial(x_values)
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_clean, x='Speed', y='Energy Consumption', alpha=0.7)
plt.plot(x_values, y_values, color='red', linestyle='--', linewidth=2)
plt.title('Speed vs Energy Consumption')

plt.xlabel('Speed (km/h)')
plt.ylabel('Energy Consumption (e.g., kWh/100km)')
plt.grid(True)
plt.show()


# Assuming you’ve already cleaned your df into df_clean

def assign_time_of_day(hour):
    if hour < 6:
        return 'Early Morning'
    elif hour < 12:
        return 'Morning'
    elif hour < 18:
        return 'Afternoon'
    else:
        return 'Evening/Night'

df_clean['TimeOfDayBucket'] = df_clean['Hour Of Day'].apply(assign_time_of_day)

plt.figure(figsize=(8, 6))
sns.boxplot(
    data=df_clean, 
    x='TimeOfDayBucket', 
    y='Speed', 
    palette='coolwarm'
)
plt.title('Distribution of Speed Across 4 Time-of-Day Buckets')
plt.xlabel('Time of Day')
plt.ylabel('Speed (km/h)')
plt.grid(True)
plt.tight_layout()
plt.show()

# --------------------------
# STEP 1: Define Baseline Consumption by Weather
# --------------------------
# Scale mentioned in your prompt:
#   - Clear = 2
#   - Electromagnetic Storm = 6
#   - Rainy Weather = 5
#   - Snowy = 8.5
#   - Solar Flare = 8
weather_base = {
    "Clear": 2,
    "Electromagnetic Storm": 6,
    "Rainy Weather": 5,
    "Snowy": 8.5,
    "Solar Flare": 8
}

# --------------------------
# STEP 2: Define Offsets by Holiday
# --------------------------
# Christmas and Halloween get bigger offsets because of decorations,
# Thanksgiving also higher (lots of cooking/guests), etc.
holiday_offsets = {
    "New Year's Day": 1.0, 
    "Valentine's Day": 1.0,
    "Easter": 0.5,
    "Independence Day": 1.0,
    "Labor Day": 1.0,
    "Halloween": 2.0,
    "Thanksgiving": 2.5,
    "Christmas": 3.0
}

holidays_in_order = [
    "New Year's Day", 
    "Valentine's Day", 
    "Easter", 
    "Independence Day", 
    "Labor Day", 
    "Halloween", 
    "Thanksgiving", 
    "Christmas"
]

weather_in_order = [
    "Clear", 
    "Electromagnetic Storm", 
    "Rainy Weather", 
    "Snowy", 
    "Solar Flare"
]

# --------------------------
# STEP 3: Build a Realistic Holiday–Weather Table
# --------------------------
data_rows = []
np.random.seed(42)  # Make results reproducible
for holiday in holidays_in_order:
    row_vals = {}
    for w in weather_in_order:
        # Base + holiday offset + small random noise
        mean_val = weather_base[w] + holiday_offsets[holiday]
        # e.g. add a random normal(0, 0.2) to get variation in tenths
        val = mean_val + np.random.normal(0, 0.2)  
        row_vals[w] = round(val, 1)
    data_rows.append([holiday] + [row_vals[w] for w in weather_in_order])

columns = ["Holiday"] + weather_in_order
df_holiday_weather = pd.DataFrame(data_rows, columns=columns)
df_holiday_weather.set_index("Holiday", inplace=True)

print("Realistic Average Energy Consumption (kWh/100km or similar) by Holiday and Weather:\n")
print(df_holiday_weather)

# --------------------------
# STEP 4: Create a Heatmap
# --------------------------
plt.figure(figsize=(10, 6))
sns.heatmap(df_holiday_weather, annot=True, cmap="coolwarm", fmt=".1f")
plt.title("Average Energy Consumption by Holiday and Weather (Realistic Example)")
plt.xlabel("Weather Condition")
plt.ylabel("Holiday")
plt.tight_layout()
plt.show()

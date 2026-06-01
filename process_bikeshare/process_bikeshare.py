import pandas as pd
import numpy as np
import requests
from datetime import datetime
from pathlib import Path

import holidays


def load_raw_data(file_path):
    """
    Loads the raw Capital Bikeshare trip data (Dataset A).
    """
    print(f"Loading data from {file_path}...")
    # Parsing dates on load for efficiency
    df = pd.read_csv(file_path, parse_dates=['started_at', 'ended_at'])
    return df

def aggregate_trips_hourly(df):
    """
    Groups raw trip logs by hour and counts casual/member trips.
    """
    print("Aggregating trips into hourly buckets...")
    
    # 1. Temporal Aggregation
    # Ensure started_at is datetime
    df['started_at'] = pd.to_datetime(df['started_at'])
    
    # Floor to the start of the hour
    df['hour_bin'] = df['started_at'].dt.floor('H')
    
    # Count by hour and member type
    # We group by the floored hour and the member_casual status
    counts = df.groupby(['hour_bin', 'member_casual']).size().unstack(fill_value=0)
    
    # Ensure columns exist even if one type is missing in the slice
    if 'casual' not in counts.columns:
        counts['casual'] = 0
    if 'member' not in counts.columns:
        counts['member'] = 0
        
    counts = counts.rename(columns={'member': 'registered'})
    
    # Create the baseline continuous hourly range
    start_time = df['hour_bin'].min()
    end_time = df['hour_bin'].max()
    full_range = pd.date_range(start=start_time, end=end_time, freq='h')
    
    # Reindex to include hours with zero trips
    hourly_df = counts.reindex(full_range, fill_value=0)
    hourly_df.index.name = 'datetime'
    
    # Calculate total count
    hourly_df['cnt'] = hourly_df['casual'] + hourly_df['registered']
    
    return hourly_df.reset_index()

def get_holiday_list(years):
    """
    Placeholder for Washington D.C. official public holidays.
    In a production setting, use the 'holidays' library:
    import holidays
    dc_holidays = holidays.US(state='DC', years=years)
    """
    # # Simple placeholder list - expands as needed
    # # Format: 'YYYY-MM-DD'
    # placeholders = [
    #     '2023-01-01', '2023-01-16', '2023-02-20', '2023-05-29', '2023-06-19',
    #     '2023-07-04', '2023-09-04', '2023-10-09', '2023-11-10', '2023-11-23', '2023-12-25'
    # ]
    # return pd.to_datetime(placeholders)
    return holidays.US(state='DC', years=years)

def add_calendar_features(df):
    """
    Extracts calendar-based features to match Dataset B schema.
    """
    print("Extracting calendar features...")
    dt = df['datetime'].dt
    
    df['dteday'] = dt.strftime('%Y-%m-%d')
    df['mnth'] = dt.month
    df['hr'] = dt.hour
    df['weekday'] = dt.weekday # 0: Monday, 6: Sunday (Standard Pandas)
    
    # yr: 2011=0, 2012=1, etc.
    df['yr'] = dt.year - 2011
    
    # season (1: Winter, 2: Spring, 3: Summer, 4: Autumn)
    # Mapping based on month
    def get_season(month):
        if month in [12, 1, 2]: return 1
        if month in [3, 4, 5]: return 2
        if month in [6, 7, 8]: return 3
        return 4 # 9, 10, 11
    
    df['season'] = df['mnth'].apply(get_season)
    
    # Holiday logic
    years = df['datetime'].dt.year.unique()
    holidays = get_holiday_list(years)
    df['holiday'] = df['datetime'].dt.normalize().isin(holidays).astype(int)
    
    # workingday: 1 if weekday (0-4) and NOT holiday
    df['workingday'] = ((df['weekday'] < 5) & (df['holiday'] == 0)).astype(int)
    
    return df

def fetch_and_merge_weather(bike_df, start_date, end_date):
    """
    Fetches historical hourly weather data from Open-Meteo ERA5 Archive API
    and merges it into the bike-sharing dataframe.
    """
    print(f"Fetching weather data from {start_date} to {end_date}...")
    
    url = "https://archive-api.open-meteo.com/v1/era5"
    params = {
        "latitude": 38.9072,
        "longitude": -77.0369,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
        "timezone": "America/New_York"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()['hourly']
        
        weather_df = pd.DataFrame(weather_data)
        weather_df['datetime'] = pd.to_datetime(weather_df['time'])
        
        # Mapping WMO weather codes to weathersit (1-4 scale)
        # 1: Clear/Partly Cloudy, 2: Mist/Cloudy, 3: Light Snow/Rain, 4: Heavy Rain/Snow/Storm
        def map_weather_code(code):
            if code in [0, 1, 2, 3]: return 1
            if code in [45, 48, 51, 53, 55]: return 2
            if code in [56, 57, 61, 63, 65, 80, 81, 82, 71, 73, 75, 77, 85, 86]: return 3
            if code in [66, 67, 95, 96, 99]: return 4
            return np.nan

        weather_df['weathersit'] = weather_df['weather_code'].apply(map_weather_code)
        
        # Normalization
        # temp: temperature_2m / 41.0
        # atemp: apparent_temperature / 50.0
        # hum: relative_humidity_2m / 100.0
        # windspeed: wind_speed_10m / 67.0
        weather_df['temp'] = weather_df['temperature_2m'] / 41.0
        weather_df['atemp'] = weather_df['apparent_temperature'] / 50.0
        weather_df['hum'] = weather_df['relative_humidity_2m'] / 100.0
        weather_df['windspeed'] = weather_df['wind_speed_10m'] / 67.0
        
        # Merge
        # Drop the original placeholder columns if they exist in bike_df to avoid suffixes
        cols_to_drop = ['weathersit', 'temp', 'atemp', 'hum', 'windspeed']
        bike_df = bike_df.drop(columns=[c for c in cols_to_drop if c in bike_df.columns])
        
        result_df = bike_df.merge(
            weather_df[['datetime', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed']], 
            on='datetime', 
            how='left'
        )
        
        return result_df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        # Return bike_df with NaNs for weather if request fails
        for col in ['weathersit', 'temp', 'atemp', 'hum', 'windspeed']:
            bike_df[col] = np.nan
        return bike_df

def process_bikeshare_data(input_csv, output_path=None):
    """
    Processes a single raw CSV file into an aggregated hourly DataFrame.
    If output_path is provided, it also fetches weather and saves to disk.
    """
    # 1. Load
    raw_df = load_raw_data(input_csv)
    
    # 2. Aggregate
    hourly_df = aggregate_trips_hourly(raw_df)
    
    # 3. Calendar Features
    hourly_df = add_calendar_features(hourly_df)
    
    # 4. Weather Integration (Only if outputting directly)
    if output_path:
        start_date = hourly_df['datetime'].min().strftime('%Y-%m-%d')
        end_date = hourly_df['datetime'].max().strftime('%Y-%m-%d')
        hourly_df = fetch_and_merge_weather(hourly_df, start_date, end_date)
        
        # Final Schema ordering
        target_columns = [
            'dteday', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
            'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed', 
            'casual', 'registered', 'cnt'
        ]
        final_df = hourly_df[target_columns].sort_values(['dteday', 'hr'])
        final_df.to_csv(output_path, index=False)
        print(f"Successfully saved aggregated data to {output_path}")
        return final_df
    
    return hourly_df

if __name__ == "__main__":
    PROJECT_ROOT = Path("/home/mendee/Projects/Areas/BME2026/trustworthy/eda_hw")
    # TODO: MODIFY HERE!!!!!!
    DATA_DIR = PROJECT_ROOT / "assets/bike_sharing_2025"
    
    # 1. Find all monthly trip data files for the year (e.g., matching the pattern)
    file_pattern = "*-capitalbikeshare-tripdata.csv"
    files = sorted(list(DATA_DIR.glob(file_pattern)))
    
    if not files:
        print(f"No files found matching {file_pattern} in {DATA_DIR}")
    else:
        print(f"Found {len(files)} monthly files. Starting aggregation...")
        
        all_monthly_aggregates = []
        
        # 2. Process each file
        for file_path in files:
            print(f"Processing: {file_path.name}...")
            # Return df instead of writing to disk
            monthly_df = process_bikeshare_data(file_path, output_path=None)
            all_monthly_aggregates.append(monthly_df)
            
        # 3. Combine and merge
        print("Combining all months...")
        combined_df = pd.concat(all_monthly_aggregates, ignore_index=True)
        
        # 4. Handle overlaps/duplicates at month boundaries
        # Group by datetime and sum counts
        combined_df = combined_df.groupby('datetime')[['casual', 'registered', 'cnt']].sum().reset_index()
        
        # 5. Re-apply calendar features to the combined range
        combined_df = add_calendar_features(combined_df)
        
        # 6. Fetch weather for the entire combined range
        start_date = combined_df['datetime'].min().strftime('%Y-%m-%d')
        end_date = combined_df['datetime'].max().strftime('%Y-%m-%d')
        print(f"Aggregated range: {start_date} to {end_date}")
        
        combined_df = fetch_and_merge_weather(combined_df, start_date, end_date)
        
        # 7. Final Schema ordering and Sorting
        target_columns = [
            'dteday', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
            'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed', 
            'casual', 'registered', 'cnt'
        ]
        
        final_df = combined_df[target_columns].sort_values(['dteday', 'hr'])
        
        # 8. Save the master hourly dataset
        OUTPUT_PATH = PROJECT_ROOT / 'assets/processed_hourly_2025_tripdata.csv'
        final_df.to_csv(OUTPUT_PATH, index=False)
        
        print(f"\nFinal master dataset saved to: {OUTPUT_PATH}")
        print(f"Total hours processed: {len(final_df)}")

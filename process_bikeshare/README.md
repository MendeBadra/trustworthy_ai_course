# Capital Bikeshare Data Processing Pipeline

This tool transforms raw Capital Bikeshare trip logs (Dataset A) into a cleaned, hourly aggregated dataset that matches the schema of classic bike-sharing datasets (Dataset B). It includes automated calendar feature extraction and historical weather integration via the Open-Meteo ERA5 API.

## Input Schema (Dataset A)
The script expects a CSV file with the following columns:
- `ride_id`, `rideable_type`, `started_at`, `ended_at`, `start_station_name`, `start_station_id`, `end_station_name`, `end_station_id`, `start_lat`, `start_lng`, `end_lat`, `end_lng`, `member_casual`

## Output Schema (Dataset B)
The resulting hourly CSV contains:
- `dteday`: Date (YYYY-MM-DD)
- `season`: Season (1: Winter, 2: Spring, 3: Summer, 4: Autumn)
- `yr`: Year (0: 2011, 1: 2012, etc.)
- `mnth`: Month (1 to 12)
- `hr`: Hour (0 to 23)
- `holiday`: Whether day is holiday or not (1: Yes, 0: No)
- `weekday`: Day of the week (0 to 6)
- `workingday`: If day is neither weekend nor holiday is 1, otherwise is 0.
- `weathersit`: Weather situation (1 to 4 scale)
- `temp`: Normalized temperature (Celsius / 41)
- `atemp`: Normalized feeling temperature (Celsius / 50)
- `hum`: Normalized humidity (Humidity / 100)
- `windspeed`: Normalized wind speed (Wind speed / 67)
- `casual`: Count of casual users
- `registered`: Count of registered users
- `cnt`: Total count of bike rentals

## Key Features

### 1. Temporal Aggregation
- Automatically floors trip timestamps to hourly buckets.
- Generates a continuous time index to ensure hours with zero rentals are preserved in the output.

### 2. Weather Data Integration
- Connects to [Open-Meteo ERA5 Archive API](https://open-meteo.com/en/docs/era5-api).
- Fetches historical data for Washington D.C. (38.9072° N, 77.0369° W).
- Maps WMO Weather Codes to the internal `weathersit` 1–4 scale.
- Normalizes all weather metrics to the specific ranges used in the original bike-sharing datasets.

### 3. Calendar Features
- Extracts seasonal and monthly patterns.
- Includes a holiday lookup (currently placeholder for common US holidays).
- Calculates `workingday` status based on calendar and holiday data.

## Requirements
- Python 3.x
- pandas
- numpy
- requests

## Usage
Update the paths in the `if __name__ == "__main__":` block of `process_bikeshare.py`:

```python
DATASET_A_PATH = 'path/to/your/raw_tripdata.csv'
OUTPUT_PATH = 'path/to/output_hourly_data.csv'
```

Then run the script:
```bash
python process_bikeshare.py
```

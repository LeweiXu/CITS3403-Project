import csv
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

def parse_csv(file_path):
    parsed_data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)  # Skip the header row
            for row in reader:
                col1 = row[0]
                col2 = row[1]
                col3 = int(row[2])
                col4 = datetime.strptime(row[3], '%Y-%m-%d').date()
                parsed_data.append([col1, col2, col3, col4])
    except Exception as e:
        print(f"Error parsing CSV file: {e}")
    return parsed_data

def calc_total_time(data):
    total_time = 0
    for row in data:
        total_time += row[2]
    return total_time

def find_highest_media_type(data):
    media_durations = {}
    for row in data:
        media_type = row[0] 
        duration = row[2]
        if media_type in media_durations:
            media_durations[media_type] += duration
        else:
            media_durations[media_type] = duration

    highest_media_type = max(media_durations, key=media_durations.get)
    return highest_media_type, media_durations[highest_media_type]

def calc_weekly_durations(data):
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=['media_type', 'media_name', 'duration', 'date'])
    df['date'] = pd.to_datetime(df['date'])  # Ensure the date column is in datetime format

    # Calculate the start of the week (Monday) for each date
    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='d')

    # Group by week_start and calculate the daily average for each week
    weekly_totals = df.groupby('week_start')['duration'].sum()
    weekly_averages = (weekly_totals / 7)/60  # Get average and convert to hours

    # Convert the index (week_start) to strings
    weekly_averages.index = weekly_averages.index.strftime('%Y-%m-%d')

    return weekly_averages.to_dict()

def calc_average_daily_consumption(data):
    daily_durations = defaultdict(int)

    for row in data:
        date = row[3]
        duration = row[2] 
        daily_durations[date] += duration

    total_days = len(daily_durations)
    total_duration = sum(daily_durations.values())

    if total_days == 0:
        return 0  # Avoid division by zero

    return total_duration / total_days
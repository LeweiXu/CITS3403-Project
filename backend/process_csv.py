import csv
from datetime import datetime

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
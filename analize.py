import glob
import os

import pandas as pd
import statistic as s

def calculate_threshold(csv_path):
    try:
        # Read the CSV file into a DataFrame
        data = pd.read_csv(csv_path)
        # Calculate the distance, RSSI - pf, and add them to the DataFrame
        data['P-Diff'] = (data['RSSI'] / data['fp'])
        # Calculate average distance and STD
        avg_distance = s.mean(data['distance'])
        std_distance = s.std(data['distance'])
        data = data.sort_values(by='P-Diff', ascending=True)
        # Check if there is a threshold that makes the STD lower than 2
        threshold = 0
        ratio = 0
        for threshold_candidate in data['P-Diff']:  # Adjust the range as needed
            subset = data[data['P-Diff'] >= threshold_candidate]
            subset_std = s.std(subset['distance'])
            if subset_std < 0.02:
                threshold = threshold_candidate
                ratio = (min(data['P-Diff']) - threshold)/(min(data['P-Diff'])-max(data['P-Diff']))
                break

        return avg_distance, std_distance, threshold, ratio

    except Exception as e:
        return None

current_directory = os.getcwd()

# Use glob to find all CSV files in the current directory
csv_files = glob.glob(os.path.join(current_directory, '*.csv'))
output_data = pd.DataFrame()
# Print the list of CSV files
for csv_file in csv_files:
    result = calculate_threshold(csv_file)
    if result is not None:
        avg_distance, std_distance, threshold, ratio = result
        new_row = {'file path': csv_file, 'avg_distance': avg_distance, 'STD': std_distance, 'TH': threshold, 'ratio': ratio}
        output_data = output_data._append(new_row, ignore_index=True)

output_data.to_csv('analyzed_data.csv')
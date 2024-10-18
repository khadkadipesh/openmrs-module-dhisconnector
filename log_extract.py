import re
import pandas as pd
from datetime import datetime

# Corrected path to the log file
log_file_path = r"C:\Users\Asus\Desktop\Integration\latency\log_latency.txt"

# Read log data
with open(log_file_path, 'r') as file:
    log_data = file.read()

# Split the log data into segments for processing
segments = re.split(r'\n\s*\n', log_data)  # Splitting based on double newline or new lines with spaces in between to identify separate sections

# Initialize lists to hold start and end times for OpenMRS and DHIS2 logs
openmrs_start_logs = []
openmrs_end_logs = []
dhis2_start_logs = []
dhis2_end_logs = []

# Extract OpenMRS and DHIS2 start and end times from the segments
for segment in segments:
    lines = segment.splitlines()
    if 'openmrs start' in segment.lower():
        # Process OpenMRS segment
        openmrs_start_time = None
        openmrs_end_time = None
        for line in lines:
            if openmrs_start_time is None and re.search(r"LoggingAdvice\.invoke\(117\)", line):
                # Capture the first occurrence as OpenMRS start time
                start_time_match = re.search(r"\|([\d\-T:,]+)\|", line)
                if start_time_match:
                    openmrs_start_time = start_time_match.group(1)

            if 'openmrs end' in segment.lower() and re.search(r"LoggingAdvice\.invoke\(157\)", line):
                # Capture the last occurrence before the word 'openmrs end'
                end_time_match = re.search(r"\|([\d\-T:,]+)\|", line)
                if end_time_match:
                    openmrs_end_time = end_time_match.group(1)

        if openmrs_start_time and openmrs_end_time:
            openmrs_start_logs.append(openmrs_start_time)
            openmrs_end_logs.append(openmrs_end_time)

    elif 'dhis2 start' in segment.lower():
        # Process DHIS2 segment
        dhis2_start_time = None
        dhis2_end_time = None
        for line in lines:
            if dhis2_start_time is None and re.search(r"\* INFO", line):
                # Capture the first occurrence as DHIS2 start time
                start_time_match = re.search(r"\* INFO\s+([\d\-T:,]+)", line)
                if start_time_match:
                    dhis2_start_time = start_time_match.group(1)

            if 'dhis2 end' in segment.lower() and re.search(r"Authentication event", line):
                # Capture the last occurrence before the word 'dhis2 end'
                end_time_match = re.search(r"INFO\s+([\d\-T:,]+)", line)
                if end_time_match:
                    dhis2_end_time = end_time_match.group(1)

        if dhis2_start_time and dhis2_end_time:
            dhis2_start_logs.append(dhis2_start_time)
            dhis2_end_logs.append(dhis2_end_time)

# Debugging: Print the number of captured start and end times
print(f"\nNumber of OpenMRS start logs: {len(openmrs_start_logs)}")
print(f"Number of OpenMRS end logs: {len(openmrs_end_logs)}")
print(f"Number of DHIS2 start logs: {len(dhis2_start_logs)}")
print(f"Number of DHIS2 end logs: {len(dhis2_end_logs)}")

# Function to calculate processing time in milliseconds
def calculate_time_difference(start, end):
    start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S,%f")
    end_time = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S,%f")
    return int((end_time - start_time).total_seconds() * 1000)

# Prepare the table data
table_data = []

# Iterate through logs to calculate the relevant times and latencies
for i in range(min(len(openmrs_start_logs), len(openmrs_end_logs), len(dhis2_start_logs), len(dhis2_end_logs))):
    try:
        openmrs_start = openmrs_start_logs[i]
        openmrs_end = openmrs_end_logs[i]
        dhis2_start = dhis2_start_logs[i]
        dhis2_end = dhis2_end_logs[i]
        
        # Calculate processing times
        openmrs_processing_time = calculate_time_difference(openmrs_start, openmrs_end)
        dhis2_processing_time = calculate_time_difference(dhis2_start, dhis2_end)
        latency = calculate_time_difference(openmrs_end, dhis2_start)

        # Append data to the table
        table_data.append([
            openmrs_start,
            openmrs_end,
            dhis2_start,
            dhis2_end,
            openmrs_processing_time,
            dhis2_processing_time,
            latency
        ])
    except IndexError:
        # If there is a mismatch in the number of logs, skip to the next iteration
        continue

# Create a DataFrame from the table data
columns = [
    "OpenMRS Start Time", "OpenMRS End Time", "DHIS2 Start Time", "DHIS2 End Time",
    "OpenMRS Processing Time (ms)", "DHIS2 Processing Time (ms)", "Latency (ms)"
]
df = pd.DataFrame(table_data, columns=columns)

# Check if any data was extracted
if df.empty:
    print("No data captured. Please check if the log format matches the expected patterns.")
else:
    # Display the DataFrame
    print(df)

    # Correct the output path to an existing directory on your system
    output_csv_path = r"C:\Users\Asus\Desktop\Integration\latency\output_latency.csv"  # Update with an existing directory
    df.to_csv(output_csv_path, index=False)

# Calculate the average latency (in milliseconds)
if not df.empty:
    average_latency = df["Latency (ms)"].mean()
    print(f"Average Latency (ms): {average_latency}")
else:
    print("No data available to calculate average latency.")

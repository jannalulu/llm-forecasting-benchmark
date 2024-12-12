# This script processes resolution data from metaculus_data_aibq3.json which is created by scraping/metaculus_aibq3.py
import json
import csv

def process_json_file(input_file, output_file):
  with open(input_file, 'r') as file:
    data = json.load(file)
  
  # Prepare the CSV data
  csv_data = []
  
  # Process each question in the list
  for question in data:
    question_id = question.get('id')
    resolution = 1 if question.get('resolution', '').lower() == 'yes' else 0
    csv_data.append([question_id, resolution])

  # Write to CSV file
  with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['question_id', 'resolution'])
    writer.writerows(csv_data)

  print(f"File '{output_file}' has been created successfully.")

input_file = 'scraping/metaculus_data_aibq4_wd.json'
output_file = 'aibq4_resolutions.csv'

process_json_file(input_file, output_file)

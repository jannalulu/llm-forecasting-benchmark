import json
import re
import csv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def extract_probabilities(text):
    # Handle None input
    if text is None:
        logging.info("Received null/None input, returning default values")
        return None, None, None
    
    # Find the prediction line
    prediction_match = re.search(r'My Prediction: ([\d.]+)% is the most likely\.', text)
    if prediction_match:
        prob = map(float, prediction_match.groups())
        logging.info(f"Extracted probabilities: {prob}%")
        return prob
    
    # If the above pattern doesn't match, try to find all percentages
    probabilities = re.findall(r'(\d+(?:\.\d{1,2})?)%', text)
    if probabilities:
        probabilities = [float(p) for p in probabilities]
        if len(probabilities) == 1:
            prob = probabilities[-1:]
            logging.info(f"Extracted probabilities: {prob}%")
            return prob
    
    logging.warning("Unable to extract probabilities.")
    return None, None, None

def process_json_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    results = {}
    for item in data:
        question_id = item['question_id']
        results[question_id] = {}
        
        llm_key = f'gpt-4o-2024-08-06_reasoning'
        
        if llm_key in item:
            results[question_id][f'gpt-4o'] = extract_probabilities(item[llm_key])

    return results

def write_to_csv(results, filename='baseline_outcomes_4o.csv'):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            headers = ['question_id'] + [f'{model}_{metric}' for model in ['gpt-4o'] for metric in ['prob']]
            writer.writerow(headers)
        
        for question_id, probabilities in results.items():
            row = [question_id]
            for model in ['gpt-4o']:
                key = f'{model}'
                probs = probabilities.get(key, (None))
                row.extend(probs)
            writer.writerow(row)

    logging.info(f"Results written to {filename}")

if __name__ == "__main__":
    json_file = "baseline_predictions_4o.json" 
    results = process_json_data(json_file)
    write_to_csv(results)
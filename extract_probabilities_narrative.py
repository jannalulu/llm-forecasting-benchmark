import json
import re
import csv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def extract_probabilities(text):
    if text is None:
        logging.warning("Received None value instead of text.")
        return None, None, None

    # Find the prediction line
    prediction_match = re.search(r'Our models had it at ([\d.]+)%', text)
    if prediction_match:
        prob = float(prediction_match.group(1))
        logging.info(f"Extracted probability: {prob}%")
        return prob
    
    # If the above pattern doesn't match, try to find all percentages
    probabilities = re.findall(r'(\d+(?:\.\d{1,2})?)%', text)
    if probabilities:
        probabilities = [float(p) for p in probabilities]
        if len(probabilities) >= 1:
            prob = probabilities[0]
            logging.info(f"Extracted probability: {prob}%")
            return prob
    logging.warning("Unable to extract probabilities.")
    return None

def process_json_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    results = {}
    for item in data:
        question_id = item['question_id']
        results[question_id] = {}
        
        for i in range(5):
            claude_key = f'claude_reasoning{i}'
            
            if claude_key in item:
                results[question_id][f'claude{i}'] = extract_probabilities(item[claude_key])

    return results

def write_to_csv(results, filename='aibq3_outcomes_narrative_claude_sonnet.csv'):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            headers = ['question_id'] + [f'{model}{i}_prob' for model in ['claude'] for i in range(5)]
            writer.writerow(headers)
        
        for question_id, probabilities in results.items():
            row = [question_id]
            for model in ['claude']:
                for i in range(5):
                    key = f'{model}{i}'
                    prob = probabilities.get(key, None)
                    row.append(prob)
            writer.writerow(row)

    logging.info(f"Results written to {filename}")

if __name__ == "__main__":
    json_file = "aibq3_predictions_narrative_claude_sonnet.json" 
    results = process_json_data(json_file)
    write_to_csv(results)

import json
import re
import csv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def extract_probabilities(text):
    # Find the prediction line
    prediction_match = re.search(r'Between ([\d.]+)% and ([\d.]+)%, (?:but |with )([\d.]+)% being the most likely\.', text)
    if prediction_match:
        min_prob, max_prob, final_prob = map(float, prediction_match.groups())
        logging.info(f"Extracted probabilities: Min: {min_prob}%, Max: {max_prob}%, Final: {final_prob}%")
        return min_prob, max_prob, final_prob
    
    # If the above pattern doesn't match, try to find all percentages
    probabilities = re.findall(r'(\d+(?:\.\d{1,2})?)%', text)
    if probabilities:
        probabilities = [float(p) for p in probabilities]
        if len(probabilities) >= 3:
            min_prob, max_prob, final_prob = probabilities[-3:]
            logging.info(f"Extracted probabilities: Min: {min_prob}%, Max: {max_prob}%, Final: {final_prob}%")
            return min_prob, max_prob, final_prob
    
    logging.warning("Unable to extract probabilities.")
    return None, None, None

def process_json_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    results = {}
    for item in data:
        question_id = item['question_id']
        results[question_id] = {}
        
        for i in range(5):
            gpt_key = f'gpt_reasoning{i}'
            claude_key = f'claude_reasoning{i}'
            
            if gpt_key in item:
                results[question_id][f'gpt{i}'] = extract_probabilities(item[gpt_key])
            if claude_key in item:
                results[question_id][f'claude{i}'] = extract_probabilities(item[claude_key])

    return results

def write_to_csv(results, filename='test_aibq3.csv'):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            headers = ['question_id'] + [f'{model}{i}_{metric}' for model in ['gpt', 'claude'] for i in range(5) for metric in ['min', 'max', 'final']]
            writer.writerow(headers)
        
        for question_id, probabilities in results.items():
            row = [question_id]
            for model in ['gpt', 'claude']:
                for i in range(5):
                    key = f'{model}{i}'
                    probs = probabilities.get(key, (None, None, None))
                    row.extend(probs)
            writer.writerow(row)

    logging.info(f"Results written to {filename}")

if __name__ == "__main__":
    json_file = "test_aibq3_predictions1.json" 
    results = process_json_data(json_file)
    write_to_csv(results)
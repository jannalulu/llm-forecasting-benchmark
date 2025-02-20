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
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    results = {}
    for item in data:
        question_id = item['question_id']
        results[question_id] = {}
        
        for i in range(5):
            llm_key = f'deepseek-chat_reasoning{i}'
            
            if llm_key in item:
                results[question_id][f'deepseekv3{i}'] = extract_probabilities(item[llm_key])

    return results

def write_to_csv(results, filename='aibq3_outcomes_past_deepseekv3.csv'):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            headers = ['question_id'] + [f'{model}{i}_{metric}' for model in ['deepseekv3'] for i in range(5) for metric in ['min', 'max', 'final']]
            writer.writerow(headers)
        
        for question_id, probabilities in results.items():
            row = [question_id]
            for model in ['deepseekv3']:
                for i in range(5):
                    key = f'{model}{i}'
                    probs = probabilities.get(key, (None, None, None))
                    row.extend(probs)
            writer.writerow(row)

    logging.info(f"Results written to {filename}")

if __name__ == "__main__":
    json_file = "aibq3_predictions_past_deepseekv3.json" 
    results = process_json_data(json_file)
    write_to_csv(results)
import json
import re
import csv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def extract_probabilities(text):
    # Find the prediction line
    prediction_match = re.search(r'([\d.]+)% being the most likely, with ([\d.]+)% confidence\.', text)
    if prediction_match:
        final_prob, conf = map(float, prediction_match.groups())
        logging.info(f"Extracted probabilities: Final: {final_prob}%, Conf: {conf}%")
        return final_prob, conf
    
    # If the above pattern doesn't match, try to find all percentages
    probabilities = re.findall(r'(\d+(?:\.\d{1,2})?)%', text)
    if probabilities:
        probabilities = [float(p) for p in probabilities]
        if len(probabilities) >= 2:
            final_prob, conf = probabilities[-2:]
            logging.info(f"Extracted probabilities: Final: {final_prob}%, Conf: {conf}%")
            return final_prob, conf
    
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
            gpt_key = f'gpt_reasoning{i}'
            
            if gpt_key in item:
                results[question_id][f'gpt{i}'] = extract_probabilities(item[gpt_key])

    return results

def write_to_csv(results, filename='aibq3_outcomes_conf_4o.csv'):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            headers = ['question_id'] + [f'{model}{i}_{metric}' for model in ['gpt'] for i in range(5) for metric in ['final', 'conf']]
            writer.writerow(headers)
        
        for question_id, probabilities in results.items():
            row = [question_id]
            for model in ['gpt']:
                for i in range(5):
                    key = f'{model}{i}'
                    probs = probabilities.get(key, (None, None))
                    row.extend(probs)
            writer.writerow(row)

    logging.info(f"Results written to {filename}")

if __name__ == "__main__":
    json_file = "aibq3_predictions_conf_4o.json" 
    results = process_json_data(json_file)
    write_to_csv(results)
import csv
import statistics
from scipy import stats
import numpy as np
from typing import Dict, List, Tuple, Optional

def read_resolutions(resolutions_file: str) -> Dict[str, int]:
    """Read resolution data from CSV file."""
    with open(resolutions_file, 'r') as f:
        reader = csv.DictReader(f)
        return {row['question_id']: int(row['resolution']) for row in reader}

def calculate_standard_error(scores: List[float]) -> Optional[float]:
    """Calculate standard error from a list of scores."""
    n = len(scores)
    if n < 2:
        return None
    std_dev = statistics.stdev(scores)
    return std_dev / (n ** 0.5)

def process_predictions(outcomes_file: str, resolutions: Dict[str, int]) -> Tuple[Dict[str, Dict], Dict[str, List[float]]]:
    """Process predictions from outcomes file and organize data for calculations."""
    question_predictions = {}
    brier_scores = {f'gpt-4o': []}
    
    with open(outcomes_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_id = row['question_id']
            if question_id in resolutions:
                resolution = resolutions[question_id]
                
                if question_id not in question_predictions:
                    question_predictions[question_id] = {
                        'predictions': [],
                        'resolution': resolution
                    }
                
                for model in brier_scores.keys():
                    prediction = float(row[f'{model}_prob']) / 100
                    question_predictions[question_id]['predictions'].append(prediction)
                    brier_score = (resolution - prediction) ** 2
                    brier_scores[model].append(brier_score)
    
    return question_predictions, brier_scores

def format_results(brier_scores: Dict[str, List[float]]
                   ) -> Dict[str, Dict[str, float]]:
    results = {}
    
    # Individual model results
    for model, scores in brier_scores.items():
        results[model] = {
            'score': sum(scores) / len(scores),
            'se': calculate_standard_error(scores)
        }
    
    return results

def calculate_brier_scores(resolutions_file: str, outcomes_file: str) -> Dict[str, Dict[str, float]]:
    """Calculate Brier scores for individual models."""
    resolutions = read_resolutions(resolutions_file)
    _, brier_scores = process_predictions(outcomes_file, resolutions)
    return format_results(brier_scores)


def print_results(results: Dict[str, Dict[str, float]]) -> None:
    """Print formatted results."""
    print("\nIndividual Model Brier Scores (score, standard error):")
    for model in [f'gpt-4o']:
        score = results[model]['score']
        se = results[model]['se']
        print(f"{model}: {score:.4f}, {se:.4f}")

if __name__ == "__main__":
    resolutions_file = 'baseline_subset_resolutions.csv'
    outcomes_file = 'baseline_outcomes_4o.csv'
    
    results = calculate_brier_scores(resolutions_file, outcomes_file)
    print_results(results)
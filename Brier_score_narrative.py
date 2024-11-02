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

def initialize_models() -> List[str]:
    return [f'claude{i}' for i in range(5)]

def process_predictions(outcomes_file: str, resolutions: Dict[str, int]) -> Tuple[Dict[str, Dict], Dict[str, List[float]]]:
    """Process predictions from outcomes file and organize data."""
    models = initialize_models()
    question_predictions = {}
    brier_scores = {model: [] for model in models}
    
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
                
                for model in models:
                    prediction = float(row[f'{model}_prob']) / 100
                    question_predictions[question_id]['predictions'].append(prediction)
                    brier_score = (resolution - prediction) ** 2
                    brier_scores[model].append(brier_score)
    
    return question_predictions, brier_scores

def calculate_ensemble_scores(question_predictions: Dict[str, Dict]) -> Tuple[List[float], List[float]]:
    """Calculate ensemble scores using median and mean aggregation methods."""
    median_prediction_brier = []
    mean_prediction_brier = []
    
    for question_data in question_predictions.values():
        predictions = question_data['predictions']
        resolution = question_data['resolution']
        
        median_pred = statistics.median(predictions)
        median_prediction_brier.append((resolution - median_pred) ** 2)
        
        mean_pred = statistics.mean(predictions)
        mean_prediction_brier.append((resolution - mean_pred) ** 2)
    
    return median_prediction_brier, mean_prediction_brier

def format_results(brier_scores: Dict[str, List[float]], 
                  median_brier: List[float], 
                  mean_brier: List[float]) -> Dict[str, Dict[str, float]]:
    """Format final results including scores and standard errors."""
    results = {}
    
    # Individual model results
    for model, scores in brier_scores.items():
        results[model] = {
            'score': sum(scores) / len(scores),
            'se': calculate_standard_error(scores)
        }
    
    # Ensemble results
    results['median_ensemble'] = {
        'score': sum(median_brier) / len(median_brier),
        'se': calculate_standard_error(median_brier)
    }
    results['mean_ensemble'] = {
        'score': sum(mean_brier) / len(mean_brier),
        'se': calculate_standard_error(mean_brier)
    }
    
    return results

def print_results(results: Dict[str, Dict[str, float]]) -> None:
    print("\nIndividual Model Brier Scores (score, standard error):")
    for model in initialize_models():
        score = results[model]['score']
        se = results[model]['se']
        print(f"{model}: {score:.4f}, {se:.4f}")

    print("\nEnsemble Brier Scores (score, standard error):")
    print(f"Median Ensemble: {results['median_ensemble']['score']:.4f}, {results['median_ensemble']['se']:.4f}")
    print(f"Mean Ensemble: {results['mean_ensemble']['score']:.4f}, {results['mean_ensemble']['se']:.4f}")

def calculate_brier_scores(resolutions_file: str, outcomes_file: str) -> Dict[str, Dict[str, float]]:
    """Main function to calculate all Brier scores and metrics."""
    resolutions = read_resolutions(resolutions_file)
    question_predictions, brier_scores = process_predictions(outcomes_file, resolutions)
    median_brier, mean_brier = calculate_ensemble_scores(question_predictions)
    return format_results(brier_scores, median_brier, mean_brier)

if __name__ == "__main__":
    resolutions_file = 'aibq3_resolutions.csv'
    outcomes_file = 'aibq3_outcomes_narrative_claude_sonnet.csv'
    
    # Calculate and print results
    results = calculate_brier_scores(resolutions_file, outcomes_file)
    print_results(results)
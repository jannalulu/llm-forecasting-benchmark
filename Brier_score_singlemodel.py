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
    brier_scores = {f'deepseekv3{i}': [] for i in range(5)}
    
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
                    prediction = float(row[f'{model}_final']) / 100
                    question_predictions[question_id]['predictions'].append(prediction)
                    brier_score = (resolution - prediction) ** 2
                    brier_scores[model].append(brier_score)
    
    return question_predictions, brier_scores

def calculate_ensemble_scores(question_predictions: Dict[str, Dict]) -> Tuple[List[float], List[float]]:
    """Calculate Brier scores for median and mean ensembles."""
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
                  median_prediction_brier: List[float],
                  mean_prediction_brier: List[float]) -> Dict[str, Dict[str, float]]:
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
        'score': sum(median_prediction_brier) / len(median_prediction_brier),
        'se': calculate_standard_error(median_prediction_brier)
    }
    results['mean_ensemble'] = {
        'score': sum(mean_prediction_brier) / len(mean_prediction_brier),
        'se': calculate_standard_error(mean_prediction_brier)
    }
    
    return results

def calculate_brier_scores(resolutions_file: str, outcomes_file: str) -> Dict[str, Dict[str, float]]:
    """Calculate Brier scores for individual models and ensembles."""
    resolutions = read_resolutions(resolutions_file)
    question_predictions, brier_scores = process_predictions(outcomes_file, resolutions)
    median_prediction_brier, mean_prediction_brier = calculate_ensemble_scores(question_predictions)
    return format_results(brier_scores, median_prediction_brier, mean_prediction_brier)

def print_results(results: Dict[str, Dict[str, float]]) -> None:
    """Print formatted results."""
    print("\nIndividual Model Brier Scores (score, standard error):")
    for model in [f'deepseekv3{i}' for i in range(5)]:
        score = results[model]['score']
        se = results[model]['se']
        print(f"{model}: {score:.4f}, {se:.4f}")

    print("\nEnsemble Brier Scores (score, standard error):")
    print(f"Median Ensemble: {results['median_ensemble']['score']:.4f}, {results['median_ensemble']['se']:.4f}")
    print(f"Mean Ensemble: {results['mean_ensemble']['score']:.4f}, {results['mean_ensemble']['se']:.4f}")

if __name__ == "__main__":
    resolutions_file = 'aibq3_resolutions.csv'
    outcomes_file = 'aibq3_outcomes_past_deepseekv3.csv'
    
    results = calculate_brier_scores(resolutions_file, outcomes_file)
    print_results(results)
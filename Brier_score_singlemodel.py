import csv
import statistics
from scipy import stats
import numpy as np

resolutions_file = 'aibq3_resolutions.csv'
outcomes_file = 'aibq3_outcomes_past_claude_sonnet.csv'

def calculate_standard_error(scores):
    n = len(scores)
    if n < 2:  # Need at least 2 samples to calculate standard deviation
        return None
    std_dev = statistics.stdev(scores)
    return std_dev / (n ** 0.5)

def calculate_brier_scores(resolutions_file, outcomes_file):
    # Read resolutions
    resolutions = {}
    with open(resolutions_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            resolutions[row['question_id']] = int(row['resolution'])

    # Store predictions by question for ensemble calculations
    question_predictions = {}
    # Store individual model Brier scores
    brier_scores = {model: [] for model in ['claude0', 'claude1', 'claude2', 'claude3', 'claude4']}
    
    # Read outcomes and store predictions by question
    with open(outcomes_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_id = row['question_id']
            if question_id in resolutions:
                resolution = resolutions[question_id]
                
                # Initialize predictions list for this question if not exists
                if question_id not in question_predictions:
                    question_predictions[question_id] = {
                        'predictions': [],
                        'resolution': resolution
                    }
                
                # Store individual model predictions and calculate their Brier scores
                for model in brier_scores.keys():
                    prediction = float(row[f'{model}_final']) / 100  # Convert percentage to probability
                    question_predictions[question_id]['predictions'].append(prediction)
                    brier_score = (resolution - prediction) ** 2
                    brier_scores[model].append(brier_score)

    # Calculate various aggregated Brier scores
    results = {}
    
    # Individual model average Brier scores
    for model, scores in brier_scores.items():
        results[model] = sum(scores) / len(scores)

    # Calculate Brier score for median predictions
    median_prediction_brier = []
    # Calculate Brier score for mean predictions
    mean_prediction_brier = []
    
    for question_data in question_predictions.values():
        predictions = question_data['predictions']
        resolution = question_data['resolution']
        
        # Calculate median prediction for this question
        median_pred = statistics.median(predictions)
        median_prediction_brier.append((resolution - median_pred) ** 2)
        
        # Calculate mean prediction for this question
        mean_pred = statistics.mean(predictions)
        mean_prediction_brier.append((resolution - mean_pred) ** 2)
    
    # Add ensemble results with standard errors
    results['median_ensemble'] = {
        'score': sum(median_prediction_brier) / len(median_prediction_brier),
        'se': calculate_standard_error(median_prediction_brier)
    }
    results['mean_ensemble'] = {
        'score': sum(mean_prediction_brier) / len(mean_prediction_brier),
        'se': calculate_standard_error(mean_prediction_brier)
    }
    
    # Add standard errors for individual models
    for model in brier_scores.keys():
        score = results[model]
        results[model] = {
            'score': score,
            'se': calculate_standard_error(brier_scores[model])
        }
    
    return results

# Calculate and print results
results = calculate_brier_scores(resolutions_file, outcomes_file)

print("\nIndividual Model Brier Scores (score, standard error):")
for model in ['claude0', 'claude1', 'claude2', 'claude3', 'claude4']:
    score = results[model]['score']
    se = results[model]['se']
    print(f"{model}: {score:.4f}, {se:.4f}")

print("\nEnsemble Brier Scores (score, standard error):")
print(f"Median Ensemble: {results['median_ensemble']['score']:.4f}, {results['median_ensemble']['se']:.4f}")
print(f"Mean Ensemble: {results['mean_ensemble']['score']:.4f}, {results['mean_ensemble']['se']:.4f}")
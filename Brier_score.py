import csv
import statistics
from scipy import stats
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

def initialize_model_structures() -> Tuple[List[str], List[str]]:
    """Initialize model names for GPT and Claude."""
    gpt_models = [f'gpt{i}' for i in range(5)]
    claude_models = [f'claude{i}' for i in range(5)]
    return gpt_models, claude_models

def process_predictions(outcomes_file: str, resolutions: Dict[str, int]) -> Tuple[Dict[str, Dict[str, List[float]]], Dict[str, List[float]]]:
    """Process predictions from outcomes file and organize data by model family."""
    gpt_models, claude_models = initialize_model_structures()
    all_models = gpt_models + claude_models
    
    question_predictions = {
        qid: {'gpt_preds': [], 'claude_preds': []} 
        for qid in resolutions.keys()
    }
    
    brier_scores = {model: [] for model in all_models}
    
    with open(outcomes_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_id = row['question_id']
            if question_id in resolutions:
                for model in all_models:
                    prediction = float(row[f'{model}_final']) / 100
                    model_family = 'gpt_preds' if model.startswith('gpt') else 'claude_preds'
                    question_predictions[question_id][model_family].append(prediction)
                    brier_score = (resolutions[question_id] - prediction) ** 2
                    brier_scores[model].append(brier_score)
    
    return question_predictions, brier_scores

def calculate_ensemble_scores(question_predictions: Dict[str, Dict[str, List[float]]], 
                            resolutions: Dict[str, int]) -> Dict[str, List[float]]:
    """Calculate ensemble scores using median and mean aggregation methods."""
    ensemble_scores = {
        'gpt_median': [], 'claude_median': [],
        'gpt_mean': [], 'claude_mean': []
    }
    
    for question_id, preds in question_predictions.items():
        if preds['gpt_preds'] and preds['claude_preds']:
            resolution = resolutions[question_id]
            
            # Calculate and store median-based scores
            gpt_median = statistics.median(preds['gpt_preds'])
            claude_median = statistics.median(preds['claude_preds'])
            ensemble_scores['gpt_median'].append((resolution - gpt_median) ** 2)
            ensemble_scores['claude_median'].append((resolution - claude_median) ** 2)
            
            # Calculate and store mean-based scores
            gpt_mean = statistics.mean(preds['gpt_preds'])
            claude_mean = statistics.mean(preds['claude_preds'])
            ensemble_scores['gpt_mean'].append((resolution - gpt_mean) ** 2)
            ensemble_scores['claude_mean'].append((resolution - claude_mean) ** 2)
    
    return ensemble_scores

def format_results(brier_scores: Dict[str, List[float]], 
                  ensemble_scores: Dict[str, List[float]]) -> Tuple[Dict[str, List[float]], Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
    """Format final results including individual and ensemble scores."""
    # Calculate average scores for individual models
    average_scores = {
        model: {
            'score': sum(scores) / len(scores),
            'se': calculate_standard_error(scores)
        }
        for model, scores in brier_scores.items()
    }
    
    # Calculate ensemble scores
    formatted_ensemble_scores = {
        'GPT median': {
            'score': sum(ensemble_scores['gpt_median']) / len(ensemble_scores['gpt_median']),
            'se': calculate_standard_error(ensemble_scores['gpt_median'])
        },
        'Claude median': {
            'score': sum(ensemble_scores['claude_median']) / len(ensemble_scores['claude_median']),
            'se': calculate_standard_error(ensemble_scores['claude_median'])
        },
        'GPT mean': {
            'score': sum(ensemble_scores['gpt_mean']) / len(ensemble_scores['gpt_mean']),
            'se': calculate_standard_error(ensemble_scores['gpt_mean'])
        },
        'Claude mean': {
            'score': sum(ensemble_scores['claude_mean']) / len(ensemble_scores['claude_mean']),
            'se': calculate_standard_error(ensemble_scores['claude_mean'])
        }
    }
    
    return brier_scores, average_scores, formatted_ensemble_scores

def calculate_cohens_d(gpt_scores: List[float], claude_scores: List[float]) -> float:
    """Calculate Cohen's d effect size."""
    mean_diff = statistics.mean(gpt_scores) - statistics.mean(claude_scores)
    pooled_std = (
        ((len(gpt_scores) - 1) * statistics.stdev(gpt_scores) ** 2 + 
         (len(claude_scores) - 1) * statistics.stdev(claude_scores) ** 2) / 
        (len(gpt_scores) + len(claude_scores) - 2)
    ) ** 0.5
    return mean_diff / pooled_std

def perform_statistical_tests(brier_scores: Dict[str, List[float]]) -> Tuple[float, float, float]:
    """Perform statistical tests comparing GPT and Claude scores."""
    gpt_scores = [score for model, scores in brier_scores.items() 
                 if model.startswith('gpt') for score in scores]
    claude_scores = [score for model, scores in brier_scores.items() 
                    if model.startswith('claude') for score in scores]
    
    t_statistic, p_value = stats.ttest_rel(gpt_scores, claude_scores)
    cohens_d = calculate_cohens_d(gpt_scores, claude_scores)
    
    return t_statistic, p_value, cohens_d

def print_statistical_results(t_statistic: float, p_value: float, cohens_d: float) -> None:
    """Print formatted statistical test results."""
    print("\nStatistical Test Results:")
    print(f"Paired t-test (GPT vs Claude):")
    print(f"t-statistic: {t_statistic:.4f}")
    print(f"p-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("The difference between GPT and Claude scores is statistically significant (p < 0.05).")
    else:
        print("The difference between GPT and Claude scores is not statistically significant (p >= 0.05).")
    
    print(f"\nEffect size (Cohen's d): {cohens_d:.4f}")
    if abs(cohens_d) < 0.2:
        print("The effect size is small.")
    elif abs(cohens_d) < 0.5:
        print("The effect size is medium.")
    else:
        print("The effect size is large.")

def print_brier_results(average_scores: Dict[str, Dict[str, float]], 
                       ensemble_scores: Dict[str, Dict[str, float]]) -> None:
    """Print formatted Brier score results."""
    print("Average Brier Scores (score, standard error):")
    for model, result in average_scores.items():
        print(f"{model}: {result['score']:.4f}, {result['se']:.4f}")
    
    print("\nEnsemble Brier Scores (score, standard error):")
    for model, result in ensemble_scores.items():
        print(f"{model}: {result['score']:.4f}, {result['se']:.4f}")

def calculate_brier_scores(resolutions_file: str, outcomes_file: str) -> Tuple[Dict[str, List[float]], Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
    """Main function to calculate all Brier scores and ensemble metrics."""
    resolutions = read_resolutions(resolutions_file)
    question_predictions, brier_scores = process_predictions(outcomes_file, resolutions)
    ensemble_scores = calculate_ensemble_scores(question_predictions, resolutions)
    return format_results(brier_scores, ensemble_scores)

if __name__ == "__main__":
    resolutions_file = 'aibq3_resolutions.csv'
    outcomes_file = 'aibq3_outcomes.csv'
    
    # Calculate all scores
    brier_scores, average_scores, ensemble_scores = calculate_brier_scores(resolutions_file, outcomes_file)
    
    # Print Brier score results
    print_brier_results(average_scores, ensemble_scores)
    
    # Perform and print statistical analysis
    t_stat, p_val, effect_size = perform_statistical_tests(brier_scores)
    print_statistical_results(t_stat, p_val, effect_size)
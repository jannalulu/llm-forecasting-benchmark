import csv
import statistics
from scipy import stats

resolutions_file = 'aibq3_resolutions.csv'
outcomes_file = 'aibq3_outcomes_past.csv'

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

    # Initialize data structures to store predictions by question
    question_predictions = {qid: {'gpt_preds': [], 'claude_preds': []} for qid in resolutions.keys()}
    
    # Read outcomes and organize predictions by question
    brier_scores = {model: [] for model in ['gpt0', 'gpt1', 'gpt2', 'gpt3', 'gpt4', 'claude0', 'claude1', 'claude2', 'claude3', 'claude4']}
    
    with open(outcomes_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_id = row['question_id']
            if question_id in resolutions:
                # Store individual model predictions and calculate their Brier scores
                for model in brier_scores.keys():
                    prediction = float(row[f'{model}_final']) / 100
                    if model.startswith('gpt'):
                        question_predictions[question_id]['gpt_preds'].append(prediction)
                    else:
                        question_predictions[question_id]['claude_preds'].append(prediction)
                    brier_score = (resolutions[question_id] - prediction) ** 2
                    brier_scores[model].append(brier_score)

    # Calculate per-question median and mean predictions and their Brier scores
    gpt_median_scores = []
    claude_median_scores = []
    gpt_mean_scores = []
    claude_mean_scores = []
    
    for question_id, preds in question_predictions.items():
        if preds['gpt_preds'] and preds['claude_preds']:  # Ensure we have predictions for both
            resolution = resolutions[question_id]
            
            # Calculate median prediction for each question
            gpt_median_pred = statistics.median(preds['gpt_preds'])
            claude_median_pred = statistics.median(preds['claude_preds'])
            
            # Calculate mean prediction for each question
            gpt_mean_pred = statistics.mean(preds['gpt_preds'])
            claude_mean_pred = statistics.mean(preds['claude_preds'])
            
            # Calculate Brier scores using per-question medians
            gpt_median_scores.append((resolution - gpt_median_pred) ** 2)
            claude_median_scores.append((resolution - claude_median_pred) ** 2)
            
            # Calculate Brier scores using per-question means
            gpt_mean_scores.append((resolution - gpt_mean_pred) ** 2)
            claude_mean_scores.append((resolution - claude_mean_pred) ** 2)

    # Calculate average Brier score and standard error for each model
    average_brier_scores = {}
    for model, scores in brier_scores.items():
        average_brier_scores[model] = {
            'score': sum(scores) / len(scores),
            'se': calculate_standard_error(scores)
        }

    # Calculate ensemble scores (both median and mean)
    ensemble_scores = {
        'GPT median': {
            'score': sum(gpt_median_scores) / len(gpt_median_scores),
            'se': calculate_standard_error(gpt_median_scores)
        },
        'Claude median': {
            'score': sum(claude_median_scores) / len(claude_median_scores),
            'se': calculate_standard_error(claude_median_scores)
        },
        'GPT mean': {
            'score': sum(gpt_mean_scores) / len(gpt_mean_scores),
            'se': calculate_standard_error(gpt_mean_scores)
        },
        'Claude mean': {
            'score': sum(claude_mean_scores) / len(claude_mean_scores),
            'se': calculate_standard_error(claude_mean_scores)
        }
    }

    return brier_scores, average_brier_scores, ensemble_scores

def perform_statistical_tests(brier_scores):
    gpt_scores = [score for model, scores in brier_scores.items() if model.startswith('gpt') for score in scores]
    claude_scores = [score for model, scores in brier_scores.items() if model.startswith('claude') for score in scores]

    # Paired t-test
    t_statistic, p_value = stats.ttest_rel(gpt_scores, claude_scores)

    print("\nStatistical Test Results:")
    print(f"Paired t-test (GPT vs Claude):")
    print(f"t-statistic: {t_statistic:.4f}")
    print(f"p-value: {p_value:.4f}")

    if p_value < 0.05:
        print("The difference between GPT and Claude scores is statistically significant (p < 0.05).")
    else:
        print("The difference between GPT and Claude scores is not statistically significant (p >= 0.05).")

    # Effect size (Cohen's d)
    mean_diff = sum(gpt_scores) / len(gpt_scores) - sum(claude_scores) / len(claude_scores)
    pooled_std = ((len(gpt_scores) - 1) * statistics.stdev(gpt_scores) ** 2 + 
                  (len(claude_scores) - 1) * statistics.stdev(claude_scores) ** 2) / (len(gpt_scores) + len(claude_scores) - 2)
    cohens_d = mean_diff / (pooled_std ** 0.5)

    print(f"\nEffect size (Cohen's d): {cohens_d:.4f}")
    if abs(cohens_d) < 0.2:
        print("The effect size is small.")
    elif abs(cohens_d) < 0.5:
        print("The effect size is medium.")
    else:
        print("The effect size is large.")

# Calculate and print results
brier_scores, average_scores, ensemble_scores = calculate_brier_scores(resolutions_file, outcomes_file)

print("Average Brier Scores (score, standard error):")
for model, result in average_scores.items():
    print(f"{model}: {result['score']:.4f}, {result['se']:.4f}")

print("\nEnsemble Brier Scores (score, standard error):")
for model, result in ensemble_scores.items():
    print(f"{model}: {result['score']:.4f}, {result['se']:.4f}")

# Perform statistical tests
perform_statistical_tests(brier_scores)
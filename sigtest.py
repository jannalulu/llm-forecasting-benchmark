import csv
import statistics
from scipy import stats

resolutions_file = 'aibq3_resolutions.csv'
outcomes_file = 'aibq3_outcomes.csv'

def calculate_brier_scores(resolutions_file, outcomes_file):
    # Read resolutions
    resolutions = {}
    with open(resolutions_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            resolutions[row['question_id']] = int(row['resolution'])

    # Read outcomes and calculate Brier scores
    brier_scores = {model: [] for model in ['gpt0', 'gpt1', 'gpt2', 'gpt3', 'gpt4', 'claude0', 'claude1', 'claude2', 'claude3', 'claude4']}
    
    with open(outcomes_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            question_id = row['question_id']
            if question_id in resolutions:
                resolution = resolutions[question_id]
                for model in brier_scores.keys():
                    prediction = float(row[f'{model}_final']) / 100  # Convert percentage to probability
                    brier_score = (resolution - prediction) ** 2
                    brier_scores[model].append(brier_score)

    # Calculate average Brier score for each model
    average_brier_scores = {model: sum(scores) / len(scores) for model, scores in brier_scores.items()}

    # Calculate median Brier score for GPT and Claude models
    gpt_scores = [average_brier_scores[f'gpt{i}'] for i in range(5)]
    claude_scores = [average_brier_scores[f'claude{i}'] for i in range(5)]
    
    median_scores = {
        'GPT median': statistics.median(gpt_scores),
        'Claude median': statistics.median(claude_scores)
    }

    return brier_scores, average_brier_scores, median_scores

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
brier_scores, average_scores, median_scores = calculate_brier_scores(resolutions_file, outcomes_file)

print("Average Brier Scores:")
for model, score in average_scores.items():
    print(f"{model}: {score:.4f}")

print("\nMedian Brier Scores:")
for model, score in median_scores.items():
    print(f"{model}: {score:.4f}")

# Perform statistical tests
perform_statistical_tests(brier_scores)
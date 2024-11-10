import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve

def create_calibration_plot():
    # Read the predictions and resolutions
    predictions_df = pd.read_csv('aibq3_outcomes_narrative_claude_sonnet.csv')
    resolutions_df = pd.read_csv('aibq3_resolutions.csv')
    
    # Merge predictions with resolutions
    merged_df = predictions_df.merge(resolutions_df, on='question_id')
    
    # Collect predictions and outcomes
    probs = []
    outcomes = []
    for i in range(5):
        probs.extend(merged_df[f'claude{i}_prob'].values / 100)
        outcomes.extend(merged_df['resolution'].values)
    
    # Create bins and calculate frequencies
    bins = np.arange(0, 1.1, 0.1)
    indices = np.digitize(probs, bins) - 1
    freqs = [np.mean(np.array(outcomes)[indices == i]) if np.any(indices == i) else np.nan 
            for i in range(len(bins)-1)]
    
    # Plot
    plt.figure(figsize=(8, 8))
    plt.plot([0, 1], [0, 1], 'k:', label='Perfect calibration')
    plt.plot(bins[:-1] + 0.05, freqs, 's-', label='Observed frequency')
    plt.xlabel('Predicted probability')
    plt.ylabel('Observed frequency')
    plt.title('Calibration Plot')
    plt.legend()
    plt.grid(True)
    plt.savefig('calibration_plot.png')
    plt.close()

def create_prediction_scatterplot():
    # Read the CSV files
    narrative_df = pd.read_csv('aibq3_outcomes_narrative_4o.csv')
    sonnet_df = pd.read_csv('aibq3_outcomes_past_claude_sonnet.csv')
    haiku_df = pd.read_csv('aibq3_outcomes_past_claude_haiku.csv')
    old_sonnet_df = pd.read_csv('aibq3_outcomes_past_4osonnet.csv')
    narrative_sonnet_df = pd.read_csv('aibq3_outcomes_narrative_claude_sonnet.csv')
    
    # Create figure with subplots
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get all predictions from both datasets
    narrative_preds = []
    sonnet_preds = []
    haiku_preds = []
    old_sonnet_preds = []
    narrative_sonnet_preds = []
    
    # Extract predictions from narrative dataset
    for i in range(5):
        narrative_preds.extend(narrative_df[f'gpt{i}_prob'].values)
    
    # Extract predictions from sonnet dataset
    for i in range(5):
        sonnet_preds.extend(sonnet_df[f'claude{i}_final'].values)
        haiku_preds.extend(haiku_df[f'claude{i}_final'].values)
        old_sonnet_preds.extend(old_sonnet_df[f'claude{i}_final'].values)
        narrative_sonnet_preds.extend(narrative_sonnet_df[f'claude{i}_prob'].values)
    
    # Create binned frequency distributions (bins of width 5)
    bins = range(0, 105, 5)  # 0 to 100 in steps of 5
    narrative_hist, bin_edges = np.histogram(narrative_preds, bins=bins)
    sonnet_hist, _ = np.histogram(sonnet_preds, bins=bins)
    haiku_hist, _ = np.histogram(haiku_preds, bins=bins)
    old_sonnet_hist, _ = np.histogram(old_sonnet_preds, bins=bins)
    narrative_sonnet_hist, _ = np.histogram(narrative_sonnet_preds, bins=bins)
    
    # Use bin centers for x-axis
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Create scatter plot using bin centers
    plt.scatter(bin_centers, narrative_hist, alpha=0.5, label='GPT Narrative')
    plt.scatter(bin_centers, sonnet_hist, alpha=0.5, label='Claude Sonnet')
    plt.scatter(bin_centers, haiku_hist, alpha=0.5, label='Claude Haiku')
    plt.scatter(bin_centers, old_sonnet_hist, alpha=0.5, label='Claude Sonnet (Old)')
    plt.scatter(bin_centers, narrative_sonnet_hist, alpha=0.5, label='Claude Sonnet Narrative')
    
    plt.xlabel('Prediction Value (%)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Prediction Values')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig('prediction_distribution.png')
    plt.close()

def create_calibration_plot():
    # Read the predictions and resolutions
    predictions_df = pd.read_csv('aibq3_outcomes_narrative_claude_sonnet.csv')
    resolutions_df = pd.read_csv('aibq3_resolutions.csv')
    
    # Merge predictions with resolutions
    merged_df = predictions_df.merge(resolutions_df, on='question_id')
    
    # Collect all predictions and their corresponding outcomes
    all_probs = []
    all_outcomes = []
    
    for i in range(5):
        probs = merged_df[f'claude{i}_prob'].values / 100  # Convert to probabilities
        outcomes = merged_df['resolution'].values
        all_probs.extend(probs)
        all_outcomes.extend(outcomes)
    
    # Calculate calibration curve
    prob_true, prob_pred = calibration_curve(all_outcomes, all_probs, n_bins=10)
    
    # Create calibration plot
    plt.figure(figsize=(8, 8))
    plt.plot([0, 1], [0, 1], 'k:', label='Perfectly calibrated')
    plt.plot(prob_pred, prob_true, 's-', label='Claude (narrative)')
    
    plt.xlabel('Mean predicted probability')
    plt.ylabel('Fraction of positives')
    plt.title('Calibration Plot')
    plt.legend()
    plt.grid(True)
    
    # Save plot
    plt.savefig('calibration_plot.png')
    plt.close()

def create_calibration_plot():
    # Read the predictions and resolutions
    predictions_df = pd.read_csv('aibq3_outcomes_narrative_claude_sonnet.csv')
    resolutions_df = pd.read_csv('aibq3_resolutions.csv')
    
    # Merge predictions with resolutions
    merged_df = predictions_df.merge(resolutions_df, on='question_id')
    
    # Create bins for predictions
    bins = np.linspace(0, 1, 11)  # 10 equal-sized bins from 0 to 1
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    # Collect all predictions and outcomes
    all_probs = []
    all_outcomes = []
    
    for i in range(5):
        probs = merged_df[f'claude{i}_prob'].values / 100  # Convert to probabilities
        outcomes = merged_df['resolution'].values
        all_probs.extend(probs)
        all_outcomes.extend(outcomes)
    
    # Calculate observed frequencies for each bin
    bin_indices = np.digitize(all_probs, bins) - 1
    observed_freqs = []
    
    for i in range(len(bins) - 1):
        mask = bin_indices == i
        if np.any(mask):
            freq = np.mean(np.array(all_outcomes)[mask])
            observed_freqs.append(freq)
        else:
            observed_freqs.append(np.nan)
    
    # Create calibration plot
    plt.figure(figsize=(8, 8))
    plt.plot([0, 1], [0, 1], 'k:', label='Perfect calibration')
    plt.plot(bin_centers, observed_freqs, 's-', label='Claude (narrative)')
    
    plt.xlabel('Predicted probability')
    plt.ylabel('Observed frequency')
    plt.title('Calibration Plot')
    plt.legend()
    plt.grid(True)
    
    # Save plot
    plt.savefig('calibration_plot.png')
    plt.close()

if __name__ == "__main__":
    create_prediction_scatterplot()
    create_calibration_plot()
    create_calibration_plot()
    create_calibration_plot()

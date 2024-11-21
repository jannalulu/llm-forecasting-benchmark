import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve

def create_prediction_scatterplot():
    # Read the CSV files
    narrative_df = pd.read_csv('../aibq3_outcomes_narrative_4o.csv')
    sonnet_df = pd.read_csv('../aibq3_outcomes_past_claude_sonnet.csv')
    haiku_df = pd.read_csv('../aibq3_outcomes_past_claude_haiku.csv')
    old_sonnet_df = pd.read_csv('../aibq3_outcomes_past_4osonnet.csv')
    narrative_sonnet_df = pd.read_csv('../aibq3_outcomes_narrative_claude_sonnet.csv')
    
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

if __name__ == "__main__":
    create_prediction_scatterplot()

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_calibration_plot():
    # Read the predictions and resolutions
    narrative_claude_df = pd.read_csv('aibq3_outcomes_narrative_claude_sonnet.csv')
    direct_claude_df = pd.read_csv('aibq3_outcomes_past_claude_sonnet.csv')
    old_sonnet_df = pd.read_csv('aibq3_outcomes_past_4osonnet.csv')
    narrative_gpt_df = pd.read_csv('aibq3_outcomes_narrative_4o.csv')
    resolutions_df = pd.read_csv('aibq3_resolutions.csv')
    
    # Create bins for predictions (5% wide)
    bins = np.arange(0, 105, 10) / 100  # Convert to probabilities
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    plt.figure(figsize=(10, 10))
    plt.plot([0, 1], [0, 1], 'k:', label='Perfect calibration')
    
    # Process each model's data
    def plot_model_calibration(df, model_prefix, label, marker, prob_suffix='prob'):
        merged_df = df.merge(resolutions_df, on='question_id')
        all_probs = []
        all_outcomes = []
        
        for i in range(5):
            prob_col = f'{model_prefix}{i}_{prob_suffix}'
            probs = merged_df[prob_col].values / 100
            outcomes = merged_df['resolution'].values
            all_probs.extend(probs)
            all_outcomes.extend(outcomes)
        
        bin_indices = np.digitize(all_probs, bins) - 1
        observed_freqs = []
        
        for i in range(len(bins) - 1):
            mask = bin_indices == i
            if np.any(mask):
                freq = np.mean(np.array(all_outcomes)[mask])
                observed_freqs.append(freq)
            else:
                observed_freqs.append(np.nan)
        
        plt.plot(bin_centers, observed_freqs, marker, label=label)
    
    # Plot each model
    plot_model_calibration(narrative_claude_df, 'claude', 'Claude (narrative)', 's-', 'prob')
    plot_model_calibration(direct_claude_df, 'claude', 'Claude (direct)', 'o-', 'final')
    plot_model_calibration(old_sonnet_df, 'claude', 'Claude (old)', '^-', 'final')
    plot_model_calibration(narrative_gpt_df, 'gpt', 'GPT-4 (narrative)', 'd-', 'prob')
    
    plt.xlabel('Predicted probability')
    plt.ylabel('Observed frequency')
    plt.title('Calibration Plot')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    # Save plot
    plt.savefig('calibration_plot.png', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_calibration_plot()

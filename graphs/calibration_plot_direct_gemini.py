import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_calibration_plot():
    # Read the predictions and resolutions
    direct_claude_df = pd.read_csv('../aibq3_outcomes_past_claude_sonnet.csv')
    old_sonnet_df = pd.read_csv('../aibq3_outcomes_past_4osonnet.csv')
    gpt_df = pd.read_csv('../aibq3_outcomes_past_4osonnet.csv')
    geminiflash_df = pd.read_csv('../aibq4_outcomes_past_gemini_flash2.csv')
    
    # Read both resolution files
    resolutions_aibq3 = pd.read_csv('../aibq3_resolutions.csv')
    resolutions_aibq4 = pd.read_csv('../aibq4_resolutions.csv')
    
    # Create bins for predictions (5% wide)
    bins = np.arange(0, 105, 10) / 100  # Convert to probabilities
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    plt.figure(figsize=(10, 10))
    plt.plot([0, 1], [0, 1], 'k:', label='Perfect calibration')
    
    def plot_model_calibration(df, model_prefix, label, marker, prob_suffix='prob', resolution_file='aibq3'):
        # Choose the appropriate resolution file
        resolutions_df = resolutions_aibq3 if resolution_file == 'aibq3' else resolutions_aibq4
        
        # Merge with the correct resolution file
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
        
        plt.plot(bin_centers, observed_freqs, marker, label=f'{label}')
    
    # Plot each model with appropriate resolution file
    plot_model_calibration(direct_claude_df, 'claude', 'Claude Sonnet (new)', 'o-', 'final', 'aibq3')
    plot_model_calibration(old_sonnet_df, 'claude', 'Claude Sonnet (old)', '^-', 'final', 'aibq3')
    plot_model_calibration(gpt_df, 'gpt', 'GPT-4o', 's-', 'final', 'aibq3')
    plot_model_calibration(geminiflash_df, 'geminiflash2', 'Gemini 2.0 Flash', 'd-', 'final', 'aibq4')
    
    plt.xlabel('Predicted probability')
    plt.ylabel('Observed frequency')
    plt.title('Calibration Plot')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    # Save plot
    plt.savefig('calibration_plot_direct_gemini.png', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_calibration_plot()
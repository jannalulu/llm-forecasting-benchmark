import pandas as pd
from typing import List

def select_random_questions(input_files: List[str] = ['metaculus_data_aibq3_categories.csv', 'metaculus_data_aibq4_categories.csv'], 
                          n: int = 100,
                          output_file: str = 'metaculus_data_subset.csv') -> None:
    """
    Select n random questions from the input files while maintaining category proportions.
    
    Args:
        input_files (List[str]): List of paths to input CSV files
        n (int): Total number of questions to select
        output_file (str): Path to output CSV file
    """
    # Read and combine all input files
    dfs = [pd.read_csv(file) for file in input_files]
    combined_df = pd.concat(dfs)
    
    # Calculate category distribution
    category_dist = combined_df['category'].value_counts(normalize=True)
    print(category_dist)
    
    # Calculate number of samples needed per category
    samples_per_category = (category_dist * n).round().astype(int)
    
    # Adjust if rounding causes total to not equal n
    total_samples = samples_per_category.sum()
    if total_samples != n:
        # Add or subtract the difference from the largest category
        largest_category = category_dist.index[0]
        samples_per_category[largest_category] += (n - total_samples)
    
    # Perform stratified sampling
    selected_questions = []
    for category, num_samples in samples_per_category.items():
        category_questions = combined_df[combined_df['category'] == category]
        if len(category_questions) < num_samples:
            print(f"Warning: Not enough questions in category {category}. Using all available {len(category_questions)} questions.")
            selected = category_questions
        else:
            selected = category_questions.sample(n=num_samples)
        selected_questions.append(selected)
    
    # Combine all selected questions
    result_df = pd.concat(selected_questions)
    
    # Save to output file
    result_df.to_csv(output_file, index=False)
    
    print("Category distribution in sample:")
    print(result_df['category'].value_counts(normalize=True))

if __name__ == "__main__":
    select_random_questions()

import json
import random

def select_random_questions(input_file='metaculus_data_aibq3_wd.json', n=100, output_file='metaculus_data_aibq3_sample.json'):
    """
    Select n random questions from the input file and save them to output file.
    
    Args:
        input_file (str): Path to input JSON file
        n (int): Number of questions to select
        output_file (str): Path to output JSON file
    """
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Check if we have enough questions
    if len(questions) < n:
        print(f"Warning: Input file only contains {len(questions)} questions, which is less than requested {n}")
        n = len(questions)
    
    # Select random questions
    selected_questions = random.sample(questions, n)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(selected_questions, f, indent=2)
    
    print(f"Successfully sampled {n} questions from {input_file}")
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    select_random_questions()

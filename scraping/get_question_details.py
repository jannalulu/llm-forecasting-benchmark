import json
import pandas as pd
from typing import Dict, List

def load_json_file(file_path: str) -> List[Dict]:
    """Load JSON file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_questions(subset_file: str = 'metaculus_data_subset.csv',
                     q3_file: str = 'metaculus_data_aibq3_wd.json',
                     q4_file: str = 'metaculus_data_aibq4_wd.json',
                     output_file: str = 'metaculus_data_subset_wd.json') -> None:
    """
    Extract question details from Q3 and Q4 JSON files based on question IDs in subset file.
    
    Args:
        subset_file (str): Path to CSV file containing selected question IDs
        q3_file (str): Path to Q3 tournament JSON file
        q4_file (str): Path to Q4 tournament JSON file
        output_file (str): Path to output JSON file
    """
    subset_df = pd.read_csv(subset_file)
    question_ids = set(subset_df['question_id'].astype(str))
    
    q3_data = load_json_file(q3_file)
    q4_data = load_json_file(q4_file)
    
    q3_dict = {str(q['id']): q for q in q3_data}
    q4_dict = {str(q['id']): q for q in q4_data}
    
    # Extract questions that match subset
    selected_questions = []
    for qid in question_ids:
        if qid in q3_dict:
            selected_questions.append(q3_dict[qid])
        elif qid in q4_dict:
            selected_questions.append(q4_dict[qid])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(selected_questions, f, indent=2)
    
    print(f"Extracted {len(selected_questions)} questions, written to {output_file}")

if __name__ == "__main__":
    extract_questions()

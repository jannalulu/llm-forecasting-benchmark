import json
import os
import re
import csv
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash-002")

BATCH_SIZE = 25

def categorize_batch(batch):
    prompt = """For each item in the following JSON array, assign a category from these options:
    ['Science & Tech',
    'Healthcare & Biology', 
    'Economics & Business',
    'Environment & Energy',
    'Politics & Governance',
    'Arts & Recreation',
    'Sports',
    'Other']

    Rules:
    1. For each item, output the question_id and category in this exact format:
       {id}: {category}
    2. Output one item per line, nothing else.
    3. You cannot skip any items, you must categorize all of them.
    4. Use exactly the categories listed above, no variations.

    Example output format:
    12345: Science & Tech
    67890: Healthcare & Biology

    Here is the data to categorize:

    """
    prompt += json.dumps(batch)

    try:
        response = model.generate_content(prompt)
        print(f"Raw response: {response.text}")  # Debug print
        
        if response.text:
            # Parse lines into id-category pairs
            results = []
            lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            
            for line in lines:
                try:
                    # Split on first colon to handle cases where category might contain colons
                    id_part, category = line.split(':', 1)
                    question_id = id_part.strip()
                    category = category.strip()
                    results.append({'id': question_id, 'category': category})
                except ValueError:
                    print(f"Warning: Could not parse line: {line}")
                    continue
            
            print(f"Parsed results: {results}")
            
            # Create a mapping of id to category from the response
            category_map = {str(item['id']): item['category'] for item in results}
            
            # Map back to original batch items, using None for any missing IDs
            final_results = []
            for item in batch:
                category = category_map.get(str(item['id']))
                if not category:
                    print(f"Warning: No category found for ID {item['id']}")
                final_results.append({'id': item['id'], 'category': category})
            
            return final_results
        else:
            print("Error: Empty response from the model")
            return [{'id': item['id'], 'category': None} for item in batch]
    except Exception as e:
        print(f"Error during categorization: {e}")
        return [{'id': item['id'], 'category': None} for item in batch]

def process_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    output_file = 'metaculus_data_aibq4_categories.csv'
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['question_id', 'category'])
        
        current_batch = []
        processed_count = 0
        
        for i, item in enumerate(data):
            current_batch.append(item)
            
            if len(current_batch) >= BATCH_SIZE or i == len(data) - 1:
                print(f"\nProcessing batch of {len(current_batch)} items")
                categorized_batch = categorize_batch(current_batch)
                
                for item in categorized_batch:
                    print(f"Writing: {item['id']} - {item['category']}")  # Debug print
                    writer.writerow([item['id'], item['category']])
                    processed_count += 1
                
                current_batch = []

        print(f"Categorization complete. Processed {processed_count} items. Results saved in '{output_file}'")

if __name__ == "__main__":
    process_json_file('metaculus_data_aibq4_wd.json')
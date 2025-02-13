import json
import os
import sys
import logging
from models import CLAUDE_MODEL, get_baseline_claude_prediction
from models import GPT_MODEL, get_baseline_gpt_prediction
from models import GEMINI_MODEL, get_baseline_gemini_prediction
from models import DEEPSEEK_MODEL, get_baseline_deepseek_prediction

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler("baseline_forecasting.log", mode='a', encoding='utf-8'),
    logging.StreamHandler(sys.stdout)
  ]
)

def setup_question_logger(question_id, model_name):
  """Set up a logger for a specific question and model."""
  log_filename = f"logs/baseline_{question_id}_{model_name}_past.log" # test
  logger = logging.getLogger(f"{question_id}_{model_name}")
  logger.setLevel(logging.INFO)
  file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  return logger

def log_question_reasoning(question_id, reasoning, question_title, model_name, run_number):
  """Log the reasoning for a specific question and run."""
  logger = setup_question_logger(question_id, model_name)
  logger.info(f"Question: {question_title}")
  logger.info(f"Run {run_number}:\n{reasoning}\n")

def list_questions():
  """Get questions and resolution_criteria, fine_print, open_time, title, and id from scraping/metaculus_data_aibq3_wd.json"""
  with open('scraping/metaculus_data_subset_wd.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
  return [
    {
      'id': item['id'],
      'title': item['title'],
      'resolution_criteria': item.get('resolution_criteria', ''),
      'fine_print': item.get('fine_print', ''),
      'open_time': item['open_time'],
    }
    for item in data
  ]


def log_questions_json(questions_data):
  """Log question predictions to a JSON file."""
  json_filename = "baseline_predictions_claude_sonnet.json" # test
  logging.info(f"Adding {len(questions_data)} items to the collection")
  
  try:
    if os.path.exists(json_filename):
      with open(json_filename, 'r', encoding='utf-8') as json_file:
        existing_data = json.load(json_file)
    else:
      existing_data = []
    
    # Update existing entries or add new ones
    for new_entry in questions_data:
      existing_entry = next((item for item in existing_data if item["question_id"] == new_entry["question_id"]), None)
      if existing_entry:
        existing_entry.update(new_entry)
      else:
        existing_data.append(new_entry)
  
    # Write all questions to the JSON file
    with open(json_filename, 'w', encoding='utf-8') as json_file:
      json.dump(existing_data, json_file, ensure_ascii=False, indent=2)
    
    logging.info(f"Successfully wrote {len(existing_data)} total items to {json_filename}")
  except Exception as e:
      logging.error(f"Error writing to {json_filename}: {str(e)}")

def main():
  questions = list_questions()
  batch_questions_data = []

  for question in questions:
    question_id = question['id']
    print(f"Processing question id: {question_id}\n\n")
    
    question_data = {
      "question_id": question_id,
      "question_title": question['title']
    }
    
    for run in range(1):
      print(f"Run {run} for question {question_id}")
      
      llm_result = get_baseline_claude_prediction(question) # get_"llm"_prediction
      print(f"{CLAUDE_MODEL} response (Run {run}): {llm_result}")
      log_question_reasoning(question_id, llm_result, question['title'], CLAUDE_MODEL, run)

      question_data[f"{CLAUDE_MODEL}_reasoning"] = llm_result

    batch_questions_data.append(question_data)

    # Write to JSON after each question
    logging.info(f"Writing batch of {len(batch_questions_data)} entries to JSON")
    log_questions_json(batch_questions_data)
    batch_questions_data = []

if __name__ == "__main__":
    main()
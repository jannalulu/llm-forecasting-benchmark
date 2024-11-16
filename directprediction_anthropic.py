import json
import os
import sys
import logging
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from prompts import DIRECT_PREDICTION

load_dotenv()

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler("forecasting.log", mode='a', encoding='utf-8'),
    logging.StreamHandler(sys.stdout)
  ]
)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

def setup_question_logger(question_id, model_name):
  """Set up a logger for a specific question and model."""
  log_filename = f"logs/{question_id}_{model_name}_past.log"
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
  """Get questions and resolution_criteria, fine_print, open_time, title, and id from scraping/metaculus_data_aibq3_nosolution.json"""
  with open('scraping/metaculus_data_aibq3_wd.json', 'r', encoding='utf-8') as f:
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

def get_news_for_question(question_id):
  """Get news articles for a specific question ID from aibq3_news.json"""
  with open('aibq3_news.json', 'r', encoding='utf-8') as f:
    news_data = json.load(f)
  for item in news_data:
    if item['question_id'] == question_id:
      return item['news']
  return "No news found for this question."

def get_claude_prediction(question_details, formatted_articles):
   
  prompt_input = {
    "title": question_details["title"],
    "background": question_details.get("background", ""),
    "resolution_criteria": question_details.get("resolution_criteria", ""),
    "fine_print": question_details.get("fine_print", ""),
    "formatted_articles": formatted_articles,
    "today": question_details["open_time"]
  }

  client = Anthropic(api_key=ANTHROPIC_API_KEY)

  max_retries = 10
  base_delay = 1

  for attempt in range(max_retries):
    try:
      response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=4096,
        messages=[
          {"role": "user", "content": DIRECT_PREDICTION.format(**prompt_input)}
        ]
      )
      claude_text = response.content[0].text
      return claude_text
    except Exception as e:
      if attempt < max_retries - 1:
        delay = base_delay * (2 ** attempt)  # Exponential backoff
        logging.warning(f"Claude API error on attempt {attempt + 1}/{max_retries}. Retrying in {delay} seconds... Error: {e}")
        time.sleep(delay)
      else:
        logging.error(f"Claude API error persisted after {max_retries} retries: {e}")
        return None

def log_questions_json(questions_data):
  """Log question predictions to a JSON file."""
  json_filename = "aibq3_predictions_past_claude_haiku.json"
  logging.info(f"Adding {len(questions_data)} items to the collection")
  
  try:
    # Read existing data if file exists
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
    
    formatted_articles = get_news_for_question(question_id)
    
    question_data = {
      "question_id": question_id,
      "question_title": question['title']
    }
    
    for run in range(5):
      print(f"Run {run} for question {question_id}")
      
      claude_result = get_claude_prediction(question, formatted_articles)
      print(f"Haiku response (Run {run}): {claude_result}")
      log_question_reasoning(question_id, claude_result, question['title'], "Haiku 3-5-new", run)

      question_data[f"claude_reasoning{run}"] = claude_result

    batch_questions_data.append(question_data)

    # Write to JSON after each question
    logging.info(f"Writing batch of {len(batch_questions_data)} entries to JSON")
    log_questions_json(batch_questions_data)
    batch_questions_data = []

if __name__ == "__main__":
    main()
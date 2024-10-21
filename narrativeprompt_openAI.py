import json
import os
import sys
import logging
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

load_dotenv()

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler("forecasting_narrative.log", mode='a', encoding='utf-8'),
    logging.StreamHandler(sys.stdout)
  ]
)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

def setup_question_logger(question_id, model_name):
  """Set up a logger for a specific question and model."""
  log_filename = f"logs_testrun/narrative_{question_id}_{model_name}.log" #remove test_run
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
  with open('scraping/test_metaculus_data_aibq3_wd.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
  return [
    {
      'id': item['id'],
      'title': item['title'],
      'resolution_criteria': item.get('resolution_criteria', ''),
      'background': item.get('background', ''),
      'fine_print': item.get('fine_print', ''),
      'open_time': item['open_time'],
    }
    for item in data
  ]

def get_news_for_question(question_id):
  """Get news articles for a specific question ID from aibq3_news.json"""
  with open('aibq3_news_limited.json', 'r', encoding='utf-8') as f: #change to aibq3_news for actual run
    news_data = json.load(f)
  for item in news_data:
    if item['question_id'] == question_id:
      return item['news']
    return "No news found for this question."

# Prompt
PROMPT_NARRATIVE_PREDICTION = """
  Write a brief fictional narrative scene set the day after the event described in the following question:
  "{title}"

  The scene should be a conversation between two experts discussing the event. The event may not have occurred. 

  The scene is set the day after the potential event. The title contains the date for which the event should have occurred. If the title says "would x occur by September 10th?", the scene is set on September 11.  
  Keep the parameters of the story in mind: {resolution_criteria}
  Background: {background}
  Additional context: {fine_print}

  Give the two experts real names of actual experts based on the context of the question and have them briefly discuss what actually happened based on the information provided. For example, the character should be Jerome Powell telling us about inflation numbers if the {title} asked about inflation percentages. 
  The scene should be written in a screenplay format. It should be less than 100 words.
"""

#GPT-4 predictions
def get_gpt_prediction(question_details, formatted_articles):
  client = OpenAI(api_key=OPENAI_API_KEY)

  prompt_input = {
    "title": question_details["title"],
    "background": question_details.get("background", ""),
    "resolution_criteria": question_details.get("resolution_criteria", ""),
    "fine_print": question_details.get("fine_print", ""),
    "formatted_articles": formatted_articles
  }

  try:
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "user", "content": PROMPT_NARRATIVE_PREDICTION.format(**prompt_input)}
      ]
    )
    gpt_text = response.choices[0].message.content
    return gpt_text
  except Exception as e:
    print(f"Error in GPT prediction: {e}")
    return None

def log_questions_json(questions_data):
  """Log question predictions to a JSON file."""
  json_filename = "test_aibq3_narrative_predictions_4o.json" #change when not testing
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
    
    for run in range(10):
      print(f"Run {run} for question {question_id}")
      
      gpt_result = get_gpt_prediction(question, formatted_articles)
      print(f"4o response (Run {run}): {gpt_result}")
      
      log_question_reasoning(question_id, gpt_result, question['title'], "4o", run)

      question_data[f"gpt_reasoning{run}"] = gpt_result

    batch_questions_data.append(question_data)

    # Write to JSON after each question
    logging.info(f"Writing batch of {len(batch_questions_data)} entries to JSON")
    log_questions_json(batch_questions_data)
    batch_questions_data = []

if __name__ == "__main__":
    main()
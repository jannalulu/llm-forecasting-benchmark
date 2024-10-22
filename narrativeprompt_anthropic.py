import json
import os
import sys
import logging
from dotenv import load_dotenv
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
  log_filename = f"logs/{question_id}_reasoning_{model_name}_narrative.log"
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
      'background': item.get('background', ''),
      'fine_print': item.get('fine_print', ''),
      'open_time': item['open_time'],
      'scheduled_resolve_time': item['scheduled_resolve_time']
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

# Prompt
PROMPT_NARRATIVE_PREDICTION = """
  You are a talented script writer for a movie about predicting probabilities of something happening in the future, but with a twist. Here are the rules:
  1. The event is described in question form: {title}.
  2. The parameters of the story is determined by the {resolution_criteria}.
  3. The scene is set the day after the potential event, after the {scheduled_resolve_time}.
  4. The superforecasters, Nate Silver and Philip Tetlock, talk about the event as if it has or has not happened. The event may not occur. 
  5. The superforecasters only get news articles up to a certain date, the {date}.
  6. The superforecaster models are extremely accurate and have good Brier scores. The models are NEVER wrong. The probabilities given by the superforecaster reflects the reality of actually happened. Given what they know now, they must say what probability the event would have occurred. For low probability events, something that has a "10%" likelihood of happening is very different from "0.1%". 
  7. The superforecaster says that "our models had it at ZZ.ZZ%." 
  8. Use background, additional context, and news articles to inform your script.
    {background}, {fine_print}, {formatted_articles}
  9. The script should be less than 150 words.
"""

def get_claude_prediction(question_details, formatted_articles):
   
  prompt_input = {
    "title": question_details["title"],
    "background": question_details.get("background", ""),
    "resolution_criteria": question_details.get("resolution_criteria", ""),
    "fine_print": question_details.get("fine_print", ""),
    "formatted_articles": formatted_articles,
    "date": question_details["open_time"],
    "scheduled_resolve_time": question_details["scheduled_resolve_time"]
  }

  client = Anthropic(api_key=ANTHROPIC_API_KEY)

  try:
    response = client.messages.create(
      model="claude-3-5-sonnet-20241022",
      max_tokens=4096,
      temperature=0.5,
      messages=[
        {"role": "user", "content": PROMPT_NARRATIVE_PREDICTION.format(**prompt_input)}
      ]
    )
    claude_text = response.content[0].text
    return claude_text
  except Exception as e:
    print(f"Error in Claude prediction: {e}")
    return None

def log_questions_json(questions_data):
  """Log question predictions to a JSON file."""
  json_filename = "aibq3_predictions_narrative_claude_sonnet.json"
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
    
    for run in range(3):
      print(f"Run {run} for question {question_id}")

      claude_result = get_claude_prediction(question, formatted_articles)
      print(f"Sonnet response (Run {run}): {claude_result}")
      
      log_question_reasoning(question_id, claude_result, question['title'], "Sonnet3-5-new", run)

      question_data[f"claude_reasoning{run}"] = claude_result

    batch_questions_data.append(question_data)

    # Write to JSON after each question
    logging.info(f"Writing batch of {len(batch_questions_data)} entries to JSON")
    log_questions_json(batch_questions_data)
    batch_questions_data = []

if __name__ == "__main__":
    main()
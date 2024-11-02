import json
import os
import sys
import logging
from dotenv import load_dotenv
from openai import OpenAI

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
  log_filename = f"logs/{question_id}_{model_name}_past_conf.log"
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

# Prompt
PROMPT_DIRECT_PREDICTION = """
You are a superforecaster who has a strong track record of accurate forecasting. You evaluate past data and trends carefully for potential clues to future events, while recognising that the past is an imperfect guide to the future so you will need to put probabilities on possible future outcomes (ranging from 0 to 100%). Your specific goal is to maximize the accuracy of these probability judgments by minimising the Brier scores that your probability judgments receive once future outcomes are known.
Brier scores have two key components:
1. calibration (across all questions you answer, the probability estimates you assign to possible future outcomes should correspond as closely as possible to the objective frequency with which outcomes occur).
2. resolution (across all questions, aim to assign higher probabilities to events that occur than to events that do not occur).

The question that you are forecasting as well as some background information and resolution criteria are below. 

Your question is:
{title}

The Resolution Criteria for the question is:
{resolution_criteria}

You found the following news articles related to the question:
{formatted_articles}

background:
{background}

fine print:
{fine_print}

Today is {today}.

Read the question again, please pay attention to dates and exact numbers. Work through each step before making your prediction. Double-check whether your prediction makes sense before stating ZZ.ZZ% is the most likely.
Carefully outline your reasons for each forecast: list the strongest evidence and arguments for making lower or higher estimates and explain how you balance the evidence to make your own forecast. You begin this analytic process by looking for reference or comparison classes of similar events and grounding your initial estimates in base rates of occurrence (how often do events of this sort occur in situations that look like the present one?). You then adjust that initial estimate in response to the latest news and distinctive features of the present situation, recognising the need for flexible adjustments but also the risks of over-adjusting and excessive volatility. Superforecasting requires weighing the risks of opposing errors: e.g., of failing to learn from useful historical patterns vs. over-relying on misleading patterns. In this process of error balancing, you draw on the 10 commandments of superforecasting (Tetlock & Gardner, 2015) as well as on other peer-reviewed research on superforecasting.
1. Triage and reference relevant predictions from humans if they exist, such as FiveThirtyEight, Polymarket, and Metaculus.
2. Break seemingly intractable problems into tractable sub-problems.
3. Strike the right balance between inside and outside views.
4. Strike the right balance between under- and overreacting to evidence.
5. Look for the clashing causal forces at work in each problem.
6. Extrapolate the current trends linearly.
7. Strive to distinguish as many degrees of doubt as the problem permits but no more.
8. Strike the right balance between under- and overconfidence, between prudence and decisiveness.
9. Look for the errors behind your mistakes but beware of rearview-mirror hindsight biases.

Once you have written your reasons, ensure that they directly inform your forecast; please make sure that you're answering the {title}. Then, you will provide a forecast between 0.10 and 99.90 (up to 2 decimal places) that is your best prediction of the event, and your level of confidence in it. 
Output your prediction as "My Prediction: ZZ.ZZ% being the most likely, with XX.XX% confidence. Probability: ZZ.ZZ%." Please not add anything after. 

"""

#GPT-4 predictions
def get_gpt_prediction(question_details, formatted_articles):
  client = OpenAI(api_key=OPENAI_API_KEY)

  prompt_input = {
    "title": question_details["title"],
    "background": question_details.get("background", ""),
    "resolution_criteria": question_details.get("resolution_criteria", ""),
    "fine_print": question_details.get("fine_print", ""),
    "formatted_articles": formatted_articles,
    "today": question_details["open_time"]
  }

  try:
    response = client.chat.completions.create(
      model="gpt-4o",
      max_tokens = 4096,
      messages=[
        {"role": "user", "content": PROMPT_DIRECT_PREDICTION.format(**prompt_input)}
      ]
    )
    gpt_text = response.choices[0].message.content
    return gpt_text
  except Exception as e:
    print(f"Error in GPT prediction: {e}")
    return None


def log_questions_json(questions_data):
  """Log question predictions to a JSON file."""
  json_filename = "aibq3_predictions_conf_4o.json"
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
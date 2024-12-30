import os
import time
import logging
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv
from prompts import DIRECT_PREDICTION
from prompts import NARRATIVE_PREDICTION

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GEMINI_API_KEY= os.environ.get('GEMINI_API_KEY')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

CLAUDE_MODEL = "claude-3-5-haiku-20241022"
GPT_MODEL = "gpt-4o"
GEMINI_MODEL = "gemini-exp-1206"
DEEPSEEK_MODEL = "deepseek-chat" # deepseek-chat-v3

max_retries = 10
base_delay = 2

def get_claude_prediction(question_details, formatted_articles):
  client = Anthropic(api_key=ANTHROPIC_API_KEY)

  prompt_input = {
    "title": question_details["title"],
    "background": question_details.get("background", ""),
    "resolution_criteria": question_details.get("resolution_criteria", ""),
    "fine_print": question_details.get("fine_print", ""),
    "formatted_articles": formatted_articles,
    "today": question_details["open_time"]
  }

  for attempt in range(max_retries):
    try:
      response = client.messages.create(
        model=CLAUDE_MODEL,
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

  for attempt in range(max_retries):
    try:
      response = client.chat.completions.create(
        model=GPT_MODEL,
        max_tokens = 4096,
        messages=[
          {"role": "user", "content": DIRECT_PREDICTION.format(**prompt_input)}
        ]
      )
      gpt_text = response.choices[0].message.content
      return gpt_text
    
    except Exception as e:
      if attempt < max_retries - 1:
        delay = base_delay * (2 ** attempt)  # Exponential backoff
        logging.warning(f"GPT API error on attempt {attempt + 1}/{max_retries}. Retrying in {delay} seconds... Error: {e}")
        time.sleep(delay)
      else:
        logging.error(f"GPT API error persisted after {max_retries} retries: {e}")
        return None

def get_gemini_prediction(question_details, formatted_articles):
  client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
  )

  prompt_input = {
    "title": question_details["title"],
    "background": question_details.get("background", ""),
    "resolution_criteria": question_details.get("resolution_criteria", ""),
    "fine_print": question_details.get("fine_print", ""),
    "formatted_articles": formatted_articles,
    "today": question_details["open_time"]
  }

  for attempt in range(max_retries):
    try:
      response = client.chat.completions.create(
        model=GEMINI_MODEL,
        max_tokens = 4096,
        messages=[
          {"role": "user", "content": DIRECT_PREDICTION.format(**prompt_input)}
        ]
      )
      gemini_text = response.choices[0].message.content
      return gemini_text
    except Exception as e:
      if attempt < max_retries - 1:
        delay = base_delay * (2 ** attempt)  # Exponential backoff
        logging.warning(f"Gemini API error on attempt {attempt + 1}/{max_retries}. Retrying in {delay} seconds... Error: {e}")
        time.sleep(delay)
      else:
        logging.error(f"Gemini API error persisted after {max_retries} retries: {e}")
        return None

def get_deepseek_prediction(question_details,formatted_articles):

  client = OpenAI(
    api_key=DEEPSEEK_API_KEY, 
    base_url="https://api.deepseek.com"
  )

  prompt_input = {
  "title": question_details["title"],
  "background": question_details.get("background", ""),
  "resolution_criteria": question_details.get("resolution_criteria", ""),
  "fine_print": question_details.get("fine_print", ""),
  "formatted_articles": formatted_articles,
  "today": question_details["open_time"]
  }

  for attempt in range(max_retries):
    try:
      response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        max_tokens = 8000,
        messages=[
          {"role": "user", "content": DIRECT_PREDICTION.format(**prompt_input)}
        ],
        stream=False
      )
      
      deepseek_text = response.choices[0].message.content
      return deepseek_text
    except Exception as e:
      if attempt < max_retries - 1:
        delay = base_delay * (2 ** attempt)  # Exponential backoff
        logging.warning(f"Deepseek API error on attempt {attempt + 1}/{max_retries}. Retrying in {delay} seconds... Error: {e}")
        time.sleep(delay)
      else:
        logging.error(f"Deepseek API error persisted after {max_retries} retries: {e}")
        return None


def get_claude_prediction_narrative(question_details, formatted_articles):
   
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

  for attempt in range(max_retries):
    try:
      response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        temperature=0.5,
        messages=[
          {"role": "user", "content": NARRATIVE_PREDICTION.format(**prompt_input)}
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

def get_gpt_prediction_narrative(question_details, formatted_articles):
  client = OpenAI(api_key=OPENAI_API_KEY)

  prompt_input = {
    "title": question_details["title"],
    "background": question_details.get("background", ""),
    "resolution_criteria": question_details.get("resolution_criteria", ""),
    "fine_print": question_details.get("fine_print", ""),
    "formatted_articles": formatted_articles,
    "date": question_details["open_time"],
    "scheduled_resolve_time": question_details["scheduled_resolve_time"]
  }

  try:
    response = client.chat.completions.create(
      model="gpt-4o",
      temperature=0.5,
      messages=[
        {"role": "user", "content": NARRATIVE_PREDICTION.format(**prompt_input)}
      ]
    )
    gpt_text = response.choices[0].message.content
    return gpt_text
  except Exception as e:
    print(f"Error in GPT prediction: {e}")
    return None

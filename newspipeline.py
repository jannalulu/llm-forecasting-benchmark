import json
import os
from asknews_sdk import AskNewsSDK
import time
from asknews_sdk.errors import APIError
import sys
import logging
import datetime
from dotenv import load_dotenv

load_dotenv()

log_filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler("newspipelineq3.log", mode='a', encoding='utf-8'),
    logging.StreamHandler(sys.stdout)
  ]
)

ASKNEWS_CLIENT_ID = os.environ.get('ASKNEWS_CLIENT_ID')
ASKNEWS_SECRET = os.environ.get('ASKNEWS_SECRET')

def setup_question_logger(question_id, log_type):
  """Set up a logger for a specific question and log type."""
  log_filename = f"logs/{question_id}_{log_type}.log"
  logger = logging.getLogger(f"{question_id}_{log_type}")
  logger.setLevel(logging.INFO)
  file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  return logger

def log_question_news(question_id, news, question_title):
  """Log the news articles for a specific question."""
  logger = setup_question_logger(question_id, "news")
  logger.info(f"Question: {question_title}")
  logger.info(f"News articles for question {question_id}:\n{news}")

# Get questions ID, title, and open_time from scraped metaculus data
def list_questions():
  with open('scraping/metaculus_data_aibq3_nosolution.json', 'r') as f:
    data = json.load(f)
  return [
    {
      'id': item['id'],
      'title': item['title'],
      'open_time': item['open_time'],
    }
    for item in data
  ]

# AskNews API call to get news
def asknews_api_call_with_retry(func, *args, **kwargs):
  max_retries = 3
  base_delay = 1
  for attempt in range(max_retries):
    try:
      return func(*args, **kwargs)
    except APIError as e:
      if e.error_code == 500000:
        if attempt < max_retries - 1:
          delay = base_delay * (2 ** attempt)
          logging.warning(f"AskNews API Internal Server Error. Retrying in {delay} seconds...")
          time.sleep(delay)
        else:
          logging.error("AskNews API Internal Server Error persisted after max retries.")
          raise
      else:
        raise


def get_formatted_asknews_context(query, news_date, ask, news_logger):
  try:
    question_open_date = datetime.datetime.strptime(question_open_date, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp = int(question_open_date.replace(hour=23, minute=59, second=59).timestamp()) # End timestamp is set to the end of the day of the question's open date
    start_timestamp = int((question_open_date - datetime.timedelta(days=89)).replace(hour=0, minute=0, second=0).timestamp())

    hot_response = asknews_api_call_with_retry(
      ask.news.search_news,
      query=query,
      n_articles=5,
      return_type="both",
      strategy="default",
      method="kw",
      start_timestamp=start_timestamp,
      end_timestamp=end_timestamp,
      historical=True
    )

    historical_response = asknews_api_call_with_retry(
      ask.news.search_news,
      query=query,
      historical=True,
      n_articles=50,
      return_type="both",
      strategy="default",
      method="kw",
      start_timestamp=start_timestamp,
      end_timestamp=end_timestamp
    )

    formatted_articles = format_asknews_context(hot_response.as_dicts, historical_response.as_dicts)
    news_logger.info(f"Formatted articles for {news_date}:\n{formatted_articles}")
    return formatted_articles
  except APIError as e:
    logging.error(f"AskNews API error: {e}")
    return "Error fetching news articles. Please try again later."

def format_asknews_context(hot_articles, historical_articles):
  formatted_articles = "Here are the relevant news articles:\n\n"

  for articles in [hot_articles, historical_articles]:
    if articles:
      articles = sorted([article.__dict__ for article in articles], key=lambda x: x['pub_date'], reverse=True)
      for article in articles:
        pub_date = article["pub_date"].strftime("%B %d, %Y %I:%M %p")
        formatted_articles += f"**{article['eng_title']}**\n{article['summary']}\nOriginal language: {article['language']}\nPublish date: {pub_date}\nSource:[{article['source_id']}]({article['article_url']})\n\n"

  if not hot_articles and not historical_articles:
      formatted_articles += "No articles were found.\n\n"

  return formatted_articles

def main():
  ask = AskNewsSDK(client_id=ASKNEWS_CLIENT_ID, client_secret=ASKNEWS_SECRET, scopes=["news"])
  questions = list_questions()

  for question in questions:
    question_id = question['id']
    print(f"Processing question id: {question_id}\n\n")
    
    news_logger = setup_question_logger(question_id, "news")
    formatted_articles = get_formatted_asknews_context(question['title'], question['open_time'], ask, news_logger)
    log_question_news(question_id, formatted_articles, question['title'])
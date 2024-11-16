import json
import os
import time
from dotenv import load_dotenv
import requests
from requests.exceptions import Timeout, RequestException

load_dotenv()

API_BASE_URL = "https://www.metaculus.com/api2"
MAX_RETRIES = 3
RETRY_DELAY = 5 # Retry after 5 seconds

def make_request_with_retry(url, headers=None, params=None):
	for attempt in range(MAX_RETRIES):
		try:
			response = requests.get(url, headers=headers, params=params, timeout=30)
			response.raise_for_status()
			return response
		except Timeout:
			if attempt < MAX_RETRIES - 1:
				print(f"Request timed out. Retrying in {RETRY_DELAY} seconds...")
				time.sleep(RETRY_DELAY)
			else:
				print(f"Max retries reached. Unable to complete request to {url}")
				raise
		except RequestException as e:
			print(f"An error occurred: {e}")
			raise

def get_question_details(question_id):
	"""
	Get all details about a specific question.
	"""
	url = f"{API_BASE_URL}/questions/{question_id}/"
	response = make_request_with_retry(url)
	return response.json()

def list_questions(tournament_id=3349, count=None):
	"""
	Get all resolved binary questions with specified fields
	"""
	offset = 0
	all_questions = []
	while True:
		url_params = {
			"limit": 100, 
			"offset": offset,
			"order_by": "-activity",
			"project": tournament_id,
		}
		url = f"{API_BASE_URL}/questions/"
		try:
			response = make_request_with_retry(url, params=url_params)
			data = response.json()
			questions = data.get('results', [])
			
			for question in questions:
				try:
					question_details = get_question_details(question['id'])

					if question_details["status"] == "resolved" and question_details["question"].get("type", "") == "binary" and question_details["question"].get("resolution", "") not in ["ambiguous", "annulled"]:
						filtered_question = {
							"title": question_details["title"],
							"id": question_details["id"],
							"background": question_details["question"].get("description", ""),
							"open_time": question_details["open_time"],
							"actual_close_time": question_details["actual_close_time"], # Time the question closes
							"scheduled_resolve_time": question_details["scheduled_resolve_time"], # Time the question is scheduled to resolve
							"actual_resolve_time": question_details["question"]["actual_resolve_time"], # Time the question is actually resolved
							"status": question_details["status"],
							"type": question_details["question"].get("type", ""),
							"resolution_criteria": question_details["question"].get("resolution_criteria", ""),
							"resolution": question_details["question"].get("resolution", ""),
							"fine_print": question_details["question"].get("fine_print", ""),
						}
						
						all_questions.append(filtered_question)
						print(f"Processed question: {filtered_question}")
				
				except RequestException as e:
					print(f"Error processing question {question['id']}: {e}")
					continue

				if count and len(all_questions) >= count:
					return all_questions
			
			if not questions:
				break
			
			offset += len(questions)
		except RequestException as e:
			print(f"Error fetching questions: {e}")
			break
	
	return all_questions

def write_to_json(filename="metaculus_data_aibq3_wd.json"):
	processed_questions = list_questions()
	with open(filename, 'w', encoding='utf-8') as f:
		json.dump(processed_questions, f)
		
if __name__ == "__main__":
	write_to_json()
	with open('metaculus_data_aibq3_wd.json', 'r') as f:
		data = json.load(f)
		print(f"Successfully scraped {len(data)} questions.")
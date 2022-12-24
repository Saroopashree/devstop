# %%
import logging
import random
import time

import requests
from html2text import HTML2Text
from pymongo import UpdateOne

from utils import BotType, DataSource, DBClients, get_log_file_path

logging.basicConfig(filename=get_log_file_path(BotType.crawler, DataSource.so), level=logging.INFO)

# %%
def paginate_so_questions():
    so_filter = "filter=!7bj2fvS8F(e5DHF6SkdVr)n0uzJ9Q2bYEVWc_qE1rKih4w040.AF2-OvhpRKh_lPvubmGrzFxDr(Msqe"
    api_key = "key=U4DMV*8nvpm3EOpvf69Rxw(("
    URL = "https://api.stackexchange.com/2.3/questions?site=stackoverflow&tagged=python&order=desc&sort=votes&"

    page = 1
    while True:
        try:
            logging.info(f"Gettting page {page}")
            req_url = "&".join([URL, api_key, so_filter, f"page={page}", "pagesize=100"])
            result = requests.get(req_url)
            json_result = result.json()

            if result.status_code != 200 or json_result.get("error_id") is not None:
                raise Exception(f"Error in request\nPage: {page}\nJson: {json_result}")

            yield json_result["items"]

            if json_result["has_more"] == False:
                logging.info("Obtained all questions")
                break

            if json_result["quota_remaining"] == 0:
                logging.info("Quota exceeded")
                break

            if json_result.get("backoff"):
                logging.info("Backoff restriction provided")
                time.sleep(json_result["backoff"])

            page += 1
        except Exception as e:
            raise e


# %%
def crawl():
    logging.info("Crawler starts!\n\n")
    logging.info("Starting to collect SO questions")
    client = DBClients.mongo_client()
    logging.info("Obtained mongo client")

    html_handler = HTML2Text()
    html_handler.ignore_links = True

    num_questions = 1
    for page in paginate_so_questions():
        bulk_ops = []
        for question in page:
            # Set _id field to question_id
            question["_id"] = question["question_id"]
            del question["question_id"]

            # Change html body to plain text in question, comments and answers
            question["body"] = html_handler.handle(question["body"])
            question["comments"] = question.get("comments", [])
            question["answers"] = question.get("answers", [])
            for comment in question["comments"]:
                comment["body"] = html_handler.handle(comment["body"])
            for answer in question["answers"]:
                answer["body"] = html_handler.handle(answer["body"])

            bulk_ops.append(UpdateOne({"_id": question["_id"]}, {"$set": question}, upsert=True))

        if bulk_ops:
            client["devstop"]["so_questions"].bulk_write(bulk_ops)
        num_questions += len(page)

        if random.choice([True, False]):
            logging.info(f"Collected {num_questions} questions so far")

    logging.info("Finished collecting SO questions")


# if __name__ == "__main__":
#     crawl()

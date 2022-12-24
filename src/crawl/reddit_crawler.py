# %%
import logging
import os
import random
from typing import List

from dotenv import load_dotenv
from html2text import HTML2Text
from praw import Reddit
from praw.models import Comment, Submission
from pymongo import UpdateOne

from crawl.sample_resources.useful_fields import comment_fields, submission_fields
from utils import AppConfigs, BotType, DataSource, DBClients, get_log_file_path

logging.basicConfig(filename=get_log_file_path(BotType.crawler, DataSource.reddit), level=logging.INFO)

html_handler = HTML2Text()
html_handler.ignore_links = True


# %%
load_dotenv()
# %%
reddit = Reddit(
    client_id=AppConfigs.reddit.client_id,
    client_secret=AppConfigs.reddit.client_secret,
    user_agent=AppConfigs.reddit.user_agent,
)

# %%
def get_comments(submission: Submission) -> List[dict]:
    logging.info("Flattening comments in submission")

    submission.comments.replace_more(limit=0)
    comments: List[Comment] = submission.comments.list()
    comments_result = []
    for comment in comments:
        raw_comment_result = vars(comment)
        if comment.author is None or raw_comment_result.get("author_fullname") is None:
            continue

        each_comment_result = {field: raw_comment_result[field] for field in comment_fields}

        each_comment_result["author"] = each_comment_result["author"].name
        each_comment_result["body"] = html_handler.handle(each_comment_result["body_html"]).strip()
        del each_comment_result["body_html"]

        comments_result.append(each_comment_result)

    return comments_result


# %%
def crawl(subreddit: str = "learnpython") -> None:
    logging.info("Crawler starts!\n\n")
    logging.info("Starting to collect Reddit Submissions")
    client = DBClients.mongo_client()
    logging.info("Obtained mongo client!!")

    bulk_ops = []
    num_submissions = 1
    submission: Submission
    for submission in reddit.subreddit(subreddit).top(time_filter="all"):
        logging.info(f"Processing submission {num_submissions} - {submission.name}")
        raw_submission_result = vars(submission)

        if raw_submission_result.get("author_fullname") is None:
            continue

        submission_result = {field: raw_submission_result[field] for field in submission_fields}

        submission_result["subreddit"] = submission_result["subreddit"].display_name
        submission_result["author"] = submission_result["author"].name
        submission_result["body"] = html_handler.handle(submission_result["selftext_html"] or "").strip()
        del submission_result["selftext_html"]

        submission_result["comments"] = get_comments(submission)

        bulk_ops.append(
            UpdateOne(
                {"_id": submission_result["name"]},
                {"$set": submission_result},
                upsert=True,
            )
        )

        if len(bulk_ops) == 20:
            logging.info("Bulk writing to database")
            client["devstop"]["reddit_submissions"].bulk_write(bulk_ops)
            bulk_ops = []

        if random.choice([True, False]):
            logging.info(f"Collected {num_submissions} submissions so far!!")

        num_submissions += 1

    logging.info("Finished collecting Reddit submissions.")


# %%
# if __name__ == "__main__":
#     crawl()

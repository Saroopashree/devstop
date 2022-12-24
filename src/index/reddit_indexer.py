# %%
import logging
import re

import nltk
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from utils import BotType, DataSource, DBClients, get_log_file_path

load_dotenv()

logging.basicConfig(filename=get_log_file_path(BotType.indexer, DataSource.reddit), level=logging.INFO)

# %%
def remove_non_alphas(text: str) -> str:
    return re.sub(r"[^a-zA-Z]", " ", text).lower()


# %%
def indexer():
    logging.info("Indexer for Reddit starts\n\n")
    nltk.download("stopwords")
    nltk.download("punkt")
    nltk.download("wordnet")
    nltk.download("omw-1.4")

    mongo_client = DBClients.mongo_client()
    logging.info("Obtained mongo client")
    redis_client = DBClients.redis_client()
    logging.info("Obtained redis client")

    wnl = WordNetLemmatizer()
    stpwords = stopwords.words("english")

    reddit_submissions = mongo_client["devstop"]["reddit_submissions"].find()

    for submission in reddit_submissions:
        doc_id = "reddit-" + submission["_id"]
        logging.info(f"Processing {doc_id}")

        text = re.sub(r"`{3}.*?`{3}", "", remove_non_alphas(submission["title"]))
        text += " " + re.sub(r"`{3}.*?`{3}", "", remove_non_alphas(submission["body"]))

        for comment in submission.get("comments") or []:
            text += " " + re.sub(r"`{3}.*?`{3}", "", remove_non_alphas(comment["body"]))

        tokens = word_tokenize(text)
        all_stems = [wnl.lemmatize(tok) for tok in tokens if tok not in stpwords]
        unique_stems = set(all_stems)

        for stem in unique_stems:
            redis_client.sadd(f"devstop:index:{stem}", doc_id)
            redis_client.set(f"devstop:freq:{stem}:{doc_id}", tokens.count(stem))


# %%
if __name__ == "__main__":
    indexer()

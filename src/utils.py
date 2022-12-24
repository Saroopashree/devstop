import os
from enum import Enum

from dotenv import load_dotenv
from pymongo import MongoClient
from redis import Redis

load_dotenv()


class RedditConfigs:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")


class SEConfigs:
    client_id = os.getenv("SE_CLIENT_ID")
    client_secret = os.getenv("SE_CLIENT_SECRET")
    api_key = os.getenv("SE_API_KEY")


class MongoConfigs:
    mongo_uri = os.getenv("MONGO_URI")


class RedisConfigs:
    host = os.getenv("REDIS_HOST") or "localhost"
    port = int(os.getenv("REDIS_PORT") or 6379)
    db = int(os.getenv("REDIS_DB") or 0)


class AppConfigs:
    reddit = RedditConfigs()
    stackex = SEConfigs()
    mongo = MongoConfigs()
    redis = RedisConfigs()


class DBClients:
    @staticmethod
    def mongo_client():
        return MongoClient(AppConfigs.mongo.mongo_uri)

    @staticmethod
    def redis_client():
        return Redis(
            host=AppConfigs.redis.host,
            port=AppConfigs.redis.port,
            db=AppConfigs.redis.db,
        )


def get_url(subreddit: str, submission_id: str) -> str:
    return f"https://www.reddit.com/r/{subreddit}/comments/{submission_id}/"


class DataSource(Enum):
    so = "so"  # StackOverflow
    reddit = "reddit"


class BotType(Enum):
    crawler = "crawler"
    indexer = "indexer"


def get_log_file_path(bot_type: BotType, source: DataSource) -> str:
    return os.path.join(os.getcwd(), "src", "logs", f"{source.name}_{bot_type.name}.log")

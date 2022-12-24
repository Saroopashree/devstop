from utils import DBClients


def flush_index():
    redis_client = DBClients.redis_client()
    redis_client.flushdb()
    print("Flushed all contents in db")

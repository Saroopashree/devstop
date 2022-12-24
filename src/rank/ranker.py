# %%
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from src.utils import DBClients

# %%
wnl = WordNetLemmatizer()


# %%
def gen_search_index_keys(stems: list[str]):
    return [f"devstop:index:{stem}" for stem in stems]


# %%
def index_lookup(stems: list[str]) -> dict[str, list[str]]:
    keys = gen_search_index_keys(stems)
    redis_client = DBClients.redis_client()
    results = redis_client.mget(keys)
    return {key: result for key, result in zip(keys, results) if result}


# %%
def query_processor(query: str):
    tokens = word_tokenize(query)
    all_stems = [wnl.lemmatize(tok) for tok in tokens if tok not in stopwords.words("english")]
    unique_stems = set(all_stems)

    index_lookup(unique_stems)
    return unique_stems

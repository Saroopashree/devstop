import argparse

from crawl.reddit_crawler import crawl as crawl_reddit
from crawl.so_crawler import crawl as crawl_so
from index import flush_index
from index.reddit_indexer import indexer as index_reddit
from index.so_indexer import indexer as index_so


def main():
    parser = argparse.ArgumentParser(description="Crawling and indexing Reddit and Stack Overflow data")
    parser.add_argument(
        "bot_type",
        type=str,
        help="Bot Type: 'crawl' | 'index' | 'flush-index'",
    )
    parser.add_argument("--source", type=str, help="Data Source: 'reddit' | 'so'", default="")

    args = parser.parse_args()
    if args.bot_type == "flush-index":
        flush_index()
    elif args.bot_type == "crawl":
        if args.source == "reddit":
            crawl_reddit("learnpython+howtopython")
        elif args.source == "so":
            crawl_so()
    elif args.bot_type == "index":
        if args.source == "reddit":
            index_reddit()
        elif args.source == "so":
            index_so()


if __name__ == "__main__":
    main()

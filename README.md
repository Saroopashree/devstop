# DevStop

A one stop search engine for searching all dev related questions and discussions.

Developed by considering Reddit submissions and Stack Overflow questions in mind. But the idea can be extended to any other discussion forum.

## How does it work?

1. Crawl Reddit and Stack Overflow for questions and answers.
1. Store the data in MongoDB
1. Index the data using inverted index
1. Store the indices in Redis for easy retrieval
1. Rank the matching documents using TF-IDF cosine similarity for the given query

### Crawling

For crawling reddit submissions, the official PRAW python package is used.

For crawling Stack Overflow questions, the official Stack Exchange API is used.

> Note: Both the crawlers require valid API keys to work. API keys are to be kept in .env file in the root directory. (Check .template.env file for the variable names)

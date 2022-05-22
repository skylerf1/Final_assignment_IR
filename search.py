from elasticsearch import Elasticsearch
import pandas as pd

if __name__ == "__main__":
    es = Elasticsearch(host="localhost", port=9200)

    queries = pd.read_csv('queries_2021.tsv', sep='\t', names=['query_id', 'query_text'])
    curated_results = pd.read_csv('qrels2021.txt', sep=' ', names=['query_id', 'no_idea', 'doc_id', 'relevance'])
    for index, current_row in queries.iterrows():
        current_curated = curated_results[curated_results.query_id == current_row.query_id]
        current_trash = set(current_curated[current_curated.relevance == 0]['doc_id'])
        current_omit = set(current_curated[current_curated.relevance == 1]['doc_id'])
        current_relevant = set(current_curated[current_curated.relevance == 2]['doc_id'])

        bool_query = {
            "size": 10000,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"content": 'anaplastic'}}
                    ],
                    "minimum_should_match": 1,
                    "boost": 1.0
                }
            }
        }

        res = es.search(
            index='clinical',
            body=bool_query
        )

        not_in_result, found_trash, found_omit, found_relevant = 0, 0, 0, 0
        for hit in res['hits']['hits']:
            if hit['_id'] in current_relevant:
                found_relevant += 1
            elif hit['_id'] in current_omit:
                found_omit += 1
            elif hit['_id'] in current_trash:
                found_trash += 1
            else:
                not_in_result += 1

        print('Query %d, %d irrelevant, %d omitted, %d relevant' % (
            index + 1, len(current_trash), len(current_omit), len(current_relevant)), end='\t\t\t')
        print('Found %d irrelevant, %d omitted, %d relevant\t%d new results' % (
            found_trash, found_omit, found_relevant, not_in_result))

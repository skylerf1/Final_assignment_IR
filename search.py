from elasticsearch import Elasticsearch
import pandas as pd
import pytrec_eval
import json

if __name__ == "__main__":
    es = Elasticsearch(host="localhost", port=9200)

    queries = pd.read_csv('queries_2021.tsv', sep='\t', names=['query_id', 'query_text'])
    curated_results = pd.read_csv('qrels2021.txt', sep=' ', names=['query_id', 'no_idea', 'doc_id', 'relevance'])
    qrel_dict = {}
    results_dict = {}

    for index, current_row in curated_results.iterrows():
        query_id = str(current_row['query_id'])
        if query_id not in qrel_dict:
            qrel_dict[query_id] = {}
        qrel_dict[query_id][current_row['doc_id']] = round((current_row['relevance'] + 0.1) / 2)

    for index, current_row in queries.iterrows():
        query_id = str(index + 1)
        if query_id not in results_dict:
            results_dict[query_id] = {}
        current_curated = curated_results[curated_results.query_id == current_row.query_id]
        current_trash = set(current_curated[current_curated.relevance == 0]['doc_id'])
        current_omit = set(current_curated[current_curated.relevance == 1]['doc_id'])
        current_relevant = set(current_curated[current_curated.relevance == 2]['doc_id'])

        bool_query = {
            "size": 10000,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"content": current_row.query_text}}
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
                relevance_level = 1
            elif hit['_id'] in current_omit:
                found_omit += 1
                relevance_level = 1
            elif hit['_id'] in current_trash:
                found_trash += 1
                relevance_level = 0
            else:
                not_in_result += 1
                relevance_level = 0
            results_dict[query_id][hit['_id']] = relevance_level

        print('Query %s, %d - %d - %.2f%% irrelevant matches' % (
            query_id, len(current_trash), found_trash, found_trash/len(current_trash) * 100), end='\t\t')
        print('%d - %d - %.2f%% omitted matches' % (
            len(current_omit), found_omit, found_omit / len(current_omit) * 100), end='\t\t')
        print('%d - %d - %.2f%% relevant matches' % (
            len(current_relevant), found_relevant, found_relevant / len(current_relevant) * 100))

    evaluator = pytrec_eval.RelevanceEvaluator(
        qrel_dict, pytrec_eval.supported_measures)

    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(evaluator.evaluate(results_dict), f, indent=4)
    print('Done :)')
